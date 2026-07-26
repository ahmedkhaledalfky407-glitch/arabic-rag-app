# مساعد RAG عربي ذكي
### Arabic RAG-Powered Knowledge Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37%2B-red)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5%2B-green)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

نظام استرجاع وتعزيز توليد (RAG) متكامل باللغة العربية، مصمم خصيصاً للعمل مع الوثائق القانونية العربية. يعتمد على استرجاع السياق من المستندات وتوليد إجابات دقيقة باستخدام نماذج لغوية كبيرة (LLMs) عبر OpenRouter.

---

## ✨ الميزات الرئيسية

- **🔍 استرجاع ذكي للمعرفة** — استخدام ChromaDB و embeddings متعددة اللغات للبحث الدلالي في المستندات العربية
- **⚡ دعم متعدد النماذج** — تكامل مع OpenRouter (GPT-4o-mini, Llama, DeepSeek, Gemini, وغيرها)
- **🔐 أمان متكامل** — حماية من حقن الأوامر (Prompt Injection) والاستعلامات الضارة
- **💬 ذاكرة محادثة** — حفظ سياق المحادثة لأسئلة متتابعة بحد أقصى 10 رسائل
- **📤 رفع ملفات ديناميكي** — دعم رفع ملفات TXT جديدة وإعادة بناء قاعدة المعرفة تلقائياً
- **📊 واجهة احترافية** — واجهة Streamlit متجاوبة مع RTL، إحصائيات مباشرة، وعرض المصادر
- **🧠 معالجة نص عربي متقدمة** — تنظيف وتطبيع النص العربي مع الحفاظ على المحتوى اللاتيني

---

## 🏗️ البنية المعمارية

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  المستندات TXT  │───▶│  المعالجة المسبقة │───▶│   تقسيم النص    │
│  (documents/)   │    │  (Preprocessing)  │    │   (Chunking)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  واجهة Streamlit│◀───│  الاسترجاع       │◀───│  متجهات Embedding│
│  (streamlit_app)│    │  (Retrieval)     │    │  (Vector Rep)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       ▲                       │
        │                       │                       │
        ▼                       │                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LLM (OpenRouter)│───▶│  التوليد         │◀───│  ChromaDB Store │
