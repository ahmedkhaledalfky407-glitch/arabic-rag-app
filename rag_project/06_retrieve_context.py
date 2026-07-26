# -*- coding: utf-8 -*-
"""
الخطوة 6: استرجاع السياق والمستندات المشابهة (Vector Context Retrieval)
--------------------------------------------------------------------
مسؤول عن استقبال استعلام المستخدم، تطهيره أمنياً، البحث في ChromaDB
واسترجاع أعلى K قطع نصية مشابهة حساسية وتصفيتها وفق حد التشابه الأدنى.
"""

from __future__ import annotations

from typing import Any, Dict, List

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, MIN_SIMILARITY, TOP_K
from logger import logger
from security import sanitize_user_query, validate_scope


class VectorStoreNotFoundError(FileNotFoundError):
    """استثناء خاص يرفع عند محاولة البحث وقاعدة البيانات غير مبنية بعد."""
    pass


def get_embedding_function() -> Any:
    """إرجاع دالة التضمين المستخدمة للبحث."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)


def get_collection() -> Any:
    """الوصول إلى المجموعة (Collection) في ChromaDB بعد الفحص."""
    if not CHROMA_DIR.exists():
        raise VectorStoreNotFoundError("لم يتم بناء قاعدة المتجهات بعد. يرجى معالجة المستندات وبنائها أولاً.")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        return client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
        )
    except Exception as exc:
        raise VectorStoreNotFoundError(f"تعذر الوصول إلى مجموعة البيانات في ChromaDB: {exc}") from exc


def retrieve_context(query: str, k: int = TOP_K, min_similarity: float = MIN_SIMILARITY) -> List[Dict[str, Any]]:
    """استرجاع أعلى K قطع نصية متطابقة مع سؤال المستخدم بناءً على التشابه."""
    safe_query = sanitize_user_query(query)
    collection = get_collection()

    count = collection.count()
    if count == 0:
        logger.warning("قاعدة البيانات المتجهة فارغة.")
        return []

    results = collection.query(query_texts=[safe_query], n_results=min(max(k, 1), count))

    contexts: List[Dict[str, Any]] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for text, meta, distance in zip(docs, metas, distances):
        similarity = 1.0 - float(distance)
        if similarity < min_similarity:
            continue
        contexts.append(
            {
                "text": text,
                "filename": meta.get("filename", ""),
                "chunk_id": meta.get("chunk_id", ""),
                "article_label": meta.get("article_label", ""),
                "source": meta.get("source", ""),
                "distance": distance,
                "similarity": similarity,
            }
        )

    allowed, reason = validate_scope(safe_query, [item["text"] for item in contexts])
    if not allowed:
        logger.warning("تنبيه النطاق الأمني: %s", reason)
        return []

    return contexts[:k]


if __name__ == "__main__":
    try:
        results = retrieve_context("ما هي شروط العمل؟", k=3)
        for item in results:
            print(item["article_label"], "| similarity:", round(item["similarity"], 3))
    except VectorStoreNotFoundError as exc:
        print(f"تنبيه: {exc}")
