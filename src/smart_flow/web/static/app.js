// منطق الصفحة: رفع الفاتورة إلى /api/extract وعرض النتيجة

const $ = (id) => document.getElementById(id);
const CARDS = ["upload-card", "status-card", "result-card", "error-card"];

// رسائل عربية واضحة حسب رمز الخطأ الذي يرجعه الخادم
const ERROR_MESSAGES = {
  413: "حجم الملف أكبر من 10MB.",
  415: "نوع الملف غير مدعوم. استخدم PDF أو صورة (JPG أو PNG أو WEBP).",
  422: "تعذّرت قراءة الملف. تأكد أنه غير تالف.",
};

function showCard(id) {
  for (const card of CARDS) $(card).classList.toggle("hidden", card !== id);
}

function formatMoney(value) {
  if (value == null) return "—";
  const number = Number(value).toLocaleString("en-US", { minimumFractionDigits: 2 });
  return `${number} ر.س`;
}

function formatDate(value) {
  return value ? value.replace("T", "  ").slice(0, 17) : "—";
}

function renderResult(data) {
  const badge = $("result-badge");
  badge.textContent = data.found ? "✓ تمت قراءة الفاتورة" : "لم نجد رمز QR";
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

function showError(message) {
  $("error-message").textContent = message;
  showCard("error-card");
}

async function uploadInvoice(file) {
  if (!file) return;
  showCard("status-card");

  const form = new FormData();
  form.append("file", file);

  try {
    const response = await fetch("/api/extract", { method: "POST", body: form });
    if (!response.ok) {
      showError(ERROR_MESSAGES[response.status] ?? "حدث خطأ غير متوقع، حاول مرة أخرى.");
      return;
    }
    renderResult(await response.json());
  } catch {
    showError("تعذّر الاتصال بالخادم. تأكد أن الموقع يعمل.");
  }
}

function reset() {
  $("file-input").value = "";
  $("camera-input").value = "";
  showCard("upload-card");
}

// --- ربط الأحداث ---
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
