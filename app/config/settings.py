"""Backward-compatible settings module.

Legacy code imported ``get_settings`` from ``app.config.settings``. It now
re-exports the canonical configuration located in ``app.core.config``.
"""
from app.core.config import Settings, get_settings  # noqa: F401
