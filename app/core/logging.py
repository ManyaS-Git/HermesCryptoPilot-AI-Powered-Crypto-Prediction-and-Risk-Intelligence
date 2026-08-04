"""Structured JSON logging with optional Sentry integration."""
import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_info") and isinstance(record.extra_info, dict):
            entry.update(record.extra_info)
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def setup_telemetry(name: str) -> logging.Logger:
    """Configure a logger emitting structured JSON to stdout."""
    settings = get_settings()
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def init_sentry() -> None:
    """Initialise Sentry error tracking if a DSN is configured."""
    settings = get_settings()
    if not settings.SENTRY_DSN:
        return
    try:
        import sentry_sdk  # type: ignore

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=0.2,
        )
    except ImportError:
        pass
