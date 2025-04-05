# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Handles the loading and saving of task metadata in JSON format using anyio and file locking.
"""

import json
from typing import List, Optional
from rsd.api.types import Task
from pathlib import Path
from rsd.fs.locked_file import LockedFile


class TaskStore:
    def __init__(self, filepath: str = "tasks.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.locked_file = LockedFile(self.filepath)

    async def load_all(self) -> List[Task]:
        """Load all tasks from the JSON file."""
        try:
            tasks_data = await self.locked_file.read()
            tasks = json.loads(tasks_data)
            return [Task(**task) for task in tasks]
        except FileNotFoundError:
            return []

    async def load(self, task_id: str) -> Optional[Task]:
        """Load a single task by ID."""
        tasks = await self.load_all()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    async def save(self, task: Task) -> None:
        """Save a task to the JSON file."""
        tasks = await self.load_all()
        for i, existing_task in enumerate(tasks):
            if existing_task.id == task.id:
                tasks[i] = task
                break
        else:
            tasks.append(task)

        await self.locked_file.write(json.dumps([t.__dict__ for t in tasks], default=str, indent=4))

    async def delete(self, task_id: str) -> None:
        """Delete a task by ID."""
        tasks = await self.load_all()
        tasks = [task for task in tasks if task.id != task_id]
        await self.locked_file.write(json.dumps([t.__dict__ for t in tasks], default=str, indent=4))
