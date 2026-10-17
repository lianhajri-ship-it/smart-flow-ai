// منطق الصفحة: اللغتان، ورفع الفاتورة إلى /api/extract، وعرض النتيجة

// ---------- الترجمة ----------
// كل نص في الصفحة له مفتاح واحد، وقيمته بالعربي والإنجليزي
const TRANSLATIONS = {
  ar: {
    pageTitle: "Smart Flow AI | قراءة الفواتير",
    switchLanguage: "English",
    heroTitle: "بيانات فاتورتك في ثوانٍ",
    heroSubtitle: "ارفع الفاتورة الضريبية أو صوّر رمز QR فيها، ونستخرج البائع والرقم الضريبي والمبالغ تلقائيًا.",
    dropTitle: "اسحب الفاتورة هنا أو اضغط للاختيار",
    dropHint: "PDF أو صورة • حتى 10MB",
    cameraButton: "📷 تصوير الفاتورة",
    privacy: "🔒 لا نحفظ ملفاتك: تُقرأ الفاتورة ثم تُحذف فورًا.",
    loading: "جارٍ قراءة الفاتورة...",
    found: "✓ تمت قراءة الفاتورة",
    notFound: "لم نجد رمز QR",
    seller: "البائع",
    vatNumber: "الرقم الضريبي",
    date: "التاريخ",
    vatAmount: "ضريبة القيمة المضافة",
    total: "الإجمالي شامل الضريبة",
    currency: "ر.س",
    notFoundIntro: "لم نجد رمز QR صالحًا في هذه الفاتورة. جرّب:",
    tipCloseUp: "تصوير رمز QR عن قرب وبشكل واضح",
    tipLight: "إضاءة جيدة بدون ظل على الرمز",
    tipFlat: "وضع الفاتورة مسطّحة وتصويرها من الأعلى",
    readAnother: "قراءة فاتورة أخرى",
    tryAgain: "المحاولة مرة أخرى",
    rightsReserved: "جميع الحقوق محفوظة.",
    error413: "حجم الملف أكبر من 10MB.",
    error415: "نوع الملف غير مدعوم. استخدم PDF أو صورة (JPG أو PNG أو WEBP).",
    error422: "تعذّرت قراءة الملف. تأكد أنه غير تالف.",
    errorUnexpected: "حدث خطأ غير متوقع، حاول مرة أخرى.",
    errorNetwork: "تعذّر الاتصال بالخادم. تأكد أن الموقع يعمل.",
  },
  en: {
    pageTitle: "Smart Flow AI | Invoice Reader",
    switchLanguage: "العربية",
    heroTitle: "Your invoice data in seconds",
    heroSubtitle: "Upload a Saudi tax invoice or snap its QR code, and we extract the seller, VAT number and amounts automatically.",
    dropTitle: "Drop your invoice here or click to choose",
    dropHint: "PDF or image • up to 10MB",
    cameraButton: "📷 Take a photo",
    privacy: "🔒 We don't store your files: the invoice is read, then deleted immediately.",
    loading: "Reading your invoice...",
    found: "✓ Invoice read successfully",
    notFound: "No QR code found",
    seller: "Seller",
    vatNumber: "VAT number",
    date: "Date",
    vatAmount: "VAT amount",
    total: "Total incl. VAT",
    currency: "SAR",
    notFoundIntro: "We couldn't find a valid QR code in this invoice. Try:",
    tipCloseUp: "Taking a close, sharp photo of the QR code",
    tipLight: "Good lighting with no shadow on the code",
    tipFlat: "Laying the invoice flat and shooting from above",
    readAnother: "Read another invoice",
    tryAgain: "Try again",
    rightsReserved: "All rights reserved.",
    error413: "The file is larger than 10MB.",
    error415: "Unsupported file type. Use a PDF or an image (JPG, PNG or WEBP).",
    error422: "We couldn't read this file. Make sure it isn't damaged.",
    errorUnexpected: "Something went wrong, please try again.",
    errorNetwork: "Can't reach the server. Make sure the site is running.",
  },
};

