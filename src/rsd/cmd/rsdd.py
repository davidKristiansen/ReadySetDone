#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
File Path: src/rsd/cmd/rsdd.py

Daemon entrypoint for ReadySetDone (`rsdd`).
Responsible for receiving, processing, and persisting task events through pub/sub.
Handles signals to gracefully shutdown.
"""

import logging
import signal
from datetime import datetime

import anyio

from rsd import api
from rsd.pubsub import (
    PubSub,  # Using the PubSub interface exposed in the pubsub layer
    topics,  # Event types like TASK_ADD, TASK_UPDATE
)

logger = logging.getLogger(__name__)

# Configure the logger
logging.basicConfig(level=logging.INFO)

# Create a task pool to manage tasks
task_pool = []


# Async function to handle an event (this will be a task)
async def handle_event(event_data: str) -> None:
    """Process the event asynchronously."""
    logger.info(f"Processing event: {event_data}")
    # Simulate some async work (e.g., processing the event)
    await anyio.sleep(1)
    logger.info(f"Finished processing event: {event_data}")


async def task_added_callback(task_data: str) -> None:
    """Callback for task added event, now handled as a task."""
    logger.info(f"Task added: {task_data}")
    # Create an async task to process the event and add it to the task pool
    task = anyio.create_task(handle_event(task_data))
    task_pool.append(task)


async def task_updated_callback(task_data: str) -> None:
    """Callback for task updated event, now handled as a task."""
    logger.info(f"Task updated: {task_data}")
    task = anyio.create_task(handle_event(task_data))
    task_pool.append(task)


async def task_deleted_callback(task_id_data: str) -> None:
    """Callback for task deleted event, now handled as a task."""
    logger.info(f"Task deleted: {task_id_data}")
    task = anyio.create_task(handle_event(task_id_data))
    task_pool.append(task)


async def async_main(pubsub: PubSub) -> None:
    """Run the daemon and subscribe to task-related events."""
    # Subscribe to events through PubSub and route them to the appropriate callback
    pubsub.subscribe(topics.TASK_ADD, task_added_callback)
    pubsub.subscribe(topics.TASK_UPDATE, task_updated_callback)
    pubsub.subscribe(topics.TASK_DELETE, task_deleted_callback)

    # Keep the daemon running and processing events
    logger.info("Daemon is running and waiting for events...")

    # Wait for new tasks to arrive and be added to the pool
    while True:
        try:
            # Await any task in the pool
            if task_pool:
                # Process the next task asynchronously
                await anyio.gather(*task_pool)
                task_pool.clear()  # Clear the task pool after execution
            else:
                await anyio.sleep(1)  # No tasks in the pool, wait for new events
        except anyio.CancelledError:
            # Gracefully handle the cancellation when a signal is received
            logger.info("Daemon shutdown initiated.")
            break  # Exit the loop on cancellation

        except KeyboardInterrupt:
            logger.info("Gracefully shutting down...")
            break  # Exit the loop on keyboard interrupt (Ctrl+C)


def handle_shutdown(signum, frame) -> None:
    """Signal handler to perform cleanup and shutdown."""
    logger.info(f"Received shutdown signal: {signum}. Cleaning up...")
    # Perform any cleanup here (e.g., closing resources, saving state)
    anyio.cancel_all()  # Cancel all pending tasks gracefully
    logger.info("Shutdown complete.")


def main() -> None:
    """Sync wrapper to run the async entrypoint with AnyIO."""
    pubsub = PubSub()  # Initialize the pub/sub system

    # Register signal handling for graceful shutdown (SIGINT, SIGTERM)
    anyio.run(lambda: async_main(pubsub))  # Pass pubsub to async_main

    # Registering signal handlers using anyio's signal module
    anyio.signal(signal.SIGINT, handle_shutdown)  # For Ctrl+C (SIGINT)
    anyio.signal(signal.SIGTERM, handle_shutdown)  # For termination (SIGTERM)


if __name__ == "__main__":
    main()
