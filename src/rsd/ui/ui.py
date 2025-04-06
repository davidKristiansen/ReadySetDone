# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
UI interface for both CLI and TUI modes in ReadySetDone.
"""

from abc import ABC, abstractmethod
from typing import Any


class UI(ABC):
    @abstractmethod
    def render(self, data: Any) -> None:
        """Render UI output based on the data provided."""
        pass
