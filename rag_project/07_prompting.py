# -*- coding: utf-8 -*-
"""
الخطوة 7: توجيه واستدعاء نماذج الذكاء الاصطناعي (Prompting & LLM Generation)
--------------------------------------------------------------------------
توفير التفاعل الحواري والذكاء الاستجابي مع دعم نماذج OpenRouter المجانية
(openrouter/free) والمناقشة التفاعلية مع المستخدم في حال عدم وضوح السؤال.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import requests

from config import LLM_MODEL, MAX_TOKENS, OPENROUTER_URL, TEMPERATURE, get_openrouter_api_key
from logger import logger
from memory import ConversationMemory
from security import sanitize_user_query

# قائمة النماذج المجانية الاحتياطية على OpenRouter لضمان الاستجابة دائماً
FREE_MODEL_FALLBACKS = [
    "openrouter/free",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemini-2.5-flash",
]


def build_system_prompt() -> str:
    """بناء التعليمات التفاعلية والنظامية لـ LLM (System Prompt)."""
    return (
        "أنت مساعد عربي ذكي وتفاعلي، تعتمد على سياق المستندات المرفقة لمساعدة المستخدم.\n"
        "1. إذا كانت المعلومة موجودة في السياق المرفق، أجب عنها بوضوح واذكر اسم المصدر في نهاية الإجابة.\n"
        "2. إذا كان سؤال المستخدم غير واضح أو محتمل لأكثر من معنى، ناقش المستخدم بلباقة وطرح عليه أسئلة توضيحية لفهامه بشكل أفضل ومساعدته على تحديد مطلبه.\n"
        "3. إذا لم تجد معلومة صريحة في السياق، لا تنهِ الحوار فوراً؛ بل وضح ما هو متوفر في المستندات وناقش المستخدم بحفاوة.\n"
        "4. حافظ دائماً على لغة عربية سليمة وودودة وتفاعلية."
    )


def build_prompt(query: str, contexts: List[Dict[str, Any]], memory: ConversationMemory) -> str:
    """دمج القطع النصية المسترجعة وذاكرة المحادثة في المحث الموجه."""
    if contexts:
        context_block = "\n\n".join(
            f"المصدر: {item.get('filename', '')} | Chunk: {item.get('chunk_id', '')}\n{item.get('text', '')}"
            for item in contexts
        )
    else:
        context_block = "لا توجد قطع نصية متطابقة بشكل مباشر في قاعدة المعرفة لهذا السؤال."

    memory_block = memory.to_prompt_block()
    return (
        f"السياق المتاح:\n{context_block}\n\n{memory_block}\n\n"
        f"سؤال المستخدم: {query}\n\n"
        "اكتب إجابة عربية تفاعلية ومفيدة. إذا كانت الإجابة تعتمد على السياق اذكر المصادر، وإن كان السؤال بحاجة لتوضيح ناقش المستخدم."
    )


def ask(query: str, contexts: List[Dict[str, Any]], memory: ConversationMemory, api_key: str | None = None) -> Dict[str, Any]:
    """إرسال السؤال والمحث إلى OpenRouter مع دعم النماذج المجانية والاستجابة التفاعلية."""
    sanitized_query = sanitize_user_query(query)
    active_key = get_openrouter_api_key(api_key)

    if not active_key:
        raise RuntimeError("مفتاح OpenRouter غير متوفر. أضفه في Streamlit Secrets أو متغيرات البيئة أو القائمة الجانبية.")

    prompt_text = build_prompt(sanitized_query, contexts, memory)

    # تجهيز قائمة النماذج لتجربتها بالترتيب لضمان الاستجابة من النماذج المجانية
    target_model = os.getenv("OPENROUTER_MODEL", LLM_MODEL)
    models_to_try = [target_model]
    for fallback in FREE_MODEL_FALLBACKS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_exception: Exception | None = None
    answer_text = ""
    successful_model = target_model

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
        }

        try:
            logger.info("محاولة توليد الإجابة باستخدام النموذج: %s", model_name)
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {active_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://streamlit.io",
                    "X-Title": "Arabic RAG Assistant",
                },
                json=payload,
                timeout=45,
            )
            response.raise_for_status()
            response_json = response.json()

            if "choices" in response_json and len(response_json["choices"]) > 0:
                content = response_json["choices"][0]["message"].get("content", "")
                if content and content.strip():
                    answer_text = content.strip()
                    successful_model = model_name
                    break
        except Exception as exc:
            logger.warning("تعذر الحصول على استجابة من النموذج %s: %s", model_name, exc)
            last_exception = exc
            continue

    if not answer_text:
        if last_exception:
            raise RuntimeError(f"تعذر استجابة نماذج OpenRouter المجانية: {last_exception}")
        raise RuntimeError("لم يتم إرجاع أي نص إجابة من نماذج الذكاء الاصطناعي.")

    logger.info("تم نجاح التوليد باستخدام %s لسؤال: %s", successful_model, sanitized_query)
    return {
        "answer": answer_text,
        "model_used": successful_model,
        "sources": [
            {
                "filename": item.get("filename", ""),
                "chunk_id": item.get("chunk_id", ""),
                "similarity": item.get("similarity", 0.0),
            }
            for item in contexts
        ],
    }


def get_llm(api_key: str | None = None, model_name: str = LLM_MODEL) -> Any:
    """تجهيز كائن ChatOpenAI الخاص بـ LangChain مع دعم OpenRouter."""
    active_key = get_openrouter_api_key(api_key)
    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=active_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=model_name,
        )
    except Exception as exc:
        logger.warning("تعذر تحميل langchain_openai: %s", exc)
        return None


def get_prompt_template() -> Any:
    """بناء قالب الموجه الخاص بـ LangChain."""
    try:
        from langchain.prompts import ChatPromptTemplate
        template = """أنت مساعد عربي ذكي وتفاعلي. أجب على السؤال التالي بناءً على السياق المسترجع.
إذا كان السؤال بحاجة لتوضيح ناقش المستخدم واسأله، واذكر المصدر في نهاية الإجابة إن وُجد.

السياق:
{context}

السؤال: {question}

الإجابة:"""
        return ChatPromptTemplate.from_template(template)
    except Exception as exc:
        logger.warning("تعذر تحميل langchain.prompts: %s", exc)
        return None
