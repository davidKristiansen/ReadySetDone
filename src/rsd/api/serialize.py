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
from datetime import datetime
from typing import Any

from rsd.api.types import Id, Task


def serialize(obj: Any) -> str:
    """Serialize a Python object to a JSON string."""
    if obj == "":
        return ""

    def dt(val):
        return val.isoformat() if isinstance(val, datetime) else val

    if isinstance(obj, Task):
        return json.dumps(
            {
                "id": obj.id,
                "task": obj.task,
                "done": obj.done,
                "created": dt(obj.created),
                "completed": dt(obj.completed),
                "due": dt(obj.due),
                "pinned": obj.pinned,
            }
        )
    elif isinstance(obj, list) and all(isinstance(t, Task) for t in obj):
        return json.dumps(
            [
                {
                    "id": t.id,
                    "task": t.task,
                    "done": t.done,
                    "created": dt(t.created),
                    "completed": dt(t.completed),
                    "due": dt(t.due),
                    "pinned": t.pinned,
                }
                for t in obj
            ]
        )
    elif isinstance(obj, Id):
        return json.dumps({"id": obj.id})
    else:
        raise TypeError(f"Unsupported type for serialization: {type(obj)}")
