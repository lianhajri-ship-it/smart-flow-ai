import io
from datetime import datetime
from decimal import Decimal

import segno
from fpdf import FPDF

from smart_flow.extractor import ExtractionPipeline, QrExtractor
from smart_flow.models import InvoiceData
from smart_flow.reader import InvoiceReader
from smart_flow.zatca import encode_qr

PAYLOAD = encode_qr(
    "Test Store", "300123456700003", datetime(2026, 10, 15), Decimal("115"), Decimal("15")
)


def qr_png(content: str) -> bytes:
    buffer = io.BytesIO()
    segno.make_qr(content, error="m").save(buffer, kind="png", scale=8, border=4)
    return buffer.getvalue()


def make_pdf_with_qr(path, content: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Simplified Tax Invoice")
    pdf.image(io.BytesIO(qr_png(content)), x=20, y=40, w=45)
    pdf.output(str(path))
    return path


def test_qr_extractor_reads_png(tmp_path):
    path = tmp_path / "receipt.png"
    path.write_bytes(qr_png(PAYLOAD))
    data = QrExtractor().extract(InvoiceReader().read(path))

    assert data is not None
    assert data.seller_name == "Test Store"
    assert data.total == Decimal("115.00")


def test_qr_extractor_reads_pdf(tmp_path):
    path = make_pdf_with_qr(tmp_path / "invoice.pdf", PAYLOAD)
    data = QrExtractor().extract(InvoiceReader().read(path))

    assert data is not None
    assert data.vat_number == "300123456700003"


def test_non_zatca_qr_is_skipped(tmp_path):
    path = tmp_path / "menu.png"
    path.write_bytes(qr_png("https://example.com/menu"))
    assert QrExtractor().extract(InvoiceReader().read(path)) is None


def test_corrupted_image_returns_none(tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"not an image")
    assert QrExtractor().extract(InvoiceReader().read(path)) is None


class FakeExtractor:
    """Extractor وهمي لاختبار ترتيب الطبقات بدون ملفات حقيقية."""

    def __init__(self, name, result):
        self.name = name
        self.result = result
        self.called = False

    def extract(self, document):
        self.called = True
        return self.result


def test_pipeline_stops_at_first_success(tmp_path):
    path = tmp_path / "x.png"
    path.write_bytes(b"x")
    document = InvoiceReader().read(path)
    result = InvoiceData(None, None, None, None, None, source="second")

    first = FakeExtractor("first", None)
    second = FakeExtractor("second", result)
    third = FakeExtractor("third", result)

    assert ExtractionPipeline([first, second, third]).run(document) is result
    assert first.called and second.called
    assert not third.called


def test_pipeline_returns_none_when_all_fail(tmp_path):
    path = tmp_path / "x.png"
    path.write_bytes(b"x")
    document = InvoiceReader().read(path)
    assert ExtractionPipeline([FakeExtractor("a", None)]).run(document) is None
