# -*- coding: utf-8 -*-
"""
واجهة Streamlit احترافية ومحسنة لمساعد RAG العربي.
تتضمن:
1. التخزين المؤقت المتقدم (@st.cache_resource و @st.cache_data) للعمليات الثقيلة.
2. إدارة الحالة المستمرة (st.session_state) لمنع الـ Refresh واختفاء الإجابات.
3. معالجة الأخطاء الشاملة وتمرير التنبيهات بأسلوب أنيق للمستخدم.
4. الربط المباشر مع جميع مكونات المشروع برمجياً بشكل نظيف.
"""

from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from typing import Any, Tuple

import streamlit as st

# ── 1. تهيئة الصفحة والنمط العام ──────────────────────────────────────────

try:
    st.set_page_config(
        page_title="مساعد RAG عربي ذكي",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

from config import (
    CHROMA_DIR,
    DATA_DIR,
    DATA_FILE_CHUNKS,
    DATA_FILE_DOCUMENTS,
    DOCUMENTS_DIR,
    LLM_MODEL,
    MIN_SIMILARITY,
    TOP_K,
    get_openrouter_api_key,
)
from deque_interface import DequeInterface
from logger import logger
from memory import ConversationMemory
from security import SecurityError, sanitize_user_query
from utils import read_json_file, read_text_file

# ── 2. التخزين المؤقت واستيراد الوحدات (Cached Module Loader) ────────────────

@st.cache_resource
def load_project_module(filename: str, module_name: str) -> Any:
    """تحميل واستيراد وحدات المشروع مرة واحدة فقط والتخزين المؤقت لها."""
    here = Path(__file__).resolve().parent
    path = here / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"تعذر العثور على وحدة الملف: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


document_module = load_project_module("01_documents.py", "document_module")
preprocess_module = load_project_module("02_preprocessing.py", "preprocess_module")
chunk_module = load_project_module("03_chunking.py", "chunk_module")
vector_module = load_project_module("04_vector_representation.py", "vector_module")
store_module = load_project_module("05_create_chroma_store.py", "store_module")
retrieve_module = load_project_module("06_retrieve_context.py", "retrieve_module")
prompt_module = load_project_module("07_prompting.py", "prompt_module")

run_store_creation = store_module.run_store_creation
retrieve_context = retrieve_module.retrieve_context
ask = prompt_module.ask
VectorStoreNotFoundError = retrieve_module.VectorStoreNotFoundError

# ── 3. إدارة حالة الجلسة (Session State Initialization) ───────────────────

@st.cache_data(ttl=60)
def check_db_health() -> bool:
    """التحقق من جاهزية وتوفر قاعدة البيانات المعرفية ChromaDB."""
    try:
        if not CHROMA_DIR.exists() or not DATA_FILE_CHUNKS.exists():
            return False
        chunks = read_json_file(DATA_FILE_CHUNKS)
        return len(chunks) > 0
    except Exception:
        return False


if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = os.getenv("OPENROUTER_MODEL", LLM_MODEL)
if "deque" not in st.session_state:
    st.session_state.deque = DequeInterface(maxlen=20)
if "db_built" not in st.session_state:
    st.session_state.db_built = check_db_health()
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = get_openrouter_api_key()

# ── 4. الدوال المساعدة وإعادة البناء ────────────────────────────────────────

def ensure_directories() -> None:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_data(ttl=30)
def get_documents_list() -> list[Path]:
    paths = {p for p in DOCUMENTS_DIR.glob("*.txt")}
    paths.update(p for p in DATA_DIR.glob("*.txt"))
    return sorted(paths)


def get_stats() -> tuple[int, int]:
    doc_count = 0
    chunk_count = 0
    if DATA_FILE_DOCUMENTS.exists():
        try:
            doc_count = len(read_json_file(DATA_FILE_DOCUMENTS))
        except Exception:
            doc_count = 0
    if DATA_FILE_CHUNKS.exists():
        try:
            chunk_count = len(read_json_file(DATA_FILE_CHUNKS))
        except Exception:
            chunk_count = 0
    return doc_count, chunk_count


def rebuild_knowledge_base() -> int:
    ensure_directories()
    documents = document_module.load_documents_from_directory(DOCUMENTS_DIR)
    if not documents:
        raise ValueError("لم يتم العثور على مستندات نصية صالحة للمعالجة.")
    document_module.save_documents(documents, DATA_FILE_DOCUMENTS)
    preprocess_module.run_preprocessing()
    chunk_module.run_chunking()
    vector_module.build_embeddings()
    run_store_creation()
    check_db_health.clear()
    get_documents_list.clear()
    return len(documents)


def save_uploaded_files(files: list[Any]) -> list[str]:
    ensure_directories()
    saved: list[str] = []
    for f in files:
        if f.name.lower().endswith(".txt"):
            target = DOCUMENTS_DIR / f.name
            target.write_bytes(f.getvalue())
            saved.append(f.name)
    get_documents_list.clear()
    return saved

# ── 5. القائمة الجانبية (Sidebar & Controls) ──────────────────────────────

st.sidebar.title("⚙️ إعدادات النظام")

with st.sidebar:
    st.markdown("### 🔑 مفتاح OpenRouter API")
    active_api_key = get_openrouter_api_key(st.session_state.user_api_key)
    input_key = st.text_input(
        "مفتاح API الخاص بك:",
        value=active_api_key,
        type="password",
        help="يمكنك وضع المفتاح هنا أو في ملف .env أو Streamlit Secrets",
    )
    if input_key and input_key.strip() != active_api_key:
        st.session_state.user_api_key = input_key.strip()
        os.environ["OPENROUTER_API_KEY"] = input_key.strip()
        active_api_key = input_key.strip()
        st.success("تم تحديث واعتماد مفتاح API بنجاح!")

    st.divider()
    st.markdown("### 📁 مجلد المستندات والبيانات")
    st.caption(f"يقرأ التطبيق المستندات تلقائياً من المجلد:\n`{DOCUMENTS_DIR}`")

    uploaded = st.file_uploader("رفع ملفات TXT جديدة", type=["txt"], accept_multiple_files=True)
    if st.button("💾 حفظ الملفات المرفوعة"):
        if uploaded:
            try:
                saved = save_uploaded_files(uploaded)
                st.success(f"تم حفظ {len(saved)} ملفًا بنجاح")
            except Exception as exc:
                st.error(f"حدث خطأ أثناء حفظ الملفات: {exc}")
        else:
            st.info("اختر ملفًا واحدًا أو أكثر لرفعه")

    if st.button("🔨 إعادة بناء قاعدة المعرفة"):
        try:
            with st.spinner("جارٍ معالجة المستندات وتقسيمها وبناء المتجهات (ChromaDB)..."):
                count = rebuild_knowledge_base()
                st.session_state.db_built = True
            st.success(f"تم البناء بنجاح مع {count} مستند!")
        except Exception as exc:
            st.error(f"فشل في بناء قاعدة المعرفة: {exc}")
            logger.exception("خطأ في إعادة البناء")

    if st.button("🗑️ مسح المحادثة"):
        st.session_state.memory.clear()
        st.session_state.messages.clear()
        st.success("تم مسح المحادثة بنجاح")

    st.divider()
    st.markdown("### الإعدادات")
    top_k = st.slider("عدد النتائج المسترجعة (Top K)", 1, 10, TOP_K)
    sim_threshold = st.slider("حد أدنى للتشابه", 0.0, 1.0, MIN_SIMILARITY)

    models_list = ["openrouter/free", "google/gemini-2.5-flash", "openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-chat"]
    if st.session_state.selected_model not in models_list:
        models_list.insert(0, st.session_state.selected_model)

    st.session_state.selected_model = st.selectbox(
        "اختر النموذج",
        models_list,
        index=models_list.index(st.session_state.selected_model) if st.session_state.selected_model in models_list else 0,
    )
    os.environ["OPENROUTER_MODEL"] = st.session_state.selected_model

    st.divider()
    st.markdown("### 📊 إحصائيات قاعدة المعرفة")
    dc, cc = get_stats()
    st.metric("المستندات المعالجة", dc)
    st.metric("القطع النصية (Chunks)", cc)

    if st.session_state.db_built:
        st.caption("🟢 قاعدة البيانات جاهزة ومستقرة")
    else:
        st.caption("🔴 قاعدة البيانات غير مبنية بعد")

# ── 6. الواجهة الرئيسية (Main Header) ─────────────────────────────────────

st.markdown(
    "<div dir='rtl' style='text-align:right'>"
    "<h1>📚 مساعد RAG عربي ذكي</h1>"
    "<p>اسأل سؤالك عن المستندات المخزنة وستحصل على إجابة دقيقة من قاعدة المعرفة مع ذكر المصادر والقطع النصية المسترجعة.</p>"
    "</div>",
    unsafe_allow_html=True,
)

if not active_api_key:
    st.warning("⚠️ لم يتم العثور على مفتاح OpenRouter API. يرجى إضافته في Streamlit Secrets أو في القائمة الجانبية.")

if not st.session_state.db_built:
    st.info("ℹ️ قاعدة البيانات فارغة أو لم يتم بناؤها بعد. يرجى رفع ملفات نصية ثم الضغط على **'إعادة بناء قاعدة المعرفة'** للبدء.")

# ── 7. عرض المستندات المتاحة (Knowledge Base Viewer) ──────────────────────

knowledge_files = get_documents_list()
if knowledge_files:
    with st.expander("📁 المستندات النصية المتاحة في قاعدة المعرفة", expanded=False):
        for doc_path in knowledge_files:
            try:
                content = read_text_file(doc_path)
                st.markdown(f"**📄 {doc_path.name}**")
                st.code(content[:500] + ("..." if len(content) > 500 else ""), language="text")
            except Exception as exc:
                st.caption(f"تعذر قراءة الملف {doc_path.name}: {exc}")

st.divider()

# ── 8. عرض سجل المحادثة السابق (Persisted Chat Render) ───────────────────

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.markdown("### 📎 المصادر المسترجعة")
            for src in message["sources"]:
                st.markdown(
                    f"- 📄 `{src.get('filename', '')}` | "
                    f"Chunk: `{src.get('chunk_id', '')}` | "
                    f"التشابه: `{src.get('similarity', 0.0):.2f}`"
                )
        if message.get("meta_info"):
            st.caption(message["meta_info"])

# ── 9. إدخال وتجميع الاستعلام (Chat Input & Engine) ────────────────────────

prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    if not st.session_state.db_built:
        st.error("❌ لا يمكنك طرح الأسئلة قبل بناء قاعدة المعرفة. اضغط على 'إعادة بناء قاعدة المعرفة' في القائمة الجانبية أولاً.")
    elif not active_api_key:
        st.error("❌ يرجى توفير مفتاح OpenRouter API في القائمة الجانبية أو Streamlit Secrets أولاً.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جارٍ البحث في المستندات وتوليد الإجابة..."):
                try:
                    sanitized_query = sanitize_user_query(prompt)
                    start_time = time.time()

                    contexts = retrieve_context(sanitized_query, k=top_k, min_similarity=sim_threshold)

                    memory = st.session_state.memory
                    memory.add_turn("user", sanitized_query)

                    result = ask(sanitized_query, contexts, memory, api_key=active_api_key)
                    response_text = result.get("answer", "تعذر توليد إجابة.")
                    sources = result.get("sources", [])
                    model_used = result.get("model_used", "")
                    memory.add_turn("assistant", response_text)

                    processing_time = round(time.time() - start_time, 3)
                    meta_info = f"⏱ {processing_time} ثانية | العناصر المسترجعة: {len(contexts)}"

                    st.markdown(response_text)
                    if sources:
                        st.markdown("### 📎 المصادر المسترجعة")
                        for src in sources:
                            st.markdown(
                                f"- 📄 `{src.get('filename', '')}` | "
                                f"Chunk: `{src.get('chunk_id', '')}` | "
                                f"التشابه: `{src.get('similarity', 0.0):.2f}`"
                            )
                    st.caption(meta_info)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sources": sources,
                        "meta_info": meta_info,
                    })

                    logger.info("تمت معالجة السؤال بنجاح في %s ثانية", processing_time)

                except VectorStoreNotFoundError as exc:
                    st.warning(f"⚠️ تنبيه قاعدة البيانات: {exc}")
                except SecurityError as exc:
                    st.error(f"🔒 تنبيه أمني: {exc}")
                except Exception as exc:
                    logger.exception("حدث خطأ أثناء معالجة السؤال")
                    st.error(f"⚠️ حدث خطأ أثناء معالجة السؤال: {exc}")