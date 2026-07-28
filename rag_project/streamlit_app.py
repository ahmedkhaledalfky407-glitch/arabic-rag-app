# -*- coding: utf-8 -*-
"""
واجهة Streamlit احترافية ومحسنة لمساعد RAG العربي.
واجهة مستخدم مخصصة بتصميم داكن RTL مع خط Cairo.
"""

from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from typing import Any

import streamlit as st

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

# ── 1. تهيئة الصفحة ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title="مساعد RAG عربي ذكي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. تنسيقات CSS المخصصة ───────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0b1120;
        --bg-secondary: #111827;
        --bg-card: #1e293b;
        --border: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --accent: #3b82f6;
        --accent-hover: #2563eb;
        --success: #22c55e;
        --warning: #ef4444;
        --purple: #8b5cf6;
        --pink: #ec4899;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Cairo', sans-serif !important;
        background: linear-gradient(135deg, #0b1120 0%, #111827 50%, #0b1120 100%) !important;
        color: var(--text-primary) !important;
    }

    /* تحسين عام للعناصر */
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #111827 50%, #0b1120 100%) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-left: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    /* الأزرار */
    .stButton > button {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 16px !important;
        transition: all 0.25s !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    .stButton > button[kind="secondary"] {
        background: #1e293b !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }

    /* المدخلات */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div > input[type="range"] {
        font-family: 'Cairo', sans-serif !important;
        background: #1e293b !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    /* البطاقات */
    .card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Chat messages */
    .chat-message {
        padding: 16px 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        max-width: 85%;
        line-height: 1.7;
    }

    .chat-user {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-right: auto;
        text-align: right;
    }

    .chat-assistant {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid var(--border);
        margin-left: auto;
        text-align: right;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .badge-error {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* File uploader */
    .stFileUploader {
        background: #1e293b !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 10px;
    }

    [data-testid="stMetric"] > div > div > div > div {
        color: #60a5fa !important;
        font-weight: 800;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# ── 3. استيراد الوحدات ────────────────────────────────────────────────────────


@st.cache_resource
def load_project_module(filename: str, module_name: str) -> Any:
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

# ── 4. إدارة حالة الجلسة ─────────────────────────────────────────────────────

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
if "db_built" not in st.session_state:
    st.session_state.db_built = bool(CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()))
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = get_openrouter_api_key()


# ── 5. الدوال المساعدة ───────────────────────────────────────────────────────

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
    documents = document_module.load_documents_from_directory(DOCUMENTS_DIR)
    if not documents:
        raise ValueError("لم يتم العثور على مستندات نصية صالحة للمعالجة.")
    document_module.save_documents(documents)
    preprocess_module.run_preprocessing()
    chunk_module.run_chunking()
    vector_module.build_embeddings()
    run_store_creation()
    return len(documents)


# ── 6. القائمة الجانبية ──────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<h2 style='text-align:center; margin-bottom:20px;'>⚙️ إعدادات النظام</h2>",
        unsafe_allow_html=True,
    )

    # مفتاح API
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
        st.success("تم تحديث مفتاح API بنجاح!")

    st.divider()

    # رفع الملفات
    st.markdown("### 📁 رفع ملفات TXT جديدة")
    uploaded = st.file_uploader("ارفع ملفات نصية", type=["txt"], accept_multiple_files=True)
    if st.button("💾 حفظ الملفات المرفوعة", use_container_width=True):
        if uploaded:
            DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
            saved = []
            for f in uploaded:
                target = DOCUMENTS_DIR / f.name
                target.write_bytes(f.getvalue())
                saved.append(f.name)
            st.success(f"تم حفظ {len(saved)} ملفًا بنجاح")
        else:
            st.info("اختر ملفًا واحدًا أو أكثر لرفعه")

    # إعادة البناء
    if st.button("🔄 إعادة بناء قاعدة المعرفة", use_container_width=True, type="primary"):
        try:
            with st.spinner("جارٍ معالجة المستندات وتقسيمها وبناء المتجهات..."):
                count = rebuild_knowledge_base()
                st.session_state.db_built = True
            st.success(f"تم البناء بنجاح مع {count} مستند!")
        except Exception as exc:
            st.error(f"فشل في بناء قاعدة المعرفة: {exc}")

    # مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.memory.clear()
        st.session_state.messages.clear()
        st.success("تم مسح المحادثة بنجاح")

    st.divider()

    # الإعدادات
    st.markdown("### ⚙️ الإعدادات")
    top_k = st.slider("عدد النتائج المسترجعة (Top K)", 1, 10, 5)
    sim_threshold = st.slider("حد أدنى للتشابه", 0.0, 1.0, 0.40, 0.05)

    models_list = [
        "openrouter/free",
        "google/gemini-2.5-flash",
        "openai/gpt-4o-mini",
        "meta-llama/llama-3.3-70b-instruct",
        "deepseek/deepseek-chat",
    ]
    if st.session_state.selected_model not in models_list:
        models_list.insert(0, st.session_state.selected_model)

    st.session_state.selected_model = st.selectbox(
        "اختر النموذج",
        models_list,
        index=models_list.index(st.session_state.selected_model)
        if st.session_state.selected_model in models_list
        else 0,
    )
    os.environ["OPENROUTER_MODEL"] = st.session_state.selected_model

    st.divider()

    # الإحصائيات
    st.markdown("### 📊 إحصائيات قاعدة المعرفة")
    dc, cc = get_stats()
    st.metric("المستندات المعالجة", dc)
    st.metric("القطع النصية (Chunks)", cc)

    if st.session_state.db_built:
        st.markdown('<span class="badge badge-success">🟢 قاعدة البيانات جاهزة</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-error">🔴 قاعدة البيانات غير مبنية</span>', unsafe_allow_html=True)


# ── 7. المحتوى الرئيسي ───────────────────────────────────────────────────────

# Header
st.markdown(
    """
    <div style='text-align:center; margin-bottom:32px;'>
        <h1 style='font-size:2.6rem; font-weight:800; margin-bottom:10px;'>
            <span class='gradient-text'>مساعد RAG عربي ذكي</span>
            <span style='font-size:2rem;'>🧠</span>
        </h1>
        <p style='color:#94a3b8; font-size:1.05rem; max-width:600px; margin:0 auto; line-height:1.6;'>
            اسأل سؤالك عن المستندات المخزنة وستحصل على إجابة دقيقة من قاعدة المعرفة مع ذكر المصادر والقطع النصية المسترجعة
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# حالة قاعدة البيانات
if not st.session_state.db_built:
    st.markdown(
        """
        <div class="card" style="border: 1px solid #3b82f6; background: linear-gradient(135deg, rgba(30, 58, 95, 0.7), rgba(30, 41, 59, 0.7));">
            <div style="display:flex; align-items:flex-start; gap:14px;">
                <span style="font-size:1.4rem;">ℹ️</span>
                <div>
                    <strong>قاعدة البيانات فارغة أو لم يتم بناؤها بعد.</strong><br>
                    يرجى رفع ملفات نصية ثم الضغط على «إعادة بناء قاعدة المعرفة» للبدء.
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# عرض المستندات
with st.expander("📁 المستندات النصية المتاحة في قاعدة المعرفة", expanded=False):
    knowledge_files = get_documents_list()
    if knowledge_files:
        for doc_path in knowledge_files:
            try:
                content = read_text_file(doc_path)
                st.markdown(f"**📄 {doc_path.name}**")
                st.code(content[:500] + ("..." if len(content) > 500 else ""), language="text")
            except Exception as exc:
                st.caption(f"تعذر قراءة الملف {doc_path.name}: {exc}")

st.divider()

# ── 8. عرض سجل المحادثة ──────────────────────────────────────────────────────

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

# ── 9. إدخال السؤال ──────────────────────────────────────────────────────────

prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    if not st.session_state.db_built:
        st.error("❌ لا يمكنك طرح الأسئلة قبل بناء قاعدة المعرفة. اضغط على 'إعادة بناء قاعدة المعرفة' في القائمة الجانبية أولاً.")
    elif not active_api_key:
        st.error("❌ يرجى توفير مفتاح OpenRouter API في القائمة الجانبية أولاً.")
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

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response_text,
                            "sources": sources,
                            "meta_info": meta_info,
                        }
                    )

                    logger.info("تمت معالجة السؤال بنجاح في %s ثانية", processing_time)

                except VectorStoreNotFoundError as exc:
                    st.warning(f"⚠️ تنبيه قاعدة البيانات: {exc}")
                except SecurityError as exc:
                    st.error(f"🔒 تنبيه أمني: {exc}")
                except Exception as exc:
                    logger.exception("حدث خطأ أثناء معالجة السؤال")
                    st.error(f"⚠️ حدث خطأ أثناء معالجة السؤال: {exc}")
