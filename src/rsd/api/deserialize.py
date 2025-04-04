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
from typing import Any

from rsd.api.types import Id, Task


def deserialize(payload: str) -> Any:
    """Deserialize a JSON string to the appropriate Python object."""
    data = json.loads(payload)

    # Check if the 'task' key is present to identify Task
    if "task" in data:
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

    # Check if the 'id' key is present to identify Id
    elif "id" in data:
        return Id(id=data["id"])

    # If neither a Task nor Id object is found, raise an error
    raise TypeError("Unsupported type for deserialization, missing 'task' or 'id' key.")
