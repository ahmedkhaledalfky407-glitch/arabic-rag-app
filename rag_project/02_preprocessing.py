# -*- coding: utf-8 -*-
"""
الخطوة 2: المعالجة الأولية وتنظيف النصوص (Text Preprocessing)
--------------------------------------------------------------
مسؤول عن تنظيف وتطبيع النصوص العربية (إزالة التشكيل الزائد، تجميع السطور،
وإزالة الرموز غير المرغوب فيها) مع الحفاظ على علامات الترقيم والأرقام والمحتوى الرئيسي.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from config import DATA_FILE_DOCUMENTS, DATA_FILE_PREPROCESSED
from logger import logger
from utils import ensure_directory, read_json_file, write_json_file


def normalize_arabic_text(text: str) -> str:
    """تنظيف وتطبيع النص العربي مع الحفاظ على الأرقام وعلامات الترقيم."""
    if not text:
        return ""

    # توحيد الفواصل والسطور ورسائل Unicode المخفية
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u200f", "").replace("\u200e", "").replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("\u00a0", " ")

    # تطبيع الألف والياء والهاء
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = re.sub(r"ة(?=$|[\s\.,;:!؟)\]\}])", "ه", text)

    # إزالة التطويل (التطويل الكشيدة) والتحكم
    text = re.sub(r"[\u0640]+", "", text)
    text = re.sub(r"[\t\u00a0]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[\u0000-\u001f]", "", text)

    lines: List[str] = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"\s+", " ", line).strip()
        if cleaned_line:
            lines.append(cleaned_line)

    unique_lines: List[str] = []
    seen_lines: set[str] = set()
    for line in lines:
        if line not in seen_lines:
            unique_lines.append(line)
            seen_lines.add(line)

    cleaned_text = "\n".join(unique_lines)
    cleaned_text = re.sub(
        r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF0-9A-Za-z\s\.,;:!؟()\[\]{}<>«»/\\-]",
        "",
        cleaned_text,
    )
    return cleaned_text.strip()


def preprocess_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """تنظيف كل مستند وإرجاع قائمة بالنصوص المنظفة."""
    cleaned_documents: List[Dict[str, Any]] = []
    for document in documents:
        cleaned_doc = dict(document)
        cleaned_doc["text"] = normalize_arabic_text(document.get("text", ""))
        cleaned_documents.append(cleaned_doc)
    return cleaned_documents


def run_preprocessing() -> List[Dict[str, Any]]:
    """قراءة المستندات ومعالجتها وتخزين النتيجة."""
    documents = read_json_file(DATA_FILE_DOCUMENTS)
    if not documents:
        raise ValueError("ملف المستندات فارغ أو غير موجود.")
    cleaned_documents = preprocess_documents(documents)
    ensure_directory(DATA_FILE_PREPROCESSED.parent)
    write_json_file(DATA_FILE_PREPROCESSED, cleaned_documents)
    logger.info("تم تنظيف ومعالجة %s مستندًا", len(cleaned_documents))
    return cleaned_documents


if __name__ == "__main__":
    try:
        results = run_preprocessing()
        print(f"تم تنظيف {len(results)} مستندًا بنجاح.")
    except Exception as exc:
        print(f"خطأ أثناء المعالجة: {exc}")
