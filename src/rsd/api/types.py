# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Task model definitions used throughout the ReadySetDone API.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


def slugify(title: str) -> str:
    """Convert task title to a filesystem-friendly slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")


@dataclass
class Task:
    """
    Represents a single task in ReadySetDone.
    """

    id: str
    task: str
    done: bool
    created: datetime
    completed: Optional[datetime] = None
    due: Optional[datetime] = None
    pinned: bool = False
    children: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def new(task: str, due: Optional[datetime] = None, pinned: bool = False) -> "Task":
        """Helper to construct a new Task with auto-generated ID and timestamp."""
        return Task(
            id=str(uuid.uuid4()),
            task=task,
            done=False,
            created=datetime.now(),
            due=due,
            pinned=pinned,
        )

    @property
    def filename(self) -> str:
        slug = slugify(self.task)
        shortid = self.id.split("-")[0]  # or use first 6 chars
        return f"{self.created:%Y-%m-%d}_{slug}-{shortid}.md"
