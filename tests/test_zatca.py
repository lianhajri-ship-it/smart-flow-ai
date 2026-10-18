import base64
from datetime import datetime
from decimal import Decimal

import pytest

from smart_flow.zatca import ZatcaQrError, decode_qr, encode_qr, parse_tlv

SELLER = "متجر سمارت فلو التجريبي"


def sample_payload() -> str:
    return encode_qr(
        SELLER, "399999999900003", datetime(2026, 10, 15, 14, 30), Decimal("1150"), Decimal("150")
    )


def test_roundtrip_with_arabic_seller():
    data = decode_qr(sample_payload())

    assert data.seller_name == SELLER
    assert data.vat_number == "399999999900003"
    assert data.issued_at == datetime(2026, 10, 15, 14, 30)
    assert data.total == Decimal("1150.00")
    assert data.vat_amount == Decimal("150.00")
    assert data.source == "zatca_qr"


def test_length_is_counted_in_bytes_not_characters():
    raw = base64.b64decode(encode_qr("أ", "3", datetime(2026, 1, 1), Decimal(1), Decimal(0)))
    assert raw[:4] == bytes([1, 2]) + "أ".encode("utf-8")  # حرف واحد = 2 بايت


def test_timestamp_with_z_suffix():
    # بعض الأنظمة تكتب الوقت بتوقيت UTC وتنهيه بحرف Z
    raw = base64.b64decode(sample_payload())
    fields = parse_tlv(raw)
    fields[3] = b"2026-10-15T14:30:00Z"
    rebuilt = b"".join(bytes([tag, len(value)]) + value for tag, value in fields.items())

    issued_at = decode_qr(base64.b64encode(rebuilt).decode()).issued_at
    assert issued_at is not None and issued_at.tzinfo is not None


def test_unknown_tags_are_ignored():
    extra = bytes([6, 3]) + b"abc"  # حقل من المرحلة الثانية
    payload = base64.b64encode(base64.b64decode(sample_payload()) + extra).decode()
    assert decode_qr(payload).seller_name == SELLER


def test_invalid_base64():
    with pytest.raises(ZatcaQrError, match="Base64"):
        decode_qr("https://example.com/pay")


def test_truncated_data():
    raw = base64.b64decode(sample_payload())[:-3]
    with pytest.raises(ZatcaQrError, match="Truncated"):
        decode_qr(base64.b64encode(raw).decode())


def test_missing_fields():
    only_seller = bytes([1, 4]) + b"Test"
    with pytest.raises(ZatcaQrError, match="Missing"):
        decode_qr(base64.b64encode(only_seller).decode())


def test_bad_amount_becomes_none():
    raw = bytearray()
    for tag, value in [(1, b"S"), (2, b"3"), (3, b"not-a-date"), (4, b"abc"), (5, b"15")]:
        raw += bytes([tag, len(value)]) + value
    data = decode_qr(base64.b64encode(bytes(raw)).decode())

    assert data.total is None
    assert data.issued_at is None
    assert data.vat_amount == Decimal("15")


def test_value_too_long_for_one_byte_length():
    with pytest.raises(ZatcaQrError, match="too long"):
        encode_qr("x" * 256, "3", datetime(2026, 1, 1), Decimal(1), Decimal(0))
