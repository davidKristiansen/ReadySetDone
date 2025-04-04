# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
This module defines the pub/sub topics used in ReadySetDone.
"""

# Topics for publishing and subscribing
TASK_ADD = "task/add"
TASK_UPDATE = "task/update"
TASK_DELETE = "task/delete"
TASK_MARK_DONE = "task/mark-done"
TASK_MARK_NOT_DONE = "task/mark-not-done"
TASK_TOGGLE = "task/toggle"
TASK_PIN = "task/pin"
TASK_UNPIN = "task/unpin"
DESCRIPTION_GET = "description/get"
DESCRIPTION_SET = "description/set"

# Additional topic for updating views
UPDATED_TASKS = "update/tasks"
