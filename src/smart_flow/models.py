"""نماذج البيانات المشتركة بين أجزاء المشروع."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class InvoiceData:
    """بيانات الفاتورة المستخرجة، بغض النظر عن الطريقة (QR أو Regex أو ذكاء اصطناعي)."""

    seller_name: str | None
    vat_number: str | None
    issued_at: datetime | None
    total: Decimal | None       # الإجمالي شامل الضريبة
    vat_amount: Decimal | None  # مبلغ ضريبة القيمة المضافة
    source: str                 # الطريقة التي استُخرجت بها البيانات
