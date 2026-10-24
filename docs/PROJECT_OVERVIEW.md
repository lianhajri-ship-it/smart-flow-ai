# Smart Flow AI — Project Overview | نظرة شاملة على المشروع

**[العربية](#العربية)** · **[English](#english)**

> Status as of 2026-10-18 · version 0.1.0 · by Lina Alhajri

---

<a id="العربية"></a>

# العربية

## 1. نظرة عامة

**Smart Flow AI** أداة لأتمتة قراءة الفواتير الضريبية السعودية. يرفع المستخدم الفاتورة (ملف PDF أو صورة من الجوال)، فيستخرج النظام بياناتها الأساسية خلال ثوانٍ:

- اسم البائع
- الرقم الضريبي
- تاريخ الفاتورة ووقتها
- مبلغ ضريبة القيمة المضافة
- المبلغ المستحق شامل الضريبة

**الفكرة الأساسية:** كل فاتورة ضريبية في السعودية يجب أن تحتوي على رمز QR حسب متطلبات هيئة الزكاة والضريبة والجمارك (ZATCA). بدل محاولة قراءة النص المطبوع، وهو غير دقيق مع العربي، يقرأ النظام **رمز QR** مباشرة، فيحصل على بيانات رقمية دقيقة.

**الفئة المستهدفة:** المحاسبون وأصحاب المنشآت الصغيرة والمتوسطة الذين يُدخلون فواتير الموردين يدويًا.

## 2. حالة المشروع الحالية

| البند | الحالة |
|---|---|
| الإصدار | 0.1.0 |
| الاختبارات الآلية | ✅ 43 اختبارًا ناجحًا |
| التحقق على نماذج الهيئة الرسمية | ✅ 77 ملفًا من 77 |
| المستودع | GitHub، **خاص (Private)** |
| عدد النسخ المحفوظة (Commits) | 7 |
| النشر على الإنترنت | ⏳ لم يُنشر بعد، يعمل محليًا |
| التكلفة | صفر، كل الأدوات مجانية ومفتوحة المصدر |

## 3. المميزات

### القراءة والاستخراج
- **فك رمز QR الخاص بالهيئة** بصيغة TLV، بما فيها رموز **المرحلة الثانية** التي تحتوي حقول التوقيع الرقمي.
- **يدعم الملفات:** PDF و JPG و PNG و WEBP، بحد أقصى 10 ميجابايت.
- **يبحث في كل صفحات ملف PDF**، وليس الصفحة الأولى فقط.
- **يقرأ صور الجوال الصعبة:** يستخدم كاشفين مختلفين من OpenCV، ويجرّب الصورة بعدة أحجام، فينجح حتى مع الصور المهزوزة أو عالية الدقة.
- **يتجاهل رموز QR الأخرى** مثل روابط الدفع أو قوائم المطاعم، ويأخذ رمز الهيئة فقط.
- **بصمة لكل ملف (SHA-256)** تُستخدم لاحقًا لاكتشاف الفواتير المكررة.
- **يصلح النص العربي المعكوس** في ملفات PDF قدر الإمكان، ويستخدمه للمعاينة فقط.

### الموقع
- **مصمم للجوال أولًا** ويعمل على اللابتوب والآيباد.
- **زر تصوير** يفتح كاميرا الجوال الخلفية مباشرة.
- **السحب والإفلات** على اللابتوب.
- **لغتان:** العربية والإنجليزية، مع تغيير اتجاه الصفحة تلقائيًا.
- **اختيار اللغة تلقائيًا** حسب لغة جهاز الزائر، وحفظ اختياره للزيارات القادمة.
- **وضع ليلي** تلقائي حسب إعدادات الجهاز.
- **رسائل خطأ واضحة** باللغتين.

### الخصوصية والأمان
- **لا يُحفظ أي ملف:** الفاتورة تُعالج في مجلد مؤقت ثم تُحذف فورًا.
- **لا يُستخدم اسم الملف الذي يرسله المستخدم** على القرص، فلا يمكن استغلاله للكتابة خارج المجلد المسموح.
- **حد أقصى لحجم الملف:** لا يُقرأ أكثر من 10 ميجابايت.
- **حماية من XSS:** النصوص القادمة من الخادم تُعرض بـ `textContent` وليس `innerHTML`.

## 4. الصفحات والواجهات

### أ) الموقع — `http://localhost:8000/`
صفحة واحدة تتنقل بين أربع حالات:

| الحالة | ماذا تعرض |
|---|---|
| **الرفع** | منطقة "اسحب الفاتورة هنا"، وزر "تصوير الفاتورة"، وملاحظة الخصوصية |
| **جارٍ القراءة** | مؤشر تحميل دوّار |
| **النتيجة** | بيانات الفاتورة الخمس، أو رسالة "لم نجد رمز QR" مع نصائح للتصوير |
| **الخطأ** | رسالة واضحة حسب نوع المشكلة، وزر "المحاولة مرة أخرى" |

وفي كل الحالات: زر تبديل اللغة في الأعلى، وسطر الحقوق ورابط توثيق الـ API في الأسفل.

### ب) صفحات التوثيق التلقائية
| الرابط | الوصف |
|---|---|
| `/docs` | توثيق تفاعلي (Swagger UI) يمكن تجربة الـ API منه مباشرة |
| `/redoc` | نفس التوثيق بتصميم آخر (ReDoc) |
| `/openapi.json` | وصف الـ API بصيغة OpenAPI |

### ج) خدمات الـ API
| الطريقة | الرابط | الوظيفة |
|---|---|---|
| `GET` | `/api/health` | التأكد أن الخدمة تعمل |
| `POST` | `/api/extract` | رفع فاتورة واستخراج بياناتها |

**رموز الأخطاء:** `415` نوع الملف غير مدعوم، `413` الملف أكبر من 10 ميجابايت، `422` الملف تالف أو غير قابل للقراءة.

### د) أدوات سطر الأوامر
| الأمر | الوظيفة |
|---|---|
| `python -m smart_flow.web` | تشغيل الموقع |
| `scripts\start_site.cmd` | (Windows) تشغيل الموقع في الخلفية وفتحه بضغطتين |
| `scripts\stop_site.ps1` | (Windows) إيقاف الموقع الذي يعمل في الخلفية |
| `python -m smart_flow` | معالجة كل الفواتير في مجلد `data/inbox` دفعة واحدة |
| `python scripts/make_sample_invoice.py` | إنشاء فاتورة تجريبية فيها رمز QR |
| `python scripts/check_zatca_samples.py` | اختبار النظام على نماذج الهيئة الرسمية |
| `python scripts/take_screenshots.py` | تصوير الموقع تلقائيًا للتوثيق |
| `pytest` | تشغيل الاختبارات الآلية |

## 5. طريقة العمل (البنية)

```
الفاتورة (PDF أو صورة)
   │
   ▼
InvoiceReader ── يتحقق من النوع والحجم، ويحسب بصمة الملف
   │
   ▼
ExtractionPipeline ── يجرّب طرق الاستخراج بالترتيب ويتوقف عند أول نجاح
   │
   ├─ 1. QrExtractor      رمز QR الخاص بالهيئة   ✅ جاهز
   ├─ 2. RegexExtractor   قواعد على النص          ⏳ مخطط
   └─ 3. ذكاء اصطناعي محلي                       ⏳ مخطط
   │
   ▼
InvoiceData ── البائع، الرقم الضريبي، التاريخ، المبلغ المستحق، الضريبة
```

**مبدأ مهم:** منطق المشروع منفصل تمامًا عن الواجهات. الموقع والـ API وأداة سطر الأوامر كلها تستدعي نفس الكود.

### ملفات الكود
| الملف | المسؤولية |
|---|---|
| `src/smart_flow/config.py` | قراءة الإعدادات من ملف `.env` |
| `src/smart_flow/logger.py` | إعداد السجلات، ودعم العربي على شاشة Windows |
| `src/smart_flow/reader.py` | قراءة الملفات والتحقق منها، وإصلاح النص العربي المعكوس |
| `src/smart_flow/qr.py` | البحث عن رموز QR في الصور وصفحات PDF |
| `src/smart_flow/zatca.py` | ترميز وفك صيغة TLV الخاصة بالهيئة |
| `src/smart_flow/extractor.py` | سلسلة طرق الاستخراج |
| `src/smart_flow/models.py` | نموذج البيانات المشترك `InvoiceData` |
| `src/smart_flow/main.py` | أداة سطر الأوامر لمعالجة مجلد كامل |
| `src/smart_flow/web/app.py` | الخادم والـ API |
| `src/smart_flow/web/static/` | الصفحة: `index.html` و `style.css` و `app.js` |

## 6. التقنيات

| المجال | التقنية | الإصدار | سبب الاختيار |
|---|---|---|---|
| اللغة | Python | 3.13 | سهلة ومناسبة للأتمتة والبيانات |
| الخادم | FastAPI | 0.143 | سريع، ويولّد التوثيق تلقائيًا، ومطلوب في سوق العمل |
| تشغيل الخادم | Uvicorn | 0.54 | الخادم الموصى به مع FastAPI |
| التحقق من البيانات | Pydantic | 2.14 | يحدد شكل الرد ويتحقق منه تلقائيًا |
| رفع الملفات | python-multipart | 0.0.32 | يستقبل الملفات المرفوعة في FastAPI |
| قراءة نص PDF | pdfplumber | 0.11 | استخراج النص من ملفات PDF |
| تحويل PDF لصور | pypdfium2 | 5.14 | سريع ولا يحتاج برامج خارجية |
| معالجة الصور | Pillow و NumPy | 13.0 و 2.5 | فتح الصور وتجهيزها |
| قراءة رمز QR | OpenCV (headless) | 5.0 | كاشفان مختلفان لرموز QR |
| اتجاه النص العربي | python-bidi | 0.6 | إعادة النص المعكوس لترتيبه الصحيح |
| الإعدادات | python-dotenv | 1.2 | قراءة ملف `.env` |
| الواجهة | HTML و CSS و JavaScript | — | بدون مكتبات إضافية، خفيفة وسريعة |
| الخط | IBM Plex Sans Arabic | — | خط مجاني من Google Fonts يدعم العربي والإنجليزي |

## 7. أدوات التطوير

| الأداة | الاستخدام |
|---|---|
| **VS Code** | محرر الكود |
| **البيئة الافتراضية `.venv`** | عزل مكتبات المشروع عن باقي الجهاز |
| **pyproject.toml** | تعريف المشروع ومكتباته |
| **pytest** | الاختبارات الآلية |
| **FastAPI TestClient و httpx** | اختبار الـ API بدون تشغيل خادم |
| **fpdf2 و uharfbuzz** | إنشاء فواتير PDF عربية للاختبار |
| **segno** | إنشاء رموز QR للاختبار |
| **Playwright مع متصفح Edge** | تصوير الموقع تلقائيًا |
| **Git** | حفظ نسخ المشروع وتاريخه |
| **GitHub و GitHub CLI (`gh`)** | المستودع الخاص على الإنترنت |
| **حزمة الهيئة (ZATCA SDK)** | نماذج فواتير رسمية للتحقق من صحة النظام |

## 8. الاختبارات والجودة

### الاختبارات الآلية (43 اختبارًا)
| الملف | العدد | ماذا يختبر |
|---|---|---|
| `test_config.py` | 3 | قراءة الإعدادات وإنشاء المجلدات |
| `test_reader.py` | 13 | قراءة PDF والصور، والنص العربي المعكوس، والملفات التالفة والفارغة وغير المدعومة |
| `test_zatca.py` | 9 | فك وترميز رمز QR، والاسم العربي، والبيانات الناقصة أو التالفة |
| `test_extractor.py` | 6 | قراءة الرمز من صورة ومن PDF، وتجاهل الرموز الأخرى، وترتيب طرق الاستخراج |
| `test_web.py` | 9 | الـ API، وصورة جوال مهزوزة، والملفات الكبيرة والتالفة، واسم ملف ضار |
| `test_translations.py` | 3 | أن كل نص في الصفحة مترجم للغتين |

### التحقق على نماذج الهيئة الرسمية
السكربت `check_zatca_samples.py` يقارن بيانات رمز QR ببيانات الفاتورة نفسها، حقلًا حقلًا:

| النوع | العدد | النتيجة |
|---|---|---|
| ملفات XML | 45 | ✅ 45 من 45 |
| ملفات PDF/A-3 | 32 | ✅ 32 من 32 |

**اكتشاف مهم:** المبلغ داخل رمز QR هو **المبلغ المستحق** (PayableAmount)، وليس الإجمالي شامل الضريبة. ويختلفان عند وجود دفعة مقدمة أو تقريب.

## 9. الإعدادات (ملف `.env`)

| المتغير | القيمة الافتراضية | الوصف |
|---|---|---|
| `LOG_LEVEL` | `INFO` | مستوى السجلات: DEBUG أو INFO أو WARNING أو ERROR |
| `DATA_DIR` | `data` | مجلد بيانات العمل |
| `HOST` | `127.0.0.1` | `0.0.0.0` لفتح الموقع من جوال على نفس الشبكة |
| `PORT` | `8000` | منفذ الموقع |

**مجلدات البيانات** (لا تُرفع إلى GitHub): `data/inbox` للفواتير الجديدة، و `data/processed` و `data/failed` للمراحل القادمة، و `data/zatca-sdk` لنماذج الهيئة، و `logs/` للسجلات.

## 10. المشاكل التي حُلّت أثناء التطوير

| المشكلة | الحل |
|---|---|
| النص العربي في PDF يخرج معكوسًا، والتاريخ مقلوبًا، وبعض الكلمات مكسّرة | اعتماد رمز QR كمصدر للبيانات، والنص للمعاينة فقط |
| شاشة Windows لا تعرض العربي في السجلات | ضبط الترميز على UTF-8 |
| آلاف الأسطر من سجلات مكتبة pdfminer | عرض التحذيرات فقط من المكتبات الخارجية |
| مكتبة segno أنتجت Micro QR لا تقرؤه OpenCV | استخدام `make_qr` لإنتاج رمز عادي |
| الكاشف العادي يفشل مع صور الجوال المهزوزة | كاشف إضافي أقوى، مع تجربة عدة أحجام، واختبار يثبت التحسين |
| طول الحقول في TLV بالبايت وليس بالحرف | ترميز دقيق، لأن الحرف العربي يأخذ بايتين |
| الإجمالي في رمز QR لا يطابق الإجمالي في بعض الفواتير | اكتشاف أنه المبلغ المستحق، وتعديل الواجهة |
| النص الإنجليزي ينقلب داخل الصفحة العربية | عزله بالوسم `<bdi>` |

## 11. القيود الحالية

- ❌ الفواتير التي ليس فيها رمز QR لا تُقرأ بعد.
- ❌ صور iPhone بصيغة HEIC غير مدعومة عند رفعها كملف، أما التصوير من زر الكاميرا فيعمل.
- ⚠️ لم يُختبر بعد على عدد كبير من صور الفواتير الحقيقية الملتقطة بالجوال.
- ❌ لا يتحقق بعد من صحة الرقم الضريبي أو من حساب الضريبة.
- ❌ لا يوجد حد لعدد الطلبات (Rate limiting)، ونحتاجه قبل النشر العام.

## 12. خطة التطوير

- [x] قراءة ملفات PDF والصور
- [x] فك رمز QR الخاص بالهيئة، والتحقق على النماذج الرسمية
- [x] موقع بلغتين مصمم للجوال، مع API موثّق
- [ ] فواتير نموذجية وزر "جرّب بفاتورة نموذجية"
- [ ] التحقق من الفاتورة: صيغة الرقم الضريبي، وحساب الضريبة، والتكرار
- [ ] قواعد استخراج للفواتير التي ليس فيها رمز QR
- [ ] رفع عدة فواتير وتصديرها إلى Excel
- [ ] Docker ونشر الموقع للعامة
- [ ] تثبيت الموقع كتطبيق جوال (PWA)

## 13. الحقوق

© 2026 لينا الهاجري. جميع الحقوق محفوظة. الكود متاح للاطلاع فقط، واستخدام الموقع المنشور للتجربة مسموح للجميع. راجع ملف [LICENSE](../LICENSE).

---

<a id="english"></a>

# English

## 1. Overview

**Smart Flow AI** automates reading Saudi tax invoices. A user uploads an invoice (a PDF or a phone photo) and gets its key data within seconds:

- Seller name
- VAT number
- Invoice date and time
- VAT amount
- Amount due including VAT

**The core idea:** every tax invoice in Saudi Arabia must carry a QR code defined by ZATCA (the Zakat, Tax and Customs Authority). Instead of reading the printed text, which is unreliable for Arabic, the system reads the **QR code** directly and gets exact digital data.

**Target users:** accountants and small and medium businesses that type supplier invoices in by hand.

## 2. Current status

| Item | Status |
|---|---|
| Version | 0.1.0 |
| Automated tests | ✅ 43 passing |
| Check against official ZATCA samples | ✅ 77 of 77 files |
| Repository | GitHub, **private** |
| Commits | 7 |
| Public deployment | ⏳ Not yet, runs locally |
| Cost | Zero: free, open-source tools only |

## 3. Features

### Reading and extraction
- **ZATCA QR decoding** of the TLV format, including **Phase 2** codes with cryptographic stamp fields.
- **Supported files:** PDF, JPG, PNG and WEBP, up to 10 MB.
- **Scans every PDF page**, not just the first.
- **Handles difficult phone photos:** two different OpenCV detectors at several image sizes, so blurry or high-resolution photos still read.
- **Ignores other QR codes** such as payment links or restaurant menus and keeps only the ZATCA code.
- **SHA-256 fingerprint per file**, for duplicate detection later.
- **Repairs reversed Arabic text** from PDFs where possible, used for previews only.

### Website
- **Mobile-first**, also works on laptops and tablets.
- **Camera button** opens the phone's rear camera directly.
- **Drag and drop** on desktop.
- **Two languages:** Arabic and English, with automatic right-to-left and left-to-right layout.
- **Language auto-detected** from the visitor's device and remembered for later visits.
- **Dark mode** following the device setting.
- **Clear error messages** in both languages.

### Privacy and security
- **No file is stored:** invoices are processed in a temporary folder and deleted immediately.
- **The client's filename is never used on disk**, so it cannot be abused to write outside the allowed folder.
- **Upload size cap:** nothing beyond 10 MB is read.
- **XSS protection:** server text is rendered with `textContent`, never `innerHTML`.

## 4. Pages and interfaces

### a) Website — `http://localhost:8000/`
A single page that moves between four states:

| State | What it shows |
|---|---|
| **Upload** | "Drop your invoice here" area, "Take a photo" button and a privacy note |
| **Reading** | A spinner |
| **Result** | The five invoice fields, or "No QR code found" with photo tips |
| **Error** | A clear message for the specific problem and a "Try again" button |

In every state: a language toggle at the top, and the copyright line and an API docs link at the bottom.

### b) Auto-generated documentation
| URL | Description |
|---|---|
| `/docs` | Interactive docs (Swagger UI), try the API from the browser |
| `/redoc` | The same docs in ReDoc style |
| `/openapi.json` | Machine-readable OpenAPI description |

### c) API endpoints
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check that the service is running |
| `POST` | `/api/extract` | Upload an invoice and extract its data |

**Error codes:** `415` unsupported file type, `413` file larger than 10 MB, `422` damaged or unreadable file.

### d) Command-line tools
| Command | Purpose |
|---|---|
| `python -m smart_flow.web` | Run the website |
| `scripts\start_site.cmd` | (Windows) start the site in the background and open it, by double-click |
| `scripts\stop_site.ps1` | (Windows) stop the background site |
| `python -m smart_flow` | Process every invoice in `data/inbox` in one batch |
| `python scripts/make_sample_invoice.py` | Create a sample invoice with a QR code |
| `python scripts/check_zatca_samples.py` | Check the system against the official ZATCA samples |
| `python scripts/take_screenshots.py` | Take documentation screenshots automatically |
| `pytest` | Run the automated tests |

## 5. How it works (architecture)

```
Invoice (PDF or photo)
   │
   ▼
InvoiceReader ── validates type and size, fingerprints the file
   │
   ▼
ExtractionPipeline ── tries extractors in order, stops at the first success
   │
   ├─ 1. QrExtractor      ZATCA QR code   ✅ implemented
   ├─ 2. RegexExtractor   text rules      ⏳ planned
   └─ 3. Local AI model                   ⏳ planned
   │
   ▼
InvoiceData ── seller, VAT number, date, amount due, VAT amount
```

**Key principle:** the core logic is fully separate from the interfaces. The website, the API and the command-line tool all call the same code.

### Source files
| File | Responsibility |
|---|---|
| `src/smart_flow/config.py` | Load settings from `.env` |
| `src/smart_flow/logger.py` | Logging setup, Arabic output on the Windows console |
| `src/smart_flow/reader.py` | Read and validate files, repair reversed Arabic text |
| `src/smart_flow/qr.py` | Find QR codes in images and PDF pages |
| `src/smart_flow/zatca.py` | Encode and decode the ZATCA TLV format |
| `src/smart_flow/extractor.py` | Extraction pipeline |
| `src/smart_flow/models.py` | Shared `InvoiceData` model |
| `src/smart_flow/main.py` | Command-line batch tool |
| `src/smart_flow/web/app.py` | Web server and API |
| `src/smart_flow/web/static/` | The page: `index.html`, `style.css`, `app.js` |

## 6. Technologies

| Area | Technology | Version | Why |
|---|---|---|---|
| Language | Python | 3.13 | Clear and well suited to automation and data |
| Web framework | FastAPI | 0.143 | Fast, auto-generated docs, in demand in the job market |
| ASGI server | Uvicorn | 0.54 | The recommended server for FastAPI |
| Data validation | Pydantic | 2.14 | Defines and validates the response shape |
| File uploads | python-multipart | 0.0.32 | Receives uploaded files in FastAPI |
| PDF text | pdfplumber | 0.11 | Extracts text from PDFs |
| PDF rendering | pypdfium2 | 5.14 | Fast, no external programs needed |
| Image handling | Pillow, NumPy | 13.0, 2.5 | Open and prepare images |
| QR detection | OpenCV (headless) | 5.0 | Two different QR detectors |
| Arabic text direction | python-bidi | 0.6 | Restores reversed text to logical order |
| Settings | python-dotenv | 1.2 | Reads the `.env` file |
| Frontend | HTML, CSS, JavaScript | — | No frameworks, light and fast |
| Font | IBM Plex Sans Arabic | — | Free Google Font covering Arabic and Latin |

## 7. Development tools

| Tool | Use |
|---|---|
| **VS Code** | Code editor |
| **Virtual environment `.venv`** | Isolates the project's libraries |
| **pyproject.toml** | Project and dependency definition |
| **pytest** | Automated tests |
| **FastAPI TestClient, httpx** | Test the API without a running server |
| **fpdf2, uharfbuzz** | Generate Arabic PDF invoices for tests |
| **segno** | Generate QR codes for tests |
| **Playwright with Microsoft Edge** | Automated screenshots |
| **Git** | Version history |
| **GitHub, GitHub CLI (`gh`)** | Private online repository |
| **ZATCA SDK** | Official sample invoices to verify correctness |

## 8. Testing and quality

### Automated tests (43)
| File | Count | What it covers |
|---|---|---|
| `test_config.py` | 3 | Settings and folder creation |
| `test_reader.py` | 13 | PDFs and images; reversed Arabic text; damaged, empty and unsupported files |
| `test_zatca.py` | 9 | QR encoding and decoding, Arabic names, missing or corrupted data |
| `test_extractor.py` | 6 | QR from an image and a PDF, skipping other QR codes, extractor order |
| `test_web.py` | 9 | The API, a blurry phone photo, oversized and damaged files, a malicious filename |
| `test_translations.py` | 3 | Every page text exists in both languages |

### Check against official ZATCA samples
`check_zatca_samples.py` compares the QR data with the invoice body, field by field:

| Type | Files | Result |
|---|---|---|
| XML invoices | 45 | ✅ 45 / 45 |
| PDF/A-3 invoices | 32 | ✅ 32 / 32 |

**Key finding:** the amount in the QR code is the **amount payable** (`PayableAmount`), not the VAT-inclusive total. They differ when an invoice has an advance payment or a rounding adjustment.

## 9. Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING or ERROR |
| `DATA_DIR` | `data` | Working data folder |
| `HOST` | `127.0.0.1` | Use `0.0.0.0` to open the site from a phone on the same network |
| `PORT` | `8000` | Website port |

**Data folders** (never pushed to GitHub): `data/inbox` for new invoices, `data/processed` and `data/failed` for upcoming stages, `data/zatca-sdk` for the official samples, and `logs/` for log files.

## 10. Problems solved during development

| Problem | Solution |
|---|---|
| Arabic text from PDFs came out reversed, with swapped dates and broken words | Use the QR code as the data source; keep text for previews only |
| The Windows console could not print Arabic logs | Switch the console encoding to UTF-8 |
| Thousands of pdfminer debug lines | Show only warnings from third-party libraries |
| segno produced Micro QR codes that OpenCV cannot read | Use `make_qr` to produce standard QR codes |
| The standard detector failed on blurry phone photos | Add a stronger second detector and several image sizes, with a regression test |
| TLV lengths count bytes, not characters | Byte-accurate encoding, since each Arabic letter takes two bytes |
| The QR total did not match the invoice total on some invoices | Found it is the amount payable and relabeled it in the UI |
| English text flipped inside the Arabic page | Isolate it with `<bdi>` |

## 11. Current limitations

- ❌ Invoices without a QR code are not read yet.
- ❌ iPhone HEIC files are not supported as uploads; the in-site camera button works.
- ⚠️ Not yet tested on a large set of real phone photos of invoices.
- ❌ No VAT number or VAT calculation validation yet.
- ❌ No rate limiting yet, needed before a public launch.

## 12. Roadmap

- [x] Read PDFs and images
- [x] Decode ZATCA QR codes, verified against the official samples
- [x] Bilingual, mobile-first website with a documented API
- [ ] Sample invoices and a "try a sample" button
- [ ] Invoice validation: VAT number format, VAT calculation, duplicates
- [ ] Rule-based extraction for invoices without a QR code
- [ ] Batch upload with Excel export
- [ ] Docker and public deployment
- [ ] Installable phone app (PWA)

## 13. License

© 2026 Lina Alhajri. All rights reserved. The source code is visible for evaluation only; using the hosted demo is free for everyone. See [LICENSE](../LICENSE).
