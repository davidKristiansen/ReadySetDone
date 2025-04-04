#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
File Path: src/rsd/cmd/rsd.py

Client entrypoint for ReadySetDone (`rsd`).
Responsible for publishing task-related events to the daemon.
"""

import logging
import anyio
from rsd.pubsub.dbus_pubsub import DbusPubSub
from rsd.api.pubsub import TASK_ADD, TASK_UPDATE, TASK_DELETE
from rsd.api.types import Task

logger = logging.getLogger(__name__)

# Configure the logger
logging.basicConfig(level=logging.INFO)


async def async_main() -> None:
    """Run the client and publish events."""
    pubsub = DbusPubSub()  # Using the pubsub system

    # Example: Add a task (UI should handle interactions)
    new_task = Task.new("Finish the client setup")
    # UI part should trigger the event to add the task.
    await pubsub.publish(TASK_ADD, new_task)

    # Simulate interaction with the daemon or other listeners
    logger.info(f"Task added: {new_task}")

    # Keep the client running (simulate idle loop)
    while True:
        await anyio.sleep(1)


def main() -> None:
    """Sync wrapper to run the async entrypoint with AnyIO."""
    anyio.run(async_main)


if __name__ == "__main__":
    main()
