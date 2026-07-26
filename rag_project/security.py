from __future__ import annotations

import re
from typing import List, Tuple


PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all previous",
    r"system prompt",
    r"reveal the prompt",
    r"show the system prompt",
    r"jailbreak",
    r"act as",
    r"you are now",
    r"bypass",
    r"developer mode",
    r"تجاهل التعليمات السابقة",
    r"تجاهل كل التعليمات",
    r"مفتاح النظام",
    r"اكشف التعليمات",
    r"أظهر تعليمات النظام",
    r"اختراق",
    r"تصرف كأنك",
    r"أنت الآن",
    r"تجاوز",
    r"الوضع المطور",
]


class SecurityError(ValueError):
    """Raised when a user prompt appears unsafe or out of scope."""


def sanitize_user_query(query: str) -> str:
    if not query or not query.strip():
        raise SecurityError("الرسالة فارغة. الرجاء إدخال سؤال صحيح.")

    normalized = re.sub(r"\s+", " ", query.strip())
    lowered = normalized.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            raise SecurityError("تم رفض الطلب لأنّه يحاول تعديل السلوك أو كشف التعليمات الداخلية.")

    if len(normalized) > 4000:
        raise SecurityError("الرسالة طويلة جدًا. الرجاء تقليل طول السؤال.")

    if not re.search(r"[\u0600-\u06FF]", normalized) and not re.search(r"[A-Za-z]", normalized):
        raise SecurityError("الرسالة غير واضحة. الرجاء كتابة سؤال عربي أو إنجليزي صحيح.")

    return normalized


def validate_scope(query: str, context_texts: List[str]) -> Tuple[bool, str]:
    if not context_texts:
        return False, "لم أجد سياقًا مرتبطًا داخل قاعدة المعرفة."

    joined_context = " ".join(context_texts).lower()
    if len(joined_context) < 20:
        return False, "لم أجد سياقًا مرتبطًا داخل قاعدة المعرفة."

    return True, ""
