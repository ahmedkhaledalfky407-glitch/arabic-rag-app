# -*- coding: utf-8 -*-
"""
واجهة Streamlit احترافية - تصميم داكن RTL مع خط Cairo.
"""

from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from typing import Any

import streamlit as st

# ── 1. تهيئة الصفحة ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title="مساعد RAG عربي ذكي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. تنسيقات CSS المخصصة ───────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #070b14;
        --bg-secondary: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #273549;
        --border: #334155;
        --border-light: #475569;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent: #3b82f6;
        --accent-glow: rgba(59, 130, 246, 0.25);
        --success: #22c55e;
        --warning: #ef4444;
        --warning-bg: rgba(239, 68, 68, 0.12);
        --info-bg: rgba(59, 130, 246, 0.12);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Cairo', sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background: var(--bg-primary) !important;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }

    .stButton > button {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 16px !important;
        transition: all 0.25s !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #7c3aed) !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    .stButton > button[kind="secondary"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div > input[type="range"] {
        font-family: 'Cairo', sans-serif !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

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

    .stFileUploader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }

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

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

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
    }

    .chat-assistant {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid var(--border);
    }
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
    st.session_state.memory = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
if "db_built" not in st.session_state:
    st.session_state.db_built = bool(
        Path("chroma_db").exists() and any(Path("chroma_db").iterdir())
    )
if "user_api_key" not in st.session_state:
    try:
        from config import get_openrouter_api_key
        st.session_state.user_api_key = get_openrouter_api_key()
    except Exception:
        st.session_state.user_api_key = ""

# ── 5. الدوال المساعدة ───────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_documents_list() -> list[Path]:
    documents_dir = Path("documents")
    data_dir = Path("data")
    paths = {p for p in documents_dir.glob("*.txt")}
    paths.update(p for p in data_dir.glob("*.txt"))
    return sorted(paths)


def get_stats() -> tuple[int, int]:
    doc_count = 0
    chunk_count = 0
    data_file_documents = Path("data") / "01_documents.json"
    data_file_chunks = Path("data") / "03_chunks.json"
    if data_file_documents.exists():
        try:
            import json
            doc_count = len(json.loads(data_file_documents.read_text(encoding="utf-8")))
        except Exception:
            doc_count = 0
    if data_file_chunks.exists():
        try:
            import json
            chunk_count = len(json.loads(data_file_chunks.read_text(encoding="utf-8")))
        except Exception:
            chunk_count = 0
    return doc_count, chunk_count


def rebuild_knowledge_base() -> int:
    documents = document_module.load_documents_from_directory(Path("documents"))
    if not documents:
        raise ValueError("لم يتم العثور على مستندات نصية صالحة للمعالجة.")
    document_module.save_documents(documents)
    preprocess_module.run_preprocessing()
    chunk_module.run_chunking()
    vector_module.build_embeddings()
    run_store_creation()
    return len(documents)


# ── 6. واجهة المستخدم ────────────────────────────────────────────────────────

