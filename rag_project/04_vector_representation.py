# -*- coding: utf-8 -*-
"""
الخطوة 4: التمثيل المتجهي (Vector Representation & Embeddings)
--------------------------------------------------------------
مسؤول عن تحويل القطع النصية إلى متجهات أعداد (Embeddings) باستخدام
موديل SentenceTransformer المتعدد اللغات المعتمد في config.py.
"""

from __future__ import annotations

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from config import DATA_FILE_CHUNKS, DATA_FILE_EMBEDDINGS, EMBEDDING_MODEL
from logger import logger
from utils import ensure_directory, read_json_file

_model: SentenceTransformer | None = None


def get_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
    """تحميل نموذج التضمين مرة واحدة فقط وإعادة استخدامه (Singleton Model Loader)."""
    global _model
    if _model is None:
        logger.info("جارٍ تحميل نموذج المتجهات: %s", model_name)
        _model = SentenceTransformer(model_name, device="cpu")
    return _model


def embed_texts(texts: List[str], model_name: str = EMBEDDING_MODEL) -> np.ndarray:
    """إنشاء وتطبيع الـ Embeddings للقطع النصية الممررة."""
    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    model = get_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.asarray(embeddings, dtype=np.float32)


def build_embeddings() -> np.ndarray:
    """قراءة القطع النصية وإنشاء المتجهات وتخزينها في ملف npy."""
    chunks = read_json_file(DATA_FILE_CHUNKS)
    texts = [chunk.get("text", "") for chunk in chunks if chunk.get("text")]
    if not texts:
        raise ValueError("لا توجد نصوص جاهزة لإنشاء الـ Embeddings.")

    embeddings = embed_texts(texts)
    ensure_directory(DATA_FILE_EMBEDDINGS.parent)
    np.save(DATA_FILE_EMBEDDINGS, embeddings)
    logger.info("تم إنشاء وتخزين %s Embedding بنجاح", len(texts))
    return embeddings


if __name__ == "__main__":
    try:
        embeddings = build_embeddings()
        print(f"تم إنشاء {embeddings.shape[0]} Embedding بنجاح.")
    except Exception as exc:
        print(f"خطأ أثناء إنشاء المتجهات: {exc}")
