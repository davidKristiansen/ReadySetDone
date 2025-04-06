# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Task sorting utilities for ReadySetDone.

This module provides reusable sorting logic for task lists,
including a default sort key and a convenience sort function.
"""

from datetime import datetime
from typing import Any, Callable

from .types import Id, Task


def default_sort_key(task: Task) -> Any:
    """
    Default sort order:
    - Pinned tasks first
    - Then incomplete before completed
    - Then by creation date (oldest first)
    """
    return (not task.pinned, task.done, task.created or datetime.min)


def sort_tasks(
    tasks: list[Task], key: Callable[[Task], Any] = default_sort_key
) -> list[Task]:
    """Return a sorted copy of the task list."""
    return sorted(tasks, key=key)


def get_task_id_by_index(tasks: list[Task], index: int, key=default_sort_key) -> Id:
    """Return the ID of the task at a given index based on the sorted order."""
    sorted_tasks = sort_tasks(tasks, key=key)
    if not (1 <= index <= len(sorted_tasks)):
        raise IndexError(f"Index {index} is out of range (1..{len(sorted_tasks)})")
    return Id(sorted_tasks[index - 1].id)
