# -*- coding: utf-8 -*-
"""
إعدادات التكوين المتكاملة لمشروع مساعد RAG العربي.
تتضمن مسارات الملفات، معلمات التقسيم، نماذج الذكاء الاصطناعي، وقراءة الأسرار بمرونة.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# المسارات الرئيسية للمشروع
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
LOG_DIR = BASE_DIR / "logs"

# إعدادات المعالجة والاسترجاع
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 5
MIN_SIMILARITY = 0.40

# نماذج الذكاء الاصطناعي (تم اعتماد النموذج المجاني الافتراضي لـ OpenRouter)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
TEMPERATURE = 0.2
MAX_TOKENS = 800
MAX_MEMORY_MESSAGES = 10
COLLECTION_NAME = "arabic_rag_documents"

# إعدادات OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ملفات البيانات الوسيطة
DATA_FILE_DOCUMENTS = DATA_DIR / "01_documents.json"
DATA_FILE_PREPROCESSED = DATA_DIR / "02_preprocessed.json"
DATA_FILE_CHUNKS = DATA_DIR / "03_chunks.json"
DATA_FILE_EMBEDDINGS = DATA_DIR / "04_embeddings.npy"

# إنشاء المجلدات الأساسية إن لم تكن موجودة
for directory in (DOCUMENTS_DIR, DATA_DIR, CHROMA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def get_openrouter_api_key(override_key: str | None = None) -> str:
    """
    قراءة مفتاح OpenRouter API بمرونة وتأمين:
    1. المفتاح الممرر مباشرة (Override Key)
    2. المفتاح المسجل في Streamlit Secrets (إن وجد)
    3. متغير البيئة OPENROUTER_API_KEY
    """
    if override_key and override_key.strip():
        return override_key.strip()

    try:
        import streamlit as st
        if "OPENROUTER_API_KEY" in st.secrets and st.secrets["OPENROUTER_API_KEY"]:
            key = str(st.secrets["OPENROUTER_API_KEY"]).strip()
            os.environ["OPENROUTER_API_KEY"] = key
            return key
    except Exception:
        pass

    env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    return env_key
