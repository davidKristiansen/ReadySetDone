# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Rich logger setup for ReadySetDone.
Formats output using RichHandler for colorized, structured terminal output.
"""

import logging

from rich.logging import RichHandler


def setup_logger(color: bool = False, level: str = "info") -> None:
    """
    Configure the Rich logger.

    Args:
        color: Whether to use colorized output.
        level: Log level as a string (e.g., 'debug', 'info').
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True, markup=color)],
    )
