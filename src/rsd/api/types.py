# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
This module defines the basic data structures used in the ReadySetDone application.

The `Task` class represents a task with attributes such as ID, name, completion status,
due date, and more. The `Id` class represents a unique identifier for each task.

Classes:
- Task: Represents a task in the application.
- Id: Represents the unique identifier of a task.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Task:
    """Represents a Task in the ReadySetDone application."""

    id: str  # ID of the task
    task: str  # Task name
    done: bool = False  # Indicates whether the task is done
    created: Optional[datetime] = None  # Task creation time
    completed: Optional[datetime] = None  # Task completion time
    due: Optional[datetime] = None  # Task due date
    pinned: bool = False  # Indicates whether the task is pinned

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task object from a dictionary."""
        return cls(
            id=data["id"],
            task=data["task"],
            done=data["done"],
            created=datetime.fromisoformat(data["created"]) if data["created"] else None,
            completed=datetime.fromisoformat(data["completed"]) if data["completed"] else None,
            due=datetime.fromisoformat(data["due"]) if data["due"] else None,
            pinned=data["pinned"],
        )

    @classmethod
    def new(cls, task_name: str) -> "Task":
        """Create a new Task with a generated ID and the provided task name."""
        return cls(
            id=str(uuid.uuid4()),  # Generate a new UUID for the task ID
            task=task_name,
            created=datetime.now(),  # Set the current time as the creation time
        )


@dataclass
class Id:
    """Represents a task ID in the ReadySetDone application."""

    id: str  # Task ID, typically a UUID

    @classmethod
    def new(cls) -> "Id":
        """Create a new Id with a generated UUID."""
        return cls(id=str(uuid.uuid4()))  # Generate a new UUID for the Id

    @classmethod
    def from_string(cls, id_str: str) -> "Id":
        """Create an Id object from a string representing the ID."""
        return cls(id=id_str)
