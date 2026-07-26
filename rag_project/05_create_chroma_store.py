# -*- coding: utf-8 -*-
"""
الخطوة 5: إنشاء وتخزين قاعدة البيانات المتجهة (Chroma Vector Store)
------------------------------------------------------------------
مسؤول عن إنشاء ChromaDB collection وحفظ القطع النصية والمتجهات والبيانات الوصفية
على القرص الصلب في مجلد chroma_db لاستخدامها المباشر والسريع لاحقاً.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_DIR, COLLECTION_NAME, DATA_FILE_CHUNKS, EMBEDDING_MODEL
from logger import logger
from utils import read_json_file


def get_embedding_function() -> Any:
    """إرجاع دالة التضمين الخاصة بـ Chroma المعتمدة على SentenceTransformer."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)


def get_or_create_collection() -> Tuple[Any, Any]:
    """الاتصال بـ ChromaDB وإنشاء أو جلب المجموعة المستهدفة (Collection)."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
    return client, collection


def build_store(chunks: List[Dict[str, Any]]) -> Any:
    """إنشاء أو إعادة بناء التخزين المتجهي وإضافة القطع النصية والـ Metadata."""
    if not chunks:
        raise ValueError("قائمة القطع النصية فارغة، تعذر بناء قاعدة البيانات.")

    _, collection = get_or_create_collection()

    # مسح البيانات السابقة لمنع التكرار عند إعادة البناء
    try:
        existing_info = collection.get()
        existing_ids = existing_info.get("ids", [])
        if existing_ids:
            collection.delete(ids=existing_ids)
    except Exception as exc:
        logger.warning("تنبيه أثناء تفريغ البيانات القديمة من ChromaDB: %s", exc)

    ids = [chunk.get("chunk_id", str(index)) for index, chunk in enumerate(chunks)]
    documents = [chunk.get("text", "") for chunk in chunks]
    metadatas = [
        {
            "filename": chunk.get("filename", "unknown.txt"),
            "chunk_id": chunk.get("chunk_id", ""),
            "source": chunk.get("source", ""),
            "article_label": chunk.get("article_label", chunk.get("filename", "")),
        }
        for chunk in chunks
    ]

    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    logger.info("تم إدخال وتخزين %s عنصرًا بنجاح في ChromaDB", collection.count())
    return collection


def run_store_creation() -> Any:
    """قراءة القطع النصية وبناء متجر المتجهات."""
    chunks = read_json_file(DATA_FILE_CHUNKS)
    return build_store(chunks)


if __name__ == "__main__":
    try:
        collection = run_store_creation()
        print(f"تم بناء مخزن المتجهات بنجاح، إجمالي العناصر: {collection.count()}")
    except Exception as exc:
        print(f"خطأ أثناء بناء ChromaDB: {exc}")
