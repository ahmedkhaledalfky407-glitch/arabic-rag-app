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
        --bg-primary: #0b1120;
        --bg-secondary: #111827;
        --bg-card: #1e293b;
        --bg-card-hover: #273549;
        --border: #334155;
        --border-light: #475569;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent: #3b82f6;
        --accent-hover: #2563eb;
        --accent-glow: rgba(59, 130, 246, 0.25);
        --purple: #8b5cf6;
        --pink: #ec4899;
        --success: #22c55e;
        --warning: #ef4444;
        --warning-bg: rgba(239, 68, 68, 0.12);
        --info-bg: rgba(59, 130, 246, 0.12);
        --radius: 12px;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    * {
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box !important;
    }

    html, body {
        font-family: 'Cairo', sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        min-height: 100vh !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stApp {
        background: var(--bg-primary) !important;
        direction: rtl !important;
    }

    .stMain {
        background: transparent !important;
    }

    .block-container {
        direction: rtl !important;
        text-align: right !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }

    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    p, span, div, label, input, select, button {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        border-radius: var(--radius) !important;
        border: none !important;
        padding: 12px 16px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
        direction: rtl !important;
        text-align: center !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #7c3aed) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }

    .stButton > button[kind="secondary"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-light) !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div > input[type="range"] {
        font-family: 'Cairo', sans-serif !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        padding: 10px 14px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* File uploader */
    .stFileUploader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 10px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stFileUploader > div {
        color: var(--text-secondary) !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 16px 10px !important;
        text-align: center !important;
        direction: rtl !important;
    }

    [data-testid="stMetric"] > div > div > div > div {
        color: #60a5fa !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
    }

    [data-testid="stMetric"] > div > div > div > label {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }

    /* Chat messages */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stChatMessage > div {
        background: transparent !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stChatMessageContent {
        background: transparent !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Status badges */
    .status-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-bottom: 12px !important;
        direction: rtl !important;
    }

    .status-ready {
        background: rgba(34, 197, 94, 0.15) !important;
        color: #4ade80 !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
    }

    .status-not-ready {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }

    /* Control panel */
    .control-panel {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 18px !important;
        margin-bottom: 20px !important;
        backdrop-filter: blur(10px) !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .control-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
        gap: 12px !important;
        direction: rtl !important;
    }

    /* Chat area */
    .chat-wrapper {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        min-height: 400px !important;
        max-height: 600px !important;
        overflow-y: auto !important;
        margin-bottom: 20px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* Message bubbles */
    .message-user {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: white !important;
        padding: 14px 18px !important;
        border-radius: 18px 18px 4px 18px !important;
        margin-bottom: 12px !important;
        max-width: 75% !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25) !important;
        line-height: 1.6 !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .message-assistant {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        padding: 14px 18px !important;
        border-radius: 18px 18px 18px 4px !important;
        margin-bottom: 12px !important;
        max-width: 75% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        line-height: 1.6 !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .message-meta {
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        margin-top: 6px !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        direction: rtl !important;
    }

    /* Input area */
    .input-wrapper {
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .chat-input {
        width: 100% !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 16px 60px 16px 20px !important;
        color: var(--text-primary) !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 1rem !important;
        outline: none !important;
        transition: all 0.25s !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .chat-input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 4px var(--accent-glow) !important;
    }

    .chat-input::placeholder {
        color: var(--text-muted) !important;
    }

    .send-button {
        position: absolute !important;
        left: 10px !important;
        width: 42px !important;
        height: 42px !important;
        background: linear-gradient(135deg, #3b82f6, #7c3aed) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1.1rem !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.25s !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    .send-button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.45) !important;
    }

    .send-button:active {
        transform: scale(0.96) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px !important;
        height: 6px !important;
    }

    ::-webkit-scrollbar-track {
        background: transparent !important;
    }

    ::-webkit-scrollbar-thumb {
        background: #334155 !important;
        border-radius: 10px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #475569 !important;
    }

    /* Card styling */
    .custom-card {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        backdrop-filter: blur(10px) !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800 !important;
        direction: rtl !important;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .control-grid {
            grid-template-columns: 1fr !important;
        }
        
        .chat-wrapper {
            min-height: 300px !important;
            max-height: 400px !important;
        }
        
        .message-user,
        .message-assistant {
            max-width: 90% !important;
        }
        
        .stButton > button {
            font-size: 0.9rem !important;
            padding: 10px 12px !important;
        }
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
    base_dir = Path(__file__).resolve().parent
    st.session_state.db_built = bool((base_dir / "chroma_db").exists() and any((base_dir / "chroma_db").iterdir()))
if "user_api_key" not in st.session_state:
    try:
        from config import get_openrouter_api_key
        st.session_state.user_api_key = get_openrouter_api_key()
    except Exception:
        st.session_state.user_api_key = ""

# ── 5. الدوال المساعدة ───────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_documents_list() -> list[Path]:
    base_dir = Path(__file__).resolve().parent
    documents_dir = base_dir / "documents"
    data_dir = base_dir / "data"
    paths = {p for p in documents_dir.glob("*.txt")}
    paths.update(p for p in data_dir.glob("*.txt"))
    return sorted(paths)


def get_stats() -> tuple[int, int]:
    doc_count = 0
    chunk_count = 0
    base_dir = Path(__file__).resolve().parent
    data_file_documents = base_dir / "data" / "01_documents.json"
    data_file_chunks = base_dir / "data" / "03_chunks.json"
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
    base_dir = Path(__file__).resolve().parent
    documents_dir = base_dir / "documents"
    documents = document_module.load_documents_from_directory(documents_dir)
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
    <div style="text-align:center; margin-bottom:28px; direction:rtl;">
        <h1 style="font-size:2.4rem; font-weight:800; margin-bottom:10px; direction:rtl; text-align:center;">
            <span class="gradient-text">مساعد RAG عربي ذكي</span>
            <span style="font-size:2rem;">🧠</span>
        </h1>
        <p style="color:#94a3b8; font-size:1.05rem; max-width:600px; margin:0 auto; line-height:1.6; direction:rtl; text-align:center;">
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
        <div class="custom-card" style="border: 1px solid #3b82f6; background: linear-gradient(135deg, rgba(30, 58, 95, 0.7), rgba(30, 41, 59, 0.7)); direction:rtl; text-align:right;">
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

chat_container = st.container()
with chat_container:
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
    if not st.session_state.user_api_key:
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

# ── 9. لوحة التحكم ────────────────────────────────────────────────────────────

st.divider()

with st.container():
    st.markdown(
        """
        <div class="control-panel">
            <div class="control-grid">
                <div>
                    <label style="display:block; font-size:0.85rem; color:#94a3b8; margin-bottom:8px; direction:rtl; text-align:right;">
                        🔑 مفتاح OpenRouter API
                    </label>
                </div>
                <div>
                    <label style="display:block; font-size:0.85rem; color:#94a3b8; margin-bottom:8px; direction:rtl; text-align:right;">
                        📁 رفع ملفات TXT
                    </label>
                </div>
                <div>
                    <label style="display:block; font-size:0.85rem; color:#94a3b8; margin-bottom:8px; direction:rtl; text-align:right;">
                        ⚙️ الإعدادات
                    </label>
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        active_api_key = st.session_state.user_api_key or ""
        input_key = st.text_input(
            "🔑 مفتاح API",
            value=active_api_key,
            type="password",
            label_visibility="collapsed",
        )
        if input_key and input_key.strip() != active_api_key:
            st.session_state.user_api_key = input_key.strip()
            os.environ["OPENROUTER_API_KEY"] = input_key.strip()
            st.success("✅ تم تحديث مفتاح API")

    with col2:
        uploaded = st.file_uploader(
            "📁 رفع ملفات TXT",
            type=["txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if st.button("💾 حفظ الملفات", use_container_width=True, key="save_files"):
            if uploaded:
                base_dir = Path(__file__).resolve().parent
                documents_dir = base_dir / "documents"
                documents_dir.mkdir(parents=True, exist_ok=True)
                saved = []
                for f in uploaded:
                    target = documents_dir / f.name
                    target.write_bytes(f.getvalue())
                    saved.append(f.name)
                st.success(f"✅ تم حفظ {len(saved)} ملفًا")
            else:
                st.info("📌 اختر ملفًا لرفعه")

    with col3:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 إعادة بناء", use_container_width=True, type="primary", key="rebuild"):
                try:
                    with st.spinner("جارٍ البناء..."):
                        count = rebuild_knowledge_base()
                        st.session_state.db_built = True
                    st.success(f"✅ تم البناء: {count} مستند")
                except Exception as exc:
                    st.error(f"❌ فشل البناء: {exc}")
        with c2:
            if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear_chat"):
                st.session_state.memory = None
                st.session_state.messages.clear()
                st.success("✅ تم مسح المحادثة")
        with c3:
            st.session_state.selected_model = st.selectbox(
                "اختر النموذج",
                ["openrouter/free", "openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-chat", "google/gemini-2.5-flash"],
                index=0,
                label_visibility="collapsed",
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
    st.markdown('<span class="status-badge status-ready">🟢 قاعدة البيانات جاهزة</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="status-badge status-not-ready">🔴 قاعدة البيانات غير مبنية</span>', unsafe_allow_html=True)
