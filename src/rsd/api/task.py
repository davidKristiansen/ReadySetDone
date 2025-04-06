# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
API for task operations in ReadySetDone.
Provides a clean interface to mutate or query tasks using
TaskStore and DescriptionStore.
"""

from typing import List, Optional

from rsd.api.types import Id, Task
from rsd.service.store.description_store import DescriptionStore
from rsd.service.store.task_store import TaskStore

task_store = TaskStore(filepath="tasks.json")
description_store = DescriptionStore(folderpath="descriptions")


async def list_tasks() -> List[Task]:
    """Return a list of all tasks."""
    return await task_store.load_all()


async def get_task(task_id: Id) -> Optional[Task]:
    """Return a single task by ID."""
    return await task_store.load(task_id.id)


async def add_task(task: Task) -> None:
    """Add a new task to the system."""
    await task_store.save(task)


async def update_task(task: Task) -> None:
    """Update an existing task."""
    await task_store.save(task)


async def delete_task(task_id: Id) -> None:
    """Delete a task by ID."""
    await task_store.delete(task_id.id)


async def mark_done(task_id: Id) -> None:
    """Mark the task as done."""
    task = await get_task(task_id)
    if task and not task.done:
        task.done = True
        task.completed = task.completed or task.created
        await update_task(task)


async def mark_not_done(task_id: Id) -> None:
    """Mark the task as not done."""
    task = await get_task(task_id)
    if task and task.done:
        task.done = False
        task.completed = None
        await update_task(task)


async def toggle_task(task_id: Id) -> None:
    """Toggle the task's done state."""
    task = await get_task(task_id)
    if task:
        task.done = not task.done
        task.completed = task.completed or task.created if task.done else None
        await update_task(task)


async def pin_task(task_id: Id) -> None:
    """Pin the task."""
    task = await get_task(task_id)
    if task and not task.pinned:
        task.pinned = True
        await update_task(task)


async def unpin_task(task_id: Id) -> None:
    """Unpin the task."""
    task = await get_task(task_id)
    if task and task.pinned:
        task.pinned = False
        await update_task(task)


async def get_description(task_id: Id) -> Optional[str]:
    """Get the full Markdown description for a task."""
    return await description_store.load_description(task_id.id)


async def set_description(task_id: Id, description: str) -> None:
    """Set the Markdown description for a task."""
    await description_store.save_description(task_id.id, description)
