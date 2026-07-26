# -*- coding: utf-8 -*-
"""
الخطوة 1: قراءة وتحميل المستندات (Document Ingestion)
-----------------------------------------------------
مسؤول عن قراءة جميع الملفات النصية (TXT) من مجلد المستندات،
التحقق من عدم تكرارها، وتجهيز البيانات مع الـ Metadata الأساسية.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List

from config import DATA_DIR, DATA_FILE_DOCUMENTS, DOCUMENTS_DIR
from logger import logger
from utils import ensure_directory, iter_txt_files, read_text_file, write_json_file


def load_documents_from_directory(directory: str | os.PathLike[str] | None = None) -> List[Dict[str, Any]]:
    """
    تحميل جميع ملفات TXT من المجلد المحدد ومجلد البيانات،
    مع حساب Hash لمنع الملفات المكررة أو الفارغة.
    """
    target_dir = Path(directory or DOCUMENTS_DIR)
    search_dirs = [target_dir]
    if target_dir != DATA_DIR:
        search_dirs.append(DATA_DIR)

    documents: List[Dict[str, Any]] = []
    seen_hashes: set[str] = set()

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for file_path in iter_txt_files(search_dir):
            try:
                text = read_text_file(file_path)
            except Exception as exc:
                logger.error("فشل في قراءة الملف %s: %s", file_path.name, exc)
                continue

            if not text or not text.strip():
                logger.warning("تجاوز ملف فارغ: %s", file_path.name)
                continue

            file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if file_hash in seen_hashes:
                logger.info("تجاوز محتوى مكرر للملف: %s", file_path.name)
                continue
            seen_hashes.add(file_hash)

            documents.append(
                {
                    "id": file_path.stem.replace(" ", "_") or file_path.name,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "text": text,
                    "size_chars": len(text),
                }
            )

    if not documents:
        raise ValueError("لم يتم العثور على أي مستندات نصية صالحة داخل المجلد.")

    return documents


def save_documents(documents: List[Dict[str, Any]], path: str | os.PathLike[str] | None = None) -> None:
    """حفظ المستندات كملف JSON وسيظ وسيط."""
    output_path = Path(path or DATA_FILE_DOCUMENTS)
    ensure_directory(output_path.parent)
    write_json_file(output_path, documents)
    logger.info("تم حفظ %s مستندًا في %s", len(documents), output_path)


if __name__ == "__main__":
    try:
        documents = load_documents_from_directory()
        save_documents(documents)
        print(f"تم تحميل وحفظ {len(documents)} مستندًا بنجاح.")
    except Exception as exc:
        print(f"حدث خطأ: {exc}")