│  gpt-4o-mini     │    │  (Prompting)     │    │  (Vector DB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### خطوات المعالجة:

| الخطوة | الملف | الوصف |
|--------|------|-------|
| 1 | `01_documents.py` | تحميل المستندات النصية من مجلد `documents/` |
| 2 | `02_preprocessing.py` | تنظيف وتطبيع النص العربي |
| 3 | `03_chunking.py` | تقسيم النص إلى قطع نصية (chunks) متداخلة |
| 4 | `04_vector_representation.py` | تحويل النصوص إلى متجهات رقمية (embeddings) |
| 5 | `05_create_chroma_store.py` | بناء قاعدة بيانات المتجهات |
| 6 | `06_retrieve_context.py` | استرجاع السياق الأكثر صلة بالسؤال |
| 7 | `07_prompting.py` | توليد الإجابة النهائية باستخدام LLM |

---

## 📦 المتطلبات

- Python 3.11 أو أحدث
- pip أو uv
- مفتاح OpenRouter API ([احصل على مفتاح مجاني](https://openrouter.ai/))

---

## 🚀 التثبيت

### 1. استنساخ المشروع

```bash
git clone https://github.com/yourusername/arabic-rag-assistant.git
cd rag_labor_law_project/rag_project
```

### 2. إنشاء بيئة افتراضية

```bash
python -m venv venv311

# Windows
venv311\Scripts\activate

# Linux/Mac
source venv311/bin/activate
```

### 3. تثبيت التبعيات

```bash
pip install -r requirements.txt
```

> **ملاحظة لنظام Linux:** قد تحتاج لتثبيت الحزم التالية أولاً:
> ```bash
> sudo apt install build-essential gcc g++
> ```

### 4. إعداد متغيرات البيئة

أنشئ ملف `.env` في جذر المشروع:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=openrouter/free
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

أو استخدم Streamlit Secrets (للنشر):

```toml
# .streamlit/secrets.toml
OPENROUTER_API_KEY = "sk-or-v1-xxxxx"
OPENROUTER_MODEL = "openrouter/free"
```

---

## 💻 الاستخدام

### التشغيل المحلي

```bash
streamlit run app.py
```

### بناء قاعدة المعرفة

بعد تشغيل التطبيق:

1. **ارفع ملفات TXT** من القائمة الجانبية
2. **اضغط "إعادة بناء قاعدة المعرفة"** لمعالجة المستندات وإنشاء المتجهات
3. **ابدأ المحادثة** بطرح أسئلة على مستنداتك

### الاستخدام البرمجي

```python
from 01_documents import load_documents_from_directory, save_documents
from 02_preprocessing import run_preprocessing
from 03_chunking import run_chunking
from 04_vector_representation import build_embeddings
from 05_create_chroma_store import run_store_creation
from 06_retrieve_context import retrieve_context
from 07_prompting import ask
from memory import ConversationMemory

# 1. تحميل المستندات
documents = load_documents_from_directory("documents/")
save_documents(documents)

# 2. المعالجة المسبقة
run_preprocessing()

# 3. التقسيم
run_chunking()

# 4. المتجهات
build_embeddings()

# 5. قاعدة البيانات
run_store_creation()

# 6. الاستعلام
memory = ConversationMemory()
contexts = retrieve_context("ما هي حقوق العامل؟", k=5)
result = ask("ما هي حقوق العامل؟", contexts, memory)
print(result["answer"])
```

---

## ⚙️ الإعدادات المتقدمة

| المعامل | الافتراضي | الوصف |
|---------|----------|-------|
| `CHUNK_SIZE` | 700 | حجم القطعة النصية بالحروف |
| `CHUNK_OVERLAP` | 120 | التداخل بين القطع المتتالية |
| `TOP_K` | 5 | عدد النتائج المسترجعة |
| `MIN_SIMILARITY` | 0.40 | حد أدنى للتشابه لاعتبار النتيجة صالحة |
| `TEMPERATURE` | 0.2 | درجة إبداع النموذج (أقل = أكثر دقة) |
| `MAX_TOKENS` | 800 | الحد الأقصى لطول الإجابة |
| `MAX_MEMORY_MESSAGES` | 10 | عدد رسائل المحادثة المحفوظة |

---

## 📁 هيكل المشروع

```
rag_labor_law_project/
├── rag_project/
│   ├── app.py                      # نقطة الدخول الرئيسية
│   ├── streamlit_app.py            # واجهة المستخدم
│   ├── config.py                   # إعدادات التكوين
│   ├── requirements.txt            # تبعيات Python
│   ├── packages.txt                # تبعيات النظام (Linux)
│   ├── documents/                  # مجلد المستندات المصدرية
│   │   ├── sample_knowledge.txt
│   │   └── قانون_العمل.txt
│   ├── data/                       # بيانات وسيطة
│   │   ├── 01_documents.json
│   │   ├── 02_preprocessed.json
│   │   ├── 03_chunks.json
│   │   └── 04_embeddings.npy
│   ├── chroma_db/                  # قاعدة بيانات المتجهات
│   ├── logs/                       # ملفات السجل
│   ├── 01_documents.py             # تحميل المستندات
│   ├── 02_preprocessing.py         # تنظيف النص
│   ├── 03_chunking.py              # تقسيم النص
│   ├── 04_vector_representation.py # تمثيل متجهي
│   ├── 05_create_chroma_store.py   # بناء المخزن
│   ├── 06_retrieve_context.py      # استرجاع السياق
│   ├── 07_prompting.py             # التوليد والاستعلام
│   ├── security.py                 # الأمان والتحقق
│   ├── memory.py                   # ذاكرة المحادثة
│   ├── utils.py                    # أدوات مساعدة
│   └── logger.py                   # نظام التسجيل
├── .env.example                    # مثال لمتغيرات البيئة
├── README.md                       # هذا الملف
└── LICENSE                         # ترخيص MIT
```

---

## 🔐 الأمان

- **حماية من حقن الأوامر (Prompt Injection):** فحص الاستعلامات ضد أنماط الهجوم المعروفة بالعربية والإنجليزية
- **التحقق من النطاق (Scope Validation):** التأكد من أن الإجابة مبنية على المستندات فقط
- **إدارة آمنة للمفاتيح:** قراءة مفاتيح API من متغيرات البيئة أو Streamlit Secrets
- **تطهير الاستعلامات:** إزالة الأحرف الخطرة والتأكد من صحة المدخلات

---

## 🛠️ التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|-----------|
| **Python 3.11** | اللغة الأساسية |
| **Streamlit** | واجهة الويب |
| **ChromaDB** | قاعدة بيانات المتجهات |
| **Sentence Transformers** | نماذج الـ embeddings |
| **OpenRouter** | واجهة موحدة للـ LLMs |
| **NumPy** | العمليات الحسابية على المتجهات |

---

## 📝 ملاحظات هامة

1. **النماذج المدعومة:** يعمل المشروع مع أي نموذج متاح عبر OpenRouter. النموذج الافتراضي هو `openrouter/free` المجاني.
2. **حجم النماذج:** نموذج الـ embeddings (~500 MB) يُحمل مرة واحدة فقط ويُخزن محلياً في `~/.cache/huggingface/hub/`.
3. **الأداء:** يوصى باستخدام GPU لتسريع عملية إنشاء المتجهات مع المستندات الكبيرة.
4. **اللغة:** مصمم خصيصاً للنصوص العربية مع دعم المحتوى المختلط عربي/إنجليزي.

---

## 🤝 المساهمة

مرحباً بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. أنشئ فرعاً جديداً (`git checkout -b feature/amazing-feature`)
3. اعمل Commit (`git commit -m 'Add amazing feature'`)
4. ادفع إلى الفرع (`git push origin feature/amazing-feature`)
5. افتح Pull Request

---

## 📄 الرخصة

هذا المشروع مرخص تحت رخصة MIT — راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

## 📞 الدعم

إذا واجهت أي مشاكل أو لديك استفسارات، يرجى فتح Issue في GitHub.

---

<div align="center">
  <p>صُنع بـ ❤️ للمجتمع العربي</p>
</div>
