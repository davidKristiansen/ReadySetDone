# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Logging abstraction for ReadySetDone.

This module defines the logger factory and exposes the interface for use across the project.
"""

from typing import Literal

from .plain_logger import setup_logger as setup_plain_logger
from .rich_logger import setup_logger as setup_rich_logger

LogLevel = Literal["debug", "info", "warn", "error", "critical"]


def setup_logger(
    type: str = "plain", level: LogLevel = "info", color: bool = False
) -> None:
    """Return the appropriate logger implementation based on configuration."""
    match type.lower():
        case "plain":
            return setup_plain_logger(color=color, level=level)
        case "rich":
            return setup_rich_logger(color=color, level=level)
        case _:
            raise ValueError(f"Unknown logger type: {type!r}")


__all__ = ["setup_logger"]
