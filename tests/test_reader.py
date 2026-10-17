import pytest
from fpdf import FPDF

from smart_flow.reader import (
    InvoiceReader,
    ReaderError,
    UnsupportedFileError,
    clean_text,
    fix_arabic_line,
)


def make_pdf(path, lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in lines:
        pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))
    return path


# --- معالجة النص ---

def test_fix_arabic_line_reverses_visual_order():
    assert fix_arabic_line("ةروتاف") == "فاتورة"


def test_fix_arabic_line_keeps_mixed_line_in_right_order():
    assert fix_arabic_line("INV-0042 :ةروتافلا مقر") == "رقم الفاتورة: INV-0042"


def test_fix_arabic_line_leaves_english_untouched():
    assert fix_arabic_line("Total: 100") == "Total: 100"


def test_clean_text_normalizes_presentation_forms():
    # "ﻣﺤﻤﺪ" مكتوبة بأشكال الحروف المتصلة، وبترتيب العرض المعكوس
    assert clean_text("ﻣﺤﻤﺪ"[::-1]) == "محمد"


def test_clean_text_collapses_whitespace():
    assert clean_text("a    b\n\n\n\n\nc") == "a b\n\nc"


# --- القراءة ---

def test_read_pdf(tmp_path):
    path = make_pdf(tmp_path / "invoice.pdf", ["Invoice INV-001", "Total: 1150.00 SAR"])
    doc = InvoiceReader().read(path)

    assert doc.media_type == "application/pdf"
    assert doc.page_count == 1
    assert "INV-001" in doc.text
    assert doc.has_text
    assert len(doc.sha256) == 64


def test_pdf_without_text_has_no_text(tmp_path):
    path = make_pdf(tmp_path / "scanned.pdf", [])
    assert not InvoiceReader().read(path).has_text


def test_image_is_accepted_without_text(tmp_path):
    path = tmp_path / "receipt.JPG"  # امتداد بحروف كبيرة
    path.write_bytes(b"fake image bytes")
    doc = InvoiceReader().read(path)

    assert doc.media_type == "image/jpeg"
    assert doc.text == ""


def test_same_content_gives_same_hash(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a.write_bytes(b"same")
    b.write_bytes(b"same")
    reader = InvoiceReader()
    assert reader.read(a).sha256 == reader.read(b).sha256


def test_unsupported_extension(tmp_path):
    path = tmp_path / "notes.docx"
    path.write_bytes(b"x")
    with pytest.raises(UnsupportedFileError):
        InvoiceReader().read(path)


def test_missing_file(tmp_path):
    with pytest.raises(ReaderError, match="not found"):
        InvoiceReader().read(tmp_path / "nope.pdf")


def test_empty_file(tmp_path):
    path = tmp_path / "empty.pdf"
    path.touch()
    with pytest.raises(ReaderError, match="empty"):
        InvoiceReader().read(path)


def test_corrupted_pdf(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"this is not a pdf")
    with pytest.raises(ReaderError, match="Cannot read PDF"):
        InvoiceReader().read(path)