const $ = (id) => document.getElementById(id);
const CARDS = ["upload-card", "status-card", "result-card", "error-card"];

let language = detectLanguage();
let lastResult = null;   // نحفظ آخر نتيجة وآخر خطأ حتى نعيد عرضهما عند تغيير اللغة
let lastErrorKey = null;

function detectLanguage() {
  try {
    const saved = localStorage.getItem("language");
    if (saved in TRANSLATIONS) return saved;
  } catch {
    // localStorage قد يكون محظورًا في التصفح الخاص، فنتجاهل الخطأ
  }
  return navigator.language.startsWith("ar") ? "ar" : "en";
}

function t(key) {
  return TRANSLATIONS[language][key] ?? TRANSLATIONS.ar[key] ?? key;
}

function applyLanguage(newLanguage) {
  language = newLanguage;
  const root = document.documentElement;
  root.lang = language;
  root.dir = language === "ar" ? "rtl" : "ltr";
  document.title = t("pageTitle");

  for (const element of document.querySelectorAll("[data-i18n]")) {
    element.textContent = t(element.dataset.i18n);
  }

  if (lastResult) renderResult(lastResult);
  if (lastErrorKey) $("error-message").textContent = t(lastErrorKey);

  try {
    localStorage.setItem("language", language);
  } catch {
    // نفس السبب أعلاه
  }
}

// ---------- عرض النتيجة ----------
function showCard(id) {
  for (const card of CARDS) $(card).classList.toggle("hidden", card !== id);
}

function formatMoney(value) {
  if (value == null) return "—";
  const number = Number(value).toLocaleString("en-US", { minimumFractionDigits: 2 });
  return `${number} ${t("currency")}`;
}

function formatDate(value) {
  return value ? value.replace("T", "  ").slice(0, 17) : "—";
}

function renderResult(data) {
  lastResult = data;
  const badge = $("result-badge");
  badge.textContent = t(data.found ? "found" : "notFound");
  badge.className = `badge ${data.found ? "badge-success" : "badge-warning"}`;

  $("fields").classList.toggle("hidden", !data.found);
  $("not-found").classList.toggle("hidden", data.found);

  if (data.found) {
    // textContent وليس innerHTML: لا نُدخل نصًا من الخادم كـ HTML أبدًا (حماية من XSS)
    $("f-seller").textContent = data.seller_name ?? "—";
    $("f-vat-number").textContent = data.vat_number ?? "—";
    $("f-date").textContent = formatDate(data.issued_at);
    $("f-vat").textContent = formatMoney(data.vat_amount);
    $("f-total").textContent = formatMoney(data.total);
  }
  showCard("result-card");
}

function showError(key) {
  lastErrorKey = key;
  $("error-message").textContent = t(key);
  showCard("error-card");
}

// ---------- الرفع ----------
async function uploadInvoice(file) {
  if (!file) return;
  showCard("status-card");

  const form = new FormData();
  form.append("file", file);

  try {
    const response = await fetch("/api/extract", { method: "POST", body: form });
    if (!response.ok) {
      const key = `error${response.status}`;
      showError(key in TRANSLATIONS.ar ? key : "errorUnexpected");
      return;
    }
    renderResult(await response.json());
  } catch {
    showError("errorNetwork");
  }
}

function reset() {
  lastResult = null;
  lastErrorKey = null;
  $("file-input").value = "";
  $("camera-input").value = "";
  showCard("upload-card");
}

// ---------- ربط الأحداث ----------
$("lang-toggle").addEventListener("click", () => applyLanguage(language === "ar" ? "en" : "ar"));
$("file-input").addEventListener("change", (e) => uploadInvoice(e.target.files[0]));
$("camera-input").addEventListener("change", (e) => uploadInvoice(e.target.files[0]));
$("camera-btn").addEventListener("click", () => $("camera-input").click());
$("reset-btn").addEventListener("click", reset);
$("error-reset-btn").addEventListener("click", reset);

// السحب والإفلات (على اللابتوب)
const dropzone = $("dropzone");
dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragging");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragging"));
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragging");
  uploadInvoice(e.dataTransfer.files[0]);
});

applyLanguage(language);
