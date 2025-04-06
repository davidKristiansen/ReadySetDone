# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
TUI subset interface and dispatcher for ReadySetDone.
"""

from .textual_tui import TextualTui
from rsd.ui.ui import UI


class TuiUI:
    def __new__(cls, ui_type: str = "textual") -> UI:
        if ui_type == "textual":
            return TextualTui()
        raise ValueError(f"Unknown TUI UI type: {ui_type}")
