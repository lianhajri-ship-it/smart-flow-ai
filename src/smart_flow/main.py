"""نقطة تشغيل البرنامج."""

import logging

from smart_flow import __version__
from smart_flow.config import Settings
from smart_flow.extractor import ExtractionPipeline, QrExtractor
from smart_flow.logger import setup_logging
from smart_flow.reader import InvoiceReader, ReaderError

logger = logging.getLogger(__name__)


def process_inbox(settings: Settings, reader: InvoiceReader, pipeline: ExtractionPipeline) -> None:
    files = sorted(p for p in settings.inbox_dir.iterdir() if p.is_file())
    logger.info("Found %d file(s) in inbox", len(files))

    for path in files:
        try:
            document = reader.read(path)
        except ReaderError as exc:
            logger.error("%s", exc)
            continue
        logger.debug("Text preview of '%s':\n%s", path.name, document.text[:300])

        data = pipeline.run(document)
        if data is not None:
            logger.info(
                "Seller=%s | VAT No=%s | Date=%s | Total=%s | VAT=%s",
                data.seller_name, data.vat_number, data.issued_at, data.total, data.vat_amount,
            )


def main() -> None:
    settings = Settings.from_env()
    setup_logging(settings.log_level, settings.logs_dir / "smart_flow.log")
    settings.ensure_dirs()

    logger.info("Smart Flow AI v%s started", __version__)
    logger.info("Inbox folder: %s", settings.inbox_dir)

    pipeline = ExtractionPipeline([QrExtractor()])
    process_inbox(settings, InvoiceReader(), pipeline)


if __name__ == "__main__":
    main()
