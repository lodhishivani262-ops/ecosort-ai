"""EcoSort AI - Structured Logging Setup."""

import logging
import sys
from app.core.config import settings


class CleanFormatter(logging.Formatter):
    """Clean, readable log formatter with optional request ID context."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def setup_logging() -> logging.Logger:
    """Configures application-wide logging with uniform output format."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [REQ-%(request_id)s] "
        "%(name)s: %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = CleanFormatter(fmt=log_format, datefmt=date_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers on re-initialization
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    app_logger = logging.getLogger("ecosort")
    app_logger.setLevel(log_level)
    return app_logger


logger = logging.getLogger("ecosort")
