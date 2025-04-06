# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Module for deserializing objects in the ReadySetDone application.

This module contains functions for converting JSON strings back into
Python objects (deserialization). The primary focus is on deserializing
tasks and their associated data from JSON format back into Python objects
so they can be used in the application.

Functions:
- deserialize: Deserializes a JSON string to the appropriate Python object.
"""

import json
from datetime import datetime
from typing import Union

from rsd.api.types import Id, Task


def _deserialize_task(data: dict) -> Task:
    created = datetime.fromisoformat(data["created"]) if data["created"] else None
    completed = datetime.fromisoformat(data["completed"]) if data["completed"] else None
    due = datetime.fromisoformat(data["due"]) if data["due"] else None
    return Task(
        id=data["id"],
        task=data["task"],
        done=data["done"],
        created=created,
        completed=completed,
        due=due,
        pinned=data["pinned"],
    )


def deserialize(payload: str) -> Union[None, Id, Task, list[Task]]:
    """Deserialize a JSON string to the appropriate Python object."""
    if not payload.strip():
        return None

    data = json.loads(payload)

    # Handle a list of tasks
    if isinstance(data, list):
        return [_deserialize_task(item) for item in data if "task" in item]

    # Single Task
    if "task" in data:
        return _deserialize_task(data)

    # Single Id
    if "id" in data:
        return Id(id=data["id"])

    raise TypeError("Unsupported type for deserialization, missing 'task' or 'id' key.")
