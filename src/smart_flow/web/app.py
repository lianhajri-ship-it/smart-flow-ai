"""موقع Smart Flow AI: صفحة ويب و API لاستخراج بيانات الفواتير.

الملف المرفوع يُعالج في مجلد مؤقت ويُحذف فورًا، ولا نحفظ أي فاتورة.
"""

import logging
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from smart_flow import __version__
from smart_flow.extractor import ExtractionPipeline, QrExtractor
from smart_flow.reader import MAX_FILE_SIZE, InvoiceReader, ReaderError

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


class InvoiceResult(BaseModel):
    """شكل الرد الذي يرجعه الـ API. يظهر تلقائيًا في صفحة التوثيق /docs."""

    found: bool
    page_count: int
    source: str | None = None
    seller_name: str | None = None
    vat_number: str | None = None
    issued_at: datetime | None = None
    total: Decimal | None = None
    vat_amount: Decimal | None = None


def create_app(
    reader: InvoiceReader | None = None,
    pipeline: ExtractionPipeline | None = None,
) -> FastAPI:
    """Factory: ننشئ التطبيق داخل دالة حتى نستطيع تمرير مكوّنات مختلفة في الاختبارات."""
    reader = reader or InvoiceReader()
    pipeline = pipeline or ExtractionPipeline([QrExtractor()])

    app = FastAPI(
        title="Smart Flow AI",
        version=__version__,
        description="Extract data from Saudi tax invoices (ZATCA QR codes).",
    )

    @app.get("/api/health", tags=["System"], summary="Check that the service is running")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    # دالة عادية (def) وليست async: قراءة الصور عملية ثقيلة على المعالج،
    # و FastAPI يشغّل الدوال العادية في Thread منفصل فلا يتجمد الخادم
    @app.post(
        "/api/extract",
        response_model=InvoiceResult,
        tags=["Invoices"],
        summary="Extract invoice data from a PDF or image",
        description="Finds the ZATCA QR code in the uploaded invoice and returns its data. "
        "The file is processed in a temporary folder and deleted immediately.",
    )
    def extract(file: UploadFile) -> InvoiceResult:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in reader.supported_extensions:
            raise HTTPException(415, f"Unsupported file type '{suffix}'")

        # نقرأ بايتًا زائدًا عن الحد فقط، حتى لا نحمّل ملفًا ضخمًا كاملًا في الذاكرة
        content = file.file.read(MAX_FILE_SIZE + 1)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(413, "File is larger than 10 MB")

        with tempfile.TemporaryDirectory() as tmp:
            # لا نستخدم اسم الملف الذي أرسله المستخدم، فقد يحتوي على مسار ضار مثل ../../
            path = Path(tmp) / f"upload{suffix}"
            path.write_bytes(content)
            try:
                document = reader.read(path)
            except ReaderError as exc:
                raise HTTPException(422, str(exc)) from exc
            data = pipeline.run(document)

        if data is None:
            return InvoiceResult(found=False, page_count=document.page_count)

        return InvoiceResult(
            found=True,
            page_count=document.page_count,
            source=data.source,
            seller_name=data.seller_name,
            vat_number=data.vat_number,
            issued_at=data.issued_at,
            total=data.total,
            vat_amount=data.vat_amount,
        )

    # الصفحة الرئيسية والملفات الثابتة (HTML و CSS و JS). نضعها آخرًا حتى لا تغطي مسارات /api
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
