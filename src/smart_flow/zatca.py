"""ترميز وفك رمز QR في فواتير هيئة الزكاة والضريبة والجمارك (ZATCA).

محتوى الرمز نص Base64، وبداخله حقول بصيغة TLV:
    [Tag: بايت واحد] [Length: بايت واحد] [Value: نص UTF-8 بطول Length]
"""

import base64
import binascii
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import IntEnum

from smart_flow.models import InvoiceData


class Tag(IntEnum):
    SELLER_NAME = 1
    VAT_NUMBER = 2
    TIMESTAMP = 3
    TOTAL = 4
    VAT_AMOUNT = 5
    # المرحلة الثانية من الفوترة تضيف الحقول 6 إلى 9 (توقيعات رقمية) ولا نحتاجها


class ZatcaQrError(ValueError):
    """محتوى رمز QR ليس بصيغة ZATCA صحيحة."""


def parse_tlv(data: bytes) -> dict[int, bytes]:
    fields: dict[int, bytes] = {}
    position = 0
    while position < len(data):
        if position + 2 > len(data):
            raise ZatcaQrError("Truncated TLV header")
        tag, length = data[position], data[position + 1]
        start = position + 2
        value = data[start:start + length]
        if len(value) != length:
            raise ZatcaQrError(f"Truncated value for tag {tag}")
        fields[tag] = value
        position = start + length
    return fields


def decode_qr(payload: str) -> InvoiceData:
    try:
        raw = base64.b64decode(payload.strip(), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ZatcaQrError("QR payload is not valid Base64") from exc

    fields = parse_tlv(raw)
    missing = [tag.name for tag in Tag if tag not in fields]
    if missing:
        raise ZatcaQrError(f"Missing ZATCA fields: {', '.join(missing)}")

    try:
        values = {tag: fields[tag].decode("utf-8").strip() for tag in Tag}
    except UnicodeDecodeError as exc:
        raise ZatcaQrError("ZATCA field is not valid UTF-8") from exc

    return InvoiceData(
        seller_name=values[Tag.SELLER_NAME],
        vat_number=values[Tag.VAT_NUMBER],
        issued_at=_parse_timestamp(values[Tag.TIMESTAMP]),
        total=_parse_amount(values[Tag.TOTAL]),
        vat_amount=_parse_amount(values[Tag.VAT_AMOUNT]),
        source="zatca_qr",
    )


def encode_qr(
    seller_name: str,
    vat_number: str,
    issued_at: datetime,
    total: Decimal,
    vat_amount: Decimal,
) -> str:
    values = {
        Tag.SELLER_NAME: seller_name,
        Tag.VAT_NUMBER: vat_number,
        Tag.TIMESTAMP: issued_at.isoformat(),
        Tag.TOTAL: f"{total:.2f}",
        Tag.VAT_AMOUNT: f"{vat_amount:.2f}",
    }
    data = bytearray()
    for tag, value in values.items():
        # الطول بعدد البايتات وليس الحروف: الحرف العربي = 2 بايت في UTF-8
        encoded = value.encode("utf-8")
        if len(encoded) > 255:
            raise ZatcaQrError(f"{tag.name} is too long ({len(encoded)} bytes)")
        data += bytes([tag, len(encoded)]) + encoded
    return base64.b64encode(bytes(data)).decode("ascii")


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_amount(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None
