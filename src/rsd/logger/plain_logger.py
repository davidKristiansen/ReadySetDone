# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Plain (standard) logger setup for ReadySetDone.
Formats output using standard Python logging without Rich features.
"""

import logging

from .utils import COLOR_MAP, LEVEL_MAP, Color


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level_abbr = LEVEL_MAP.get(record.levelname, record.levelname[:3])
        level_color = COLOR_MAP.get(record.levelname, "")
        gray = Color.GRAY
        reset = Color.RESET

        formatted = (
            f"{gray}{self.formatTime(record, self.datefmt)}{reset} "
            f"{level_color}[{level_abbr}]{reset} "
            f"{gray}{record.name}:{reset} "
            f"{record.getMessage()}"
        )
        return formatted


def setup_logger(color: bool = False, level: str = "info") -> None:
    """
    Configure the plain logger using Python's logging module.

    Args:
        color: Enable or disable ANSI color output
        level: Log level as a string (e.g., 'debug', 'info').
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    # Clear any existing handlers to ensure we control formatting
    root_logger.handlers.clear()

    if color:
        formatter = ColorFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
