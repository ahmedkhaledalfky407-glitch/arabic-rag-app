# تطبيق RAG عربي للوثائق النصية

هذا المشروع يبني تطبيق Retrieval-Augmented Generation (RAG) باللغة العربية باستخدام:
- Streamlit
- OpenRouter
- ChromaDB
- BAAI/bge-m3
- TXT files

## المتطلبات

- Python 3.11+
- مفتاح OpenRouter
- اتصال بالإنترنت لتنزيل النموذج والاتصال بخدمة OpenRouter

## التثبيت

1. أنشئ بيئة افتراضية:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. ثبّت المكتبات:
   ```bash
   pip install -r requirements.txt
   ```
3. أنشئ ملف .env بناءً على .env.example وأضف المفتاح:
   ```bash
   copy .env.example .env
   ```
4. ضع ملفات TXT داخل مجلد documents أو data.

## التشغيل

1. بناء قاعدة المتجهات:
   ```bash
   python 05_create_chroma_store.py
   ```
2. تشغيل التطبيق:
   ```bash
   streamlit run streamlit_app.py
   ```

## نشر على Streamlit Community Cloud

1. ارفع المشروع بالكامل إلى GitHub.
2. في Streamlit Cloud اختر New app.
3. اربط المستودع الخاص بك.
4. اختر الملف الرئيسي كـ app.py أو streamlit_app.py.
5. أضف المتغيرات السرية في Streamlit Secrets:
   - OPENROUTER_API_KEY
   - OPENROUTER_MODEL
6. تأكد من أن requirements.txt يحتوي على المكتبات المطلوبة.

## إعداد OpenRouter

- أضف المفتاح في ملف .env باسم OPENROUTER_API_KEY.
- أو أضفه في Streamlit Secrets باسم OPENROUTER_API_KEY.
- يمكنك تغيير النموذج عبر OPENROUTER_MODEL.

## النشر

- تأكد من أن مجلد chroma_db موجود في النشر.
- تأكد من أن ملفات TXT موجودة داخل المجلدات المناسبة قبل البناء.

## هيكل المشروع

- 01_documents.py: تحميل الملفات النصية
- 02_preprocessing.py: تنظيف النص العربي
- 03_chunking.py: تقسيم النص إلى chunks
- 04_vector_representation.py: إنشاء embeddings
- 05_create_chroma_store.py: بناء ChromaDB
- 06_retrieve_context.py: استرجاع السياق
- 07_prompting.py: توليد الإجابات عبر OpenRouter
- streamlit_app.py: واجهة المستخدم
