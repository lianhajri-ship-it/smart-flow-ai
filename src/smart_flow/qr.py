"""البحث عن رموز QR داخل الصور وصفحات PDF."""

from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium
from PIL import Image

PDF_RENDER_SCALE = 3  # 72 DPI × 3 = 216 DPI، دقة كافية لقراءة الرموز الصغيرة


class QrScanError(Exception):
    """تعذّر فتح الملف لفحصه."""


def find_qr_codes(path: Path, media_type: str) -> list[str]:
    """يُرجع محتوى كل رموز QR الموجودة في الملف، بالترتيب من الصفحة الأولى."""
    # كاشف Aruco أقوى مع الصور المهزوزة، والكاشف العادي ينجح أحيانًا حيث يفشل الأول
    detectors = (cv2.QRCodeDetectorAruco(), cv2.QRCodeDetector())
    payloads: list[str] = []
    try:
        for image in _load_images(path, media_type):
            payloads.extend(_decode(detectors, image))
    except (OSError, pdfium.PdfiumError) as exc:
        raise QrScanError(f"Cannot scan '{path.name}' for QR codes: {exc}") from exc
    return payloads


def _load_images(path: Path, media_type: str) -> Iterator[Image.Image]:
    """نستخدم yield حتى لا نحوّل كل صفحات PDF إلى صور في الذاكرة دفعة واحدة."""
    if media_type != "application/pdf":
        with Image.open(path) as image:
            yield image
        return

    pdf = pdfium.PdfDocument(path)
    try:
        for page in pdf:
            yield page.render(scale=PDF_RENDER_SCALE).to_pil()
    finally:
        pdf.close()


def _decode(detectors: tuple, image: Image.Image) -> list[str]:
    gray = np.array(image.convert("L"))  # الرمادي يكفي لقراءة QR وأسرع من الألوان
    for candidate in _sizes_to_try(gray):
        for detector in detectors:
            found, payloads, _, _ = detector.detectAndDecodeMulti(candidate)
            results = [payload for payload in payloads if payload] if found else []
            if results:
                return results
    return []


def _sizes_to_try(gray: np.ndarray) -> Iterator[np.ndarray]:
    """صور الجوال كبيرة جدًا (مثل 4000×3000) وأحيانًا يفشل الكشف فيها، فنجرّب نسخًا أصغر."""
    yield gray
    longest = max(gray.shape)
    for target in (1600, 1000):
        if longest > target:
            scale = target / longest
            yield cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
