"""تشغيل الموقع بالأمر: python -m smart_flow.web"""

import uvicorn

from smart_flow.config import Settings
from smart_flow.logger import setup_logging
from smart_flow.web.app import app

settings = Settings.from_env()
setup_logging(settings.log_level)
uvicorn.run(app, host=settings.host, port=settings.port)
