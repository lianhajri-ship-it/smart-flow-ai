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
    # المبلغ المستحق شامل الضريبة. يختلف عن "الإجمالي" عند وجود دفعة مقدمة أو تقريب
    total: Decimal | None
    vat_amount: Decimal | None  # مبلغ ضريبة القيمة المضافة
    source: str                 # الطريقة التي استُخرجت بها البيانات