# Header
st.markdown(
    """
    <div style="text-align:center; margin-bottom:28px;">
        <h1 style="font-size:2.4rem; font-weight:800; margin-bottom:10px;">
            <span class="gradient-text">مساعد RAG عربي ذكي</span>
            <span style="font-size:2rem;">🧠</span>
        </h1>
        <p style="color:#94a3b8; font-size:1.05rem; max-width:600px; margin:0 auto; line-height:1.6;">
            اسأل سؤالك عن المستندات المخزنة وستحصل على إجابة دقيقة من قاعدة المعرفة مع ذكر المصادر
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
                    يرجى الضغط على «إعادة بناء قاعدة المعرفة» للبدء.
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# عرض المستندات
with st.expander("📁 المستندات النصية المتاحة", expanded=False):
    knowledge_files = get_documents_list()
    if knowledge_files:
        for doc_path in knowledge_files:
            try:
                content = doc_path.read_text(encoding="utf-8")
                st.markdown(f"**📄 {doc_path.name}**")
                st.code(content[:500] + ("..." if len(content) > 500 else ""), language="text")
            except Exception as exc:
                st.caption(f"تعذر قراءة الملف {doc_path.name}: {exc}")

st.divider()

# ── 7. سجل المحادثة ──────────────────────────────────────────────────────────

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

# ── 8. إدخال السؤال ──────────────────────────────────────────────────────────

prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    if not st.session_state.db_built:
        st.error("❌ لا يمكنك طرح الأسئلة قبل بناء قاعدة المعرفة. اضغط على 'إعادة بناء قاعدة المعرفة' أولاً.")
    elif not st.session_state.user_api_key:
        st.error("❌ يرجى توفير مفتاح OpenRouter API أولاً.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("جارٍ البحث في المستندات وتوليد الإجابة..."):
                try:
                    from memory import ConversationMemory
                    from security import sanitize_user_query

                    sanitized_query = sanitize_user_query(prompt)
                    start_time = time.time()

                    contexts = retrieve_context(sanitized_query, k=5, min_similarity=0.40)

                    memory = st.session_state.memory
                    if memory is None:
                        memory = ConversationMemory()
                        st.session_state.memory = memory
                    memory.add_turn("user", sanitized_query)

                    result = ask(
                        sanitized_query,
                        contexts,
                        memory,
                        api_key=st.session_state.user_api_key,
                    )
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

                except VectorStoreNotFoundError as exc:
                    st.warning(f"⚠️ تنبيه قاعدة البيانات: {exc}")
                except Exception as exc:
                    st.error(f"⚠️ حدث خطأ أثناء معالجة السؤال: {exc}")

# ── 9. شريط التحكم السفلي ────────────────────────────────────────────────────

st.divider()

with st.container():
    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        active_api_key = st.session_state.user_api_key or ""
        input_key = st.text_input(
            "🔑 مفتاح OpenRouter API",
            value=active_api_key,
            type="password",
            label_visibility="visible",
        )
        if input_key and input_key.strip() != active_api_key:
            st.session_state.user_api_key = input_key.strip()
            os.environ["OPENROUTER_API_KEY"] = input_key.strip()
            st.success("تم تحديث مفتاح API")

    with col2:
        uploaded = st.file_uploader("📁 رفع ملفات TXT", type=["txt"], accept_multiple_files=True, label_visibility="visible")
        if st.button("💾 حفظ", use_container_width=True):
            if uploaded:
                Path("documents").mkdir(parents=True, exist_ok=True)
                saved = []
                for f in uploaded:
                    target = Path("documents") / f.name
                    target.write_bytes(f.getvalue())
                    saved.append(f.name)
                st.success(f"تم حفظ {len(saved)} ملفًا")
            else:
                st.info("اختر ملفًا لرفعه")

    with col3:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 إعادة بناء", use_container_width=True, type="primary"):
                try:
                    with st.spinner("جارٍ البناء..."):
                        count = rebuild_knowledge_base()
                        st.session_state.db_built = True
                    st.success(f"تم البناء: {count} مستند")
                except Exception as exc:
                    st.error(f"فشل البناء: {exc}")
        with c2:
            if st.button("🗑️ مسح المحادثة", use_container_width=True):
                st.session_state.memory = None
                st.session_state.messages.clear()
                st.success("تم مسح المحادثة")
        with c3:
            st.session_state.selected_model = st.selectbox(
                "اختر النموذج",
                ["openrouter/free", "openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-chat", "google/gemini-2.5-flash"],
                index=0,
                label_visibility="visible",
            )
            os.environ["OPENROUTER_MODEL"] = st.session_state.selected_model

# ── 10. الإحصائيات ───────────────────────────────────────────────────────────

st.divider()
dc, cc = get_stats()
col1, col2 = st.columns(2)
with col1:
    st.metric("📊 المستندات المعالجة", dc)
with col2:
    st.metric("📊 القطع النصية (Chunks)", cc)

if st.session_state.db_built:
    st.markdown('<span style="background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.3); padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight:600;">🟢 قاعدة البيانات جاهزة</span>', unsafe_allow_html=True)
else:
    st.markdown('<span style="background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.3); padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight:600;">🔴 قاعدة البيانات غير مبنية</span>', unsafe_allow_html=True)
