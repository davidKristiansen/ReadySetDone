# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
TaskService implements the ReadySetDoneAPI.
This is where task business logic lives: validation, mutation, loading, etc.
"""

from typing import List, Optional

from rsd.api.interface import ReadySetDoneAPI
from rsd.api.types import Task


class TaskService(ReadySetDoneAPI):
    def __init__(self, store, pubsub):
        """
        Create a new TaskService.

        Args:
            store: An object that handles persistence (e.g. fs_store)
            pubsub: A pubsub system to notify on changes
        """
        self.store = store
        self.pubsub = pubsub

    async def list_tasks(self) -> List[Task]:
        return await self.store.load_all()

    async def get_task(self, task_id: str) -> Optional[Task]:
        return await self.store.load(task_id)

    async def add_task(self, task: Task) -> None:
        await self.store.save(task)
        await self.pubsub.publish("task-added", task)

    async def update_task(self, task: Task) -> None:
        await self.store.save(task)
        await self.pubsub.publish("task-updated", task)

    async def delete_task(self, task_id: str) -> None:
        await self.store.delete(task_id)
        await self.pubsub.publish("task-deleted", task_id)

    async def mark_done(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        if task and not task.done:
            task.done = True
            task.completed = task.completed or task.created  # or datetime.now()
            await self.update_task(task)

    async def mark_not_done(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        if task and task.done:
            task.done = False
            task.completed = None
            await self.update_task(task)

    async def toggle_done(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        if task:
            task.done = not task.done
            task.completed = task.completed or task.created if task.done else None
            await self.update_task(task)

    async def pin_task(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        if task and not task.pinned:
            task.pinned = True
            await self.update_task(task)

    async def unpin_task(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        if task and task.pinned:
            task.pinned = False
            await self.update_task(task)

    async def rename_task(self, task_id: str, new_name: str) -> None:
        task = await self.get_task(task_id)
        if task:
            task.task = new_name
            await self.update_task(task)

    async def get_description(self, task_id: str) -> Optional[str]:
        return await self.store.load_description(task_id)

    async def set_description(self, task_id: str, description: str) -> None:
        await self.store.save_description(task_id, description)
        await self.pubsub.publish("task-description-updated", task_id)
