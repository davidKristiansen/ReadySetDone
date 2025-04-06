# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Factory module for selecting and initializing the appropriate UI backend.
"""

from .cli.cli import CliUI
from .tui.tui import TuiUI
from .ui import UI


def get_ui(mode: str = "cli", ui_type: str = "plain"):
    if mode == "cli":
        return CliUI(ui_type)
    elif mode == "tui":
        return TuiUI(ui_type)
    raise ValueError(f"Unknown mode: {mode}")


__all__ = ["UI"]
