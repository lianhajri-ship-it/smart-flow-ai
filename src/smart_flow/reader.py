"""قراءة ملفات الفواتير: التحقق منها، وحساب بصمتها، واستخراج النص منها."""

import hashlib
import logging
import re
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from bidi import get_display

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_TEXT_LENGTH = 20  # أقل من هذا = PDF ممسوح ضوئيًا (صورة بلا نص)
ARABIC_PATTERN = re.compile(r"[؀-ۿ]")


class ReaderError(Exception):
    """خطأ أثناء قراءة ملف فاتورة."""


class UnsupportedFileError(ReaderError):
    """نوع الملف غير مدعوم."""


@dataclass(frozen=True)
class Document:
    path: Path
    media_type: str   # نوع الملف بالصيغة التي يفهمها الـ API مثل application/pdf
    sha256: str       # بصمة المحتوى: نستخدمها لاحقًا لاكتشاف الفواتير المكررة
    page_count: int
    text: str         # نص تقريبي للمعاينة والبحث، وليس المصدر الأساسي للبيانات

    @property
    def has_text(self) -> bool:
        return len(self.text) >= MIN_TEXT_LENGTH


def fix_arabic_line(line: str) -> str:
    """مكتبة pdfplumber تُرجع العربي بترتيب العرض (معكوسًا)، فنعيده للترتيب المنطقي."""
    if not ARABIC_PATTERN.search(line):
        return line
    return get_display(line, base_dir="R")


def clean_text(text: str) -> str:
    # NFKC يحوّل أشكال الحروف المتصلة (مثل ﻣ و ﺤ) إلى حروف عادية (م و ح)
    text = unicodedata.normalize("NFKC", text)
    lines = (fix_arabic_line(line) for line in text.splitlines())
    text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def file_sha256(path: Path) -> str:
    """نقرأ الملف على دفعات صغيرة حتى لا نحمّل الملفات الكبيرة كاملة في الذاكرة."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BaseReader(ABC):
    """كل نوع ملف له قارئ خاص يرث من هذا الكلاس."""

    media_types: dict[str, str] = {}  # الامتداد -> media type

    @abstractmethod
    def extract(self, path: Path) -> tuple[str, int]:
        """يُرجع (النص, عدد الصفحات)."""


class PdfReader(BaseReader):
    media_types = {".pdf": "application/pdf"}

    def extract(self, path: Path) -> tuple[str, int]:
        try:
            with pdfplumber.open(path) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
        except Exception as exc:  # pdfplumber يرمي أنواعًا كثيرة من الأخطاء
            raise ReaderError(f"Cannot read PDF '{path.name}': {exc}") from exc
        return clean_text("\n\n".join(pages)), len(pages)


class ImageReader(BaseReader):
    """لا نستخرج نصًا من الصور محليًا، لأن الذكاء الاصطناعي سيقرأ الصورة مباشرة."""

    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    def extract(self, path: Path) -> tuple[str, int]:
        return "", 1


class InvoiceReader:
    """الواجهة الوحيدة التي يستخدمها باقي المشروع: يختار القارئ المناسب حسب الامتداد."""

    def __init__(self, readers: list[BaseReader] | None = None) -> None:
        readers = readers or [PdfReader(), ImageReader()]
        self._readers = {ext: reader for reader in readers for ext in reader.media_types}

    @property
    def supported_extensions(self) -> set[str]:
        return set(self._readers)

    def read(self, path: Path) -> Document:
        if not path.is_file():
            raise ReaderError(f"File not found: {path}")

        extension = path.suffix.lower()
        reader = self._readers.get(extension)
        if reader is None:
            raise UnsupportedFileError(f"Unsupported file type '{extension}': {path.name}")

        size = path.stat().st_size
        if size == 0:
            raise ReaderError(f"File is empty: {path.name}")
        if size > MAX_FILE_SIZE:
            raise ReaderError(f"File too large ({size / 1024 / 1024:.1f} MB): {path.name}")

        text, page_count = reader.extract(path)
        document = Document(
            path=path,
            media_type=reader.media_types[extension],
            sha256=file_sha256(path),
            page_count=page_count,
            text=text,
        )
        logger.info(
            "Read '%s': %d page(s), %d chars, has_text=%s",
            path.name, page_count, len(text), document.has_text,
        )
        return document
