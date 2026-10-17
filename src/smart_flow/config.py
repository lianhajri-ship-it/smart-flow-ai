"""إعدادات المشروع: تُقرأ من متغيرات البيئة أو من ملف .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# جذر المشروع: src/smart_flow/config.py -> نصعد مستويين
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    inbox_dir: Path       # الفواتير الجديدة توضع هنا
    processed_dir: Path   # الفواتير بعد معالجتها بنجاح
    failed_dir: Path      # الفواتير التي فشلت معالجتها
    logs_dir: Path
    log_level: str
    host: str             # 127.0.0.1 = جهازك فقط، 0.0.0.0 = أي جهاز في نفس الشبكة
    port: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(PROJECT_ROOT / ".env")

        # إذا كان DATA_DIR مسارًا مطلقًا فإن عملية / تتجاهل PROJECT_ROOT
        data_dir = PROJECT_ROOT / os.getenv("DATA_DIR", "data")

        return cls(
            inbox_dir=data_dir / "inbox",
            processed_dir=data_dir / "processed",
            failed_dir=data_dir / "failed",
            logs_dir=PROJECT_ROOT / "logs",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
        )

    def ensure_dirs(self) -> None:
        """إنشاء مجلدات العمل إذا لم تكن موجودة."""
        for directory in (self.inbox_dir, self.processed_dir, self.failed_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)
