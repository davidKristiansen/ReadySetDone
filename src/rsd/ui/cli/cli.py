# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
CLI subset interface and dispatcher for ReadySetDone.
"""

from rsd.ui.ui import UI

from .plain_cli import PlainCli
from .rich_cli import RichCli


class CliUI:
    def __new__(cls, ui_type: str = "plain") -> UI:
        if ui_type == "plain":
            return PlainCli()
        elif ui_type == "rich":
            return RichCli()
        raise ValueError(f"Unknown CLI UI type: {ui_type}")
