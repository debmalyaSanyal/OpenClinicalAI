from __future__ import annotations

import logging

from pythonjsonlogger import jsonlogger

from core.config import Settings
from core.security import redact_phi


class PHIRedactionFilter(logging.Filter):
    def __init__(self, enabled: bool) -> None:
        super().__init__()
        self.enabled = enabled

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.enabled and isinstance(record.msg, str):
            record.msg = redact_phi(record.msg)
        return True


def configure_logging(settings: Settings) -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    handler.addFilter(PHIRedactionFilter(settings.log_phi))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)
