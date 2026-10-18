import io
from datetime import datetime
from decimal import Decimal

import pytest
import segno
from fastapi.testclient import TestClient
from PIL import Image, ImageFilter

from smart_flow.reader import MAX_FILE_SIZE
from smart_flow.web.app import create_app
from smart_flow.zatca import encode_qr

PAYLOAD = encode_qr(
    "متجر الاختبار", "399999999900003", datetime(2026, 10, 15, 9, 0), Decimal("230"), Decimal("30")
)


@pytest.fixture
def client():
    return TestClient(create_app())


def qr_png(content: str) -> bytes:
    buffer = io.BytesIO()
    segno.make_qr(content, error="m").save(buffer, kind="png", scale=8, border=4)
    return buffer.getvalue()


def upload(client, name: str, content: bytes):
    return client.post("/api/extract", files={"file": (name, content)})


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_home_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Flow AI" in response.text


def test_extract_zatca_qr(client):
    response = upload(client, "receipt.png", qr_png(PAYLOAD))
    body = response.json()

    assert response.status_code == 200
    assert body["found"] is True
    assert body["seller_name"] == "متجر الاختبار"
    assert body["total"] == "230.00"  # Decimal يُرسل كنص حتى لا تضيع الدقة
    assert body["issued_at"] == "2026-10-15T09:00:00"


def test_qr_found_in_blurry_phone_photo(client):
    # رمز في صورة كبيرة ومهزوزة قليلًا، مثل صورة جوال حقيقية.
    # الكاشف العادي وحده يفشل هنا بكل الأحجام، لذلك نستخدم كاشفين
    photo = Image.new("L", (4000, 3000), color=235)
    qr = Image.open(io.BytesIO(qr_png(PAYLOAD))).convert("L").resize((800, 800), Image.BILINEAR)
    photo.paste(qr, (1600, 1100))
    photo = photo.filter(ImageFilter.GaussianBlur(3))
    buffer = io.BytesIO()
    photo.save(buffer, format="JPEG", quality=90)

    body = upload(client, "IMG_0001.jpg", buffer.getvalue()).json()
    assert body["found"] is True


def test_image_without_qr(client):
    buffer = io.BytesIO()
    Image.new("RGB", (200, 200), "white").save(buffer, format="PNG")
    body = upload(client, "blank.png", buffer.getvalue()).json()

    assert body["found"] is False
    assert body["seller_name"] is None


def test_unsupported_type(client):
    assert upload(client, "notes.docx", b"x").status_code == 415


def test_file_too_large(client):
    assert upload(client, "big.png", b"0" * (MAX_FILE_SIZE + 1)).status_code == 413


def test_corrupted_pdf(client):
    assert upload(client, "broken.pdf", b"not a pdf").status_code == 422


def test_malicious_filename_is_not_used(client):
    # اسم ملف يحاول الخروج من المجلد المؤقت: نتجاهله ونستخدم الامتداد فقط
    response = upload(client, "../../evil.png", qr_png(PAYLOAD))
    assert response.status_code == 200
