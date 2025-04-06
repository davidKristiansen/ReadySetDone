# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
This module exposes all core service logic for ReadySetDone.

Currently available:
- TaskService: High-level API for task and description operations.
"""

from .task_service import TaskService

__all__ = ["TaskService"]
