"""استخراج بيانات الفاتورة بعدة طرق مرتّبة من الأدق والأرخص إلى الأبطأ."""

import logging
from typing import Protocol

from smart_flow import zatca
from smart_flow.models import InvoiceData
from smart_flow.qr import QrScanError, find_qr_codes
from smart_flow.reader import Document

logger = logging.getLogger(__name__)


class Extractor(Protocol):
    """أي كلاس فيه name ودالة extract بهذا الشكل يُعتبر Extractor، حتى لو لم يرث منه."""

    name: str

    def extract(self, document: Document) -> InvoiceData | None:
        """يُرجع البيانات، أو None إذا لم يستطع قراءة هذه الفاتورة."""
        ...


class QrExtractor:
    name = "zatca_qr"

    def extract(self, document: Document) -> InvoiceData | None:
        try:
            payloads = find_qr_codes(document.path, document.media_type)
        except QrScanError as exc:
            logger.warning("%s", exc)
            return None

        # قد تحتوي الفاتورة على أكثر من رمز (مثلًا رمز للدفع)، فنأخذ أول رمز ZATCA صحيح
        for payload in payloads:
            try:
                return zatca.decode_qr(payload)
            except zatca.ZatcaQrError as exc:
                logger.debug("QR in '%s' is not a ZATCA code: %s", document.path.name, exc)
        return None


class ExtractionPipeline:
    def __init__(self, extractors: list[Extractor]) -> None:
        self._extractors = extractors

    def run(self, document: Document) -> InvoiceData | None:
        for extractor in self._extractors:
            data = extractor.extract(document)
            if data is not None:
                logger.info("Extracted '%s' using %s", document.path.name, extractor.name)
                return data
        logger.warning("No extractor could read '%s'", document.path.name)
        return None
