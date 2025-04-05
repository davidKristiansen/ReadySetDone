# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Handles the loading and saving of task descriptions in Markdown format using anyio and file locking.
"""

from pathlib import Path
from typing import Optional

from rsd.fs.locked_file import LockedFile


class DescriptionStore:
    def __init__(self, folderpath: str = "descriptions"):
        self.folderpath = Path(folderpath)
        self.folderpath.mkdir(parents=True, exist_ok=True)

    def _get_description_file(self, task_id: str) -> LockedFile:
        return LockedFile(self.folderpath / f"{task_id}.md")

    async def load_description(self, task_id: str) -> Optional[str]:
        """Load the task description from a Markdown file."""
        description_file = self._get_description_file(task_id)
        try:
            return await description_file.read()
        except FileNotFoundError:
            return None

    async def save_description(self, task_id: str, description: str) -> None:
        """Save the task description to a Markdown file."""
        description_file = self._get_description_file(task_id)
        await description_file.write(description)
