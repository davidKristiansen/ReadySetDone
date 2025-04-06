# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Rich CLI renderer for ReadySetDone.
"""

from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.text import Text

from rsd import __version__
from rsd.api.sorting import default_sort_key, sort_tasks
from rsd.api.types import Task
from rsd.ui.ui import UI


class RichCli(UI):
    def __init__(self):
        self.console = Console()

    def render(self, tasks: list[Task], color: bool, metadata: bool = False):
        """Render a list of tasks using Rich formatting."""
        sorted_tasks = sort_tasks(tasks, key=default_sort_key)

        # Header: Title + version
        header = Text.assemble(
            ("ReadySetDone ", "bold" if color else ""),
            (f"v{__version__}", "dim" if color else ""),
        )
        self.console.print(header, justify="left")

        table = Table.grid(padding=(0, 1))
        table.add_column(
            "#", style="dim" if color else "", justify="right", no_wrap=True
        )
        table.add_column(" ", justify="center", no_wrap=True)
        table.add_column("Task")

        if metadata:
            table.add_column(
                "Created", style="dim" if color else "", justify="right", no_wrap=True
            )

        for index, task in enumerate(sorted_tasks, start=1):
            name = Text(task.task)
            if color and task.pinned:
                name.stylize("bold")

            checkbox = "✔" if task.done else ""
            created = (
                task.created.strftime("%b %d %Y %H:%M")
                if isinstance(task.created, datetime)
                else ""
            )

            row = [str(index), checkbox, name]
            if metadata:
                row.append(created)

            table.add_row(*row)

        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")
