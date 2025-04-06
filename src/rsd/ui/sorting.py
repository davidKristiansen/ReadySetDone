# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Sorting logic for task rendering in ReadySetDone.
Defines a common SORT_KEY used by both CLI and TUI renderers.
"""

from rsd.api.types import Task


def SORT_KEY(task: Task) -> tuple:
    """
    Sorting priority: pinned first, then undone, then by creation date.

    Returns:
        tuple: (not pinned, done, created timestamp)
    """
    return (not task.pinned, task.done, task.created)
