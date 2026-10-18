"""ينشئ فاتورة PDF عربية تجريبية فيها رمز QR حسب صيغة ZATCA، داخل مجلد data/inbox.

التشغيل: python scripts/make_sample_invoice.py
"""

import io
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import segno
from fpdf import FPDF

from smart_flow.zatca import encode_qr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "data" / "inbox" / "sample_invoice.pdf"
FONT = Path("C:/Windows/Fonts/arial.ttf")  # خط يدعم العربية

# بيانات وهمية: اسم متجر غير حقيقي، ورقم ضريبي بصيغة الأرقام التجريبية في نماذج الهيئة
SELLER = "متجر سمارت فلو التجريبي"
VAT_NUMBER = "399999999900003"
ISSUED_AT = datetime(2026, 10, 15, 14, 30)
SUBTOTAL = Decimal("1000.00")
VAT = SUBTOTAL * Decimal("0.15")
TOTAL = SUBTOTAL + VAT

LINES = [
    "فاتورة ضريبية مبسطة",
    f"المورد: {SELLER}",
    f"الرقم الضريبي: {VAT_NUMBER}",
    "رقم الفاتورة: INV-2026-0042",
    f"التاريخ: {ISSUED_AT:%Y-%m-%d}",
    f"المبلغ قبل الضريبة: {SUBTOTAL:.2f} ريال",
    f"ضريبة القيمة المضافة 15%: {VAT:.2f} ريال",
    f"الإجمالي: {TOTAL:.2f} ريال",
]


def make_qr_png() -> io.BytesIO:
    payload = encode_qr(SELLER, VAT_NUMBER, ISSUED_AT, TOTAL, VAT)
    buffer = io.BytesIO()
    # make_qr وليس make: الثانية قد تنتج Micro QR الذي لا تقرؤه OpenCV
    segno.make_qr(payload, error="m").save(buffer, kind="png", scale=8, border=4)
    buffer.seek(0)
    return buffer


def main() -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", fname=str(FONT))
    pdf.set_font("Arial", size=14)
    pdf.set_text_shaping(True)  # يربط الحروف العربية ويكتبها من اليمين لليسار

    for line in LINES:
        pdf.cell(0, 10, line, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.image(make_qr_png(), x=pdf.l_margin, y=pdf.get_y() + 10, w=45)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
