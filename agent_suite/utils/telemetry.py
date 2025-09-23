"""Telemetry hooks for integrating observability providers."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

logger = logging.getLogger("agent_suite")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging handlers if not already configured."""

    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@contextmanager
def span(name: str) -> Iterator[None]:
    """Minimal span context manager that logs entry and exit."""

    logger.debug("Starting span %s", name)
    try:
        yield
    finally:
        logger.debug("Ending span %s", name)


__all__ = ["configure_logging", "span", "logger"]
