# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Defines reusable color constants for logging
"""

from enum import StrEnum


class Color(StrEnum):
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[1;31m"
    BRIGHT_GREEN = "\033[1;32m"
    BRIGHT_YELLOW = "\033[1;33m"
    BRIGHT_BLUE = "\033[1;34m"
    BRIGHT_MAGENTA = "\033[1;35m"
    BRIGHT_CYAN = "\033[1;36m"
    BRIGHT_WHITE = "\033[1;37m"

    DEBUG = CYAN
    INFO = GREEN
    WARNING = YELLOW
    ERROR = RED
    CRITICAL = BRIGHT_RED


# Optional mapping for lookups
COLOR_MAP: dict[str, Color] = {
    "DEBUG": Color.DEBUG,
    "INFO": Color.INFO,
    "WARNING": Color.WARNING,
    "ERROR": Color.ERROR,
    "CRITICAL": Color.CRITICAL,
    "GRAY": Color.GRAY,
    "RESET": Color.RESET,
}

# 3-character abbreviation mapping for log levels
LEVEL_MAP: dict[str, str] = {
    "DEBUG": "DBG",
    "INFO": "INF",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "FAT",
}
