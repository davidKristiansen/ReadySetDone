# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
This module exposes the ReadySetDone API functions for easy access.
"""

from . import task, types
from .deserialize import deserialize
from .serialize import serialize

add_task = task.add
update_task = task.update
delete_task = task.delete
get_task = task.get
list_tasks = task.list
mark_done = task.mark_done
mark_not_done = task.mark_not_done
toggle = task.toggle
pin_task = task.pin
unpin_task = task.unpin
get_description = task.get_description
set_description = task.set_description

serialize = serialize
deserialize = deserialize

__all__ = [
    "task",
    "types",
    "add_task",
    "update_task",
    "delete_task",
    "get_task",
    "list_tasks",
    "mark_done",
    "mark_not_done",
    "toggle",
    "pin_task",
    "unpin_task",
    "get_description",
    "set_description",
    "serialize",
    "deserialize",
]
