"""إعداد نظام تسجيل الأحداث (Logging) للمشروع كله."""

import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    """يطبع السجلات على الشاشة، ويحفظها في ملف إذا مرّرنا log_file."""
    # شاشة Windows لا تستخدم UTF-8 افتراضيًا، فيفشل طباعة النص العربي بدون هذا السطر
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    # المكتبات الخارجية (مثل pdfminer) تعرض التحذيرات فقط، ومشروعنا يعرض حسب المستوى المختار
    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, handlers=handlers, force=True)
    logging.getLogger("smart_flow").setLevel(level)
