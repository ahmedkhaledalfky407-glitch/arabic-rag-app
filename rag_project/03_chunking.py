# -*- coding: utf-8 -*-
"""
الخطوة 3: تقسيم النصوص إلى قطع (Text Chunking)
-----------------------------------------------
مسؤول عن تقسيم المستندات النصية المعالجة إلى قطع صغيرة متداخلة (Chunks)،
مع إرفاق البيانات الوصفية لكل قطعة (اسم الملف، رقم القطعة، وموقعها).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_FILE_CHUNKS, DATA_FILE_PREPROCESSED
from logger import logger
from utils import ensure_directory, read_json_file, write_json_file


def recursive_split_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[Tuple[int, int, str]]:
    """تقسيم النص إلى قطع متداخلة بناءً على الحجم المحدد وتداخل الكلمات."""
    if not text or not text.strip():
        return []

    chunks: List[Tuple[int, int, str]] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        segment = text[start:end].strip()
        if segment:
            chunks.append((start, end, segment))
        if end >= text_len:
            break
        start = max(0, end - overlap)

    return chunks


def build_chunks(
    documents: List[Dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """إنشاء وتجميع كافة القطع النصية من قائمة المستندات المعالجة."""
    chunks: List[Dict[str, Any]] = []

    for document in documents:
        text = str(document.get("text", "")).strip()
        if not text:
            continue

        doc_id = document.get("id", "doc")
        filename = document.get("filename", "unknown.txt")
        source = str(document.get("path", ""))

        split_segments = recursive_split_text(text, chunk_size=chunk_size, overlap=overlap)
        for index, (start_char, end_char, chunk_text) in enumerate(split_segments, start=1):
            chunks.append(
                {
                    "chunk_id": f"{doc_id}_chunk_{index:03d}",
                    "filename": filename,
                    "source": source,
                    "start_char": start_char,
                    "end_char": end_char,
                    "text": chunk_text,
                }
            )

    return chunks


def run_chunking() -> List[Dict[str, Any]]:
    """قراءة المستندات المعالجة وتقسيمها وتخزين النتيجة في ملف JSON."""
    documents = read_json_file(DATA_FILE_PREPROCESSED)
    if not documents:
        raise ValueError("ملف المستندات المعالجة فارغ أو غير موجود.")
    chunks = build_chunks(documents)
    ensure_directory(DATA_FILE_CHUNKS.parent)
    write_json_file(DATA_FILE_CHUNKS, chunks)
    logger.info("تم إنشاء %s قطعة نصية (Chunk)", len(chunks))
    return chunks


if __name__ == "__main__":
    try:
        chunks = run_chunking()
        print(f"تم إنشاء {len(chunks)} قطعة نصية بنجاح.")
    except Exception as exc:
        print(f"خطأ أثناء التقسيم: {exc}")
