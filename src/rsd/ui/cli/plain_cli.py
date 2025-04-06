# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Plain CLI renderer for ReadySetDone.
"""

from rsd.ui.ui import UI


class PlainCli(UI):
    def render(self, data):
        for item in data:
            print(f"- {item}")
