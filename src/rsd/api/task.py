# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
API for task operations in ReadySetDone.
"""

from typing import List, Optional

from rsd.api.types import Task
from rsd.service.store.description_store import DescriptionStore
from rsd.service.store.task_store import TaskStore
from rsd.service.task_service import TaskService

task_store = TaskStore(filepath="tasks.json")
description_store = DescriptionStore(folderpath="descriptions")
task_service = TaskService(task_store)


async def list() -> List[Task]:
    """Return a list of all tasks."""
    return await task_store.load_all()


async def get(task_id: str) -> Optional[Task]:
    """Return a single task by ID."""
    return await task_store.load(task_id)


async def add(task: Task) -> None:
    """Add a new task to the system."""
    await task_service.add_task(task)


async def update(task: Task) -> None:
    """Update an existing task."""
    await task_store.save(task)


async def delete(task_id: str) -> None:
    """Delete a task by ID."""
    await task_store.delete(task_id)


async def mark_done(task_id: str) -> None:
    """Mark the task as done."""
    task = await get(task_id)
    if task and not task.done:
        task.done = True
        task.completed = task.completed or task.created
        await update(task)


async def mark_not_done(task_id: str) -> None:
    """Mark the task as not done."""
    task = await get(task_id)
    if task and task.done:
        task.done = False
        task.completed = None
        await update(task)


async def toggle(task_id: str) -> None:
    """Toggle the task's done state."""
    task = await get(task_id)
    if task:
        task.done = not task.done
        task.completed = task.completed or task.created if task.done else None
        await update(task)


async def pin(task_id: str) -> None:
    """Pin the task."""
    task = await get(task_id)
    if task and not task.pinned:
        task.pinned = True
        await update(task)


async def unpin(task_id: str) -> None:
    """Unpin the task."""
    task = await get(task_id)
    if task and task.pinned:
        task.pinned = False
        await update(task)


async def get_description(task_id: str) -> Optional[str]:
    """Get the full Markdown description for a task."""
    return await description_store.load_description(task_id)


async def set_description(task_id: str, description: str) -> None:
    """Set the Markdown description for a task."""
    await description_store.save_description(task_id, description)
