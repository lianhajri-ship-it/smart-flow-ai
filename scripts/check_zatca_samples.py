"""يختبر البرنامج على نماذج هيئة الزكاة الرسمية (ZATCA SDK).

- ملفات XML: نفك رمز QR الموجود داخل الفاتورة، ونقارنه ببيانات الفاتورة نفسها.
- ملفات PDF: نمررها على البرنامج كاملًا (صورة ← بحث عن QR ← فك)، ونقارنها بملف XML الذي له نفس الاسم.

التشغيل: python scripts/check_zatca_samples.py [مجلد النماذج]
"""

import logging
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from smart_flow.extractor import QrExtractor
from smart_flow.models import InvoiceData
from smart_flow.reader import InvoiceReader, ReaderError
from smart_flow.zatca import ZatcaQrError, decode_qr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = PROJECT_ROOT / "data" / "zatca-sdk"

# أسماء النطاقات (Namespaces) في ملفات UBL، نحتاجها للبحث داخل XML
NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}
SUPPLIER = "cac:AccountingSupplierParty/cac:Party"


@dataclass
class Expected:
    """البيانات كما هي مكتوبة في جسم الفاتورة (المرجع الذي نقارن به)."""

    qr_payload: str | None
    seller_name: str | None
    vat_number: str | None
    issued_at: datetime | None
    total: Decimal | None
    vat_amount: Decimal | None


def _text(root: ET.Element, path: str) -> str | None:
    element = root.find(path, NS)
    return element.text.strip() if element is not None and element.text else None


def parse_invoice_xml(path: Path) -> Expected:
    root = ET.parse(path).getroot()

    qr_payload = None
    for reference in root.findall("cac:AdditionalDocumentReference", NS):
        if _text(reference, "cbc:ID") == "QR":
            qr_payload = _text(reference, "cac:Attachment/cbc:EmbeddedDocumentBinaryObject")

    date, time = _text(root, "cbc:IssueDate"), _text(root, "cbc:IssueTime")
    issued_at = datetime.fromisoformat(f"{date}T{time.rstrip('Z')}") if date and time else None

    # قد يوجد أكثر من TaxTotal، ونأخذ الذي بعملة الضريبة (الريال)
    tax_currency = _text(root, "cbc:TaxCurrencyCode") or "SAR"
    vat_amount = None
    for tax_total in root.findall("cac:TaxTotal", NS):
        amount = tax_total.find("cbc:TaxAmount", NS)
        if amount is not None and amount.get("currencyID") == tax_currency:
            vat_amount = Decimal(amount.text)
            break

    # نماذج الهيئة تضع في رمز QR "المبلغ المستحق" وليس "الإجمالي شامل الضريبة".
    # يختلفان عند وجود دفعة مقدمة (PrepaidAmount) أو تقريب (PayableRoundingAmount)
    total = _text(root, "cac:LegalMonetaryTotal/cbc:PayableAmount")
    return Expected(
        qr_payload=qr_payload,
        seller_name=_text(root, f"{SUPPLIER}/cac:PartyLegalEntity/cbc:RegistrationName"),
        vat_number=_text(root, f"{SUPPLIER}/cac:PartyTaxScheme/cbc:CompanyID"),
        issued_at=issued_at,
        total=Decimal(total) if total else None,
        vat_amount=vat_amount,
    )


def compare(data: InvoiceData, expected: Expected) -> list[str]:
    """يُرجع قائمة بالحقول غير المتطابقة (فارغة = كل شيء صحيح)."""
    issued_at = data.issued_at.replace(tzinfo=None) if data.issued_at else None
    checks = {
        "seller": (data.seller_name, expected.seller_name),
        "vat_number": (data.vat_number, expected.vat_number),
        "date": (issued_at, expected.issued_at),
        "total": (data.total, expected.total),
        "vat": (data.vat_amount, expected.vat_amount),
    }
    return [
        f"{field}: QR={got!r} invoice={want!r}"
        for field, (got, want) in checks.items()
        if got != want
    ]


def check_xml(path: Path) -> list[str]:
    expected = parse_invoice_xml(path)
    if expected.qr_payload is None:
        return ["no QR element in XML"]
    try:
        return compare(decode_qr(expected.qr_payload), expected)
    except ZatcaQrError as exc:
        return [f"decode failed: {exc}"]


def check_pdf(path: Path, reader: InvoiceReader, extractor: QrExtractor) -> list[str]:
    try:
        data = extractor.extract(reader.read(path))
    except ReaderError as exc:
        return [f"read failed: {exc}"]
    if data is None:
        return ["no ZATCA QR found in PDF"]

    # نبحث عن ملف XML بنفس الاسم في نفس نسخة الحزمة لنقارن به
    version_root = path.parents[1]
    matches = list(version_root.rglob(f"{path.stem}.xml"))
    if not matches:
        return []  # قرأنا الرمز بنجاح لكن لا يوجد XML نقارن به
    return compare(data, parse_invoice_xml(matches[0]))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.ERROR)

    samples = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLES
    if not samples.is_dir():
        print(f"Samples folder not found: {samples}")
        return 1

    reader, extractor = InvoiceReader(), QrExtractor()
    files = sorted(p for p in samples.rglob("*") if p.suffix.lower() in {".xml", ".pdf"})
    failures = 0

    for path in files:
        if path.suffix.lower() == ".xml":
            problems = check_xml(path)
        else:
            problems = check_pdf(path, reader, extractor)
        status = "✅" if not problems else "❌"
        failures += bool(problems)
        print(f"{status} {path.relative_to(samples)}")
        for problem in problems:
            print(f"     - {problem}")

    print(f"\nTotal: {len(files)} | Passed: {len(files) - failures} | Failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
