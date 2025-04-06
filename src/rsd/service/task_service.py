# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
TaskService implements the ReadySetDoneAPI.
This is where task business logic lives: validation, mutation, loading, etc.
"""

from pathlib import Path
from typing import List, Optional

from rsd.api.types import Id, Task

from .store import TaskStore


class TaskService:
    def __init__(self, task_store_path: Path):
        """
        Create a new TaskService.

        Args:
            task_store_path (Path): Path to the task store JSON file
        """
        self.store = TaskStore(task_store_path)

    async def list_tasks(self) -> List[Task]:
        """Get a list of all tasks."""
        return await self.store.load_all()

    async def get_task(self, task_id: Id) -> Optional[Task]:
        """Get a single task by ID."""
        return await self.store.load(task_id.id)

    async def add_task(self, task: Task) -> None:
        """Add a new task."""
        await self.store.save(task)

    async def update_task(self, task: Task) -> None:
        """Update an existing task."""
        await self.store.save(task)

    async def delete_task(self, task_id: Id) -> None:
        """Delete a task by ID."""
        await self.store.delete(task_id.id)

    async def mark_done(self, task_id: Id) -> None:
        """Mark a task as done."""
        task = await self.get_task(task_id)
        if task and not task.done:
            task.done = True
            task.completed = task.completed or task.created
            await self.update_task(task)

    async def mark_not_done(self, task_id: Id) -> None:
        """Mark a task as not done."""
        task = await self.get_task(task_id)
        if task and task.done:
            task.done = False
            task.completed = None
            await self.update_task(task)

    async def toggle_done(self, task_id: Id) -> None:
        """Toggle the task's done state."""
        task = await self.get_task(task_id)
        if task:
            task.done = not task.done
            task.completed = task.completed or task.created if task.done else None
            await self.update_task(task)

    async def pin_task(self, task_id: Id) -> None:
        """Pin a task."""
        task = await self.get_task(task_id)
        if task and not task.pinned:
            task.pinned = True
            await self.update_task(task)

    async def unpin_task(self, task_id: Id) -> None:
        """Unpin a task."""
        task = await self.get_task(task_id)
        if task and task.pinned:
            task.pinned = False
            await self.update_task(task)

    async def rename_task(self, task_id: Id, new_name: str) -> None:
        """Rename a task."""
        task = await self.get_task(task_id)
        if task:
            task.task = new_name
            await self.update_task(task)

    async def get_description(self, task_id: Id) -> Optional[str]:
        """Get the description for a task."""
        return await self.store.load_description(task_id.id)

    async def set_description(self, task_id: Id, description: str) -> None:
        """Set the description for a task."""
        await self.store.save_description(task_id.id, description)
