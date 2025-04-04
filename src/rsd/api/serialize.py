# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Module for serializing objects in the ReadySetDone application.

This module contains functions for converting Python objects into
JSON strings (serialization). The primary focus is on serializing
tasks and their associated data into a JSON format that can be sent
over DBus or stored in persistent storage.

Functions:
- serialize: Serializes a Python object to a JSON string.
"""

import json
from typing import Any

from rsd.api.types import Id, Task


def serialize(obj: Any) -> str:
    """Serialize a Python object to a JSON string."""
    if isinstance(obj, Task):
        return json.dumps(
            {
                "id": obj.id,  # Directly use the ID as a string
                "task": obj.task,
                "done": obj.done,
                "created": obj.created.isoformat() if obj.created else None,
                "completed": obj.completed.isoformat() if obj.completed else None,
                "due": obj.due.isoformat() if obj.due else None,
                "pinned": obj.pinned,
            }
        )
    elif isinstance(obj, Id):
        return json.dumps({"id": obj.id})  # Simply return the ID as a JSON string
    else:
        raise TypeError(f"Unsupported type for serialization: {type(obj)}")
