# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Abstract interface for the ReadySetDone API.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from rsd.api.types import Task


class ReadySetDoneAPI(ABC):
    """
    Defines the core operations supported by the ReadySetDone task API.
    Implementations can be local (daemon), remote (D-Bus), or mock.
    """

    @abstractmethod
    async def list_tasks(self) -> List[Task]:
        """Return all tasks in the system."""
        ...

    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Return a single task by ID, or None if not found."""
        ...

    @abstractmethod
    async def add_task(self, task: Task) -> None:
        """Add a new task to the system."""
        ...

    @abstractmethod
    async def update_task(self, task: Task) -> None:
        """Update an existing task."""
        ...

    @abstractmethod
    async def delete_task(self, task_id: str) -> None:
        """Delete a task by ID."""
        ...

    @abstractmethod
    async def mark_done(self, task_id: str) -> None:
        """Mark the task as done."""
        ...

    @abstractmethod
    async def mark_not_done(self, task_id: str) -> None:
        """Mark the task as not done."""
        ...

    @abstractmethod
    async def toggle_done(self, task_id: str) -> None:
        """Toggle the task's done state."""
        ...

    @abstractmethod
    async def pin_task(self, task_id: str) -> None:
        """Pin the task."""
        ...

    @abstractmethod
    async def unpin_task(self, task_id: str) -> None:
        """Unpin the task."""
        ...

    @abstractmethod
    async def rename_task(self, task_id: str, new_name: str) -> None:
        """Rename a task's title."""
        ...

    @abstractmethod
    async def get_description(self, task_id: str) -> Optional[str]:
        """Get the full Markdown description for a task."""
        ...

    @abstractmethod
    async def set_description(self, task_id: str, description: str) -> None:
        """Set the Markdown description for a task."""
        ...
