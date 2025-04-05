#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Daemon entrypoint for ReadySetDone (`rsdd`).
Responsible for receiving, processing, and persisting task events through pub/sub.
Handles signals to gracefully shutdown.
"""

import logging
import signal

import anyio
from anyio import create_task_group

from rsd.api import (
    add_task,
    delete_task,
    deserialize,
    get_description,
    get_task,
    list_tasks,
    mark_done,
    mark_not_done,
    pin_task,
    serialize,
    set_description,
    task,
    toggle,
    types,
    unpin_task,
    update_task,
)
from rsd.config.args import Args
from rsd.config.config import Config
from rsd.logger import setup_logger
from rsd.pubsub import Pubsub
from rsd.pubsub.topics import (
    DESCRIPTION_GET,
    DESCRIPTION_SET,
    TASK_ADD,
    TASK_DELETE,
    TASK_MARK_DONE,
    TASK_MARK_NOT_DONE,
    TASK_PIN,
    TASK_TOGGLE,
    TASK_UNPIN,
    TASK_UPDATE,
    UPDATED_TASKS,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

keep = [
    TASK_ADD,
    TASK_UPDATE,
    TASK_DELETE,
    TASK_MARK_DONE,
    TASK_MARK_NOT_DONE,
    TASK_TOGGLE,
    TASK_PIN,
    TASK_UNPIN,
    DESCRIPTION_GET,
    DESCRIPTION_SET,
    UPDATED_TASKS,
    task,
    types,
    add_task,
    update_task,
    delete_task,
    get_task,
    list_tasks,
    mark_done,
    mark_not_done,
    toggle,
    pin_task,
    unpin_task,
    get_description,
    set_description,
    serialize,
    deserialize,
]


async def shutdown_handler(tg: anyio.abc.TaskGroup):
    with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.warning(f"Received signal {signum}, shutting down...")
            tg.cancel_scope.cancel()
            break


async def async_main() -> None:
    """Run the daemon, subscribe to events, and manage tasks."""
    async with create_task_group() as tg:
        # Start PubSub
        pubsub = Pubsub(
            mode="daemon",
            task_group=tg,
            serializer=serialize,
            deserializer=deserialize,
        )
        await pubsub.start()

        async def add_task_handler(payload):
            await add_task(deserialize(payload))

        pubsub.subscribe(TASK_ADD, add_task)

        logger.info("Daemon is running. Waiting for events...")

        # Start shutdown handler in parallel
        tg.start_soon(shutdown_handler, tg)

        # Keep running until cancelled (by shutdown signal)
        await anyio.Event().wait()

    # Cleanup after cancellation
    await pubsub.stop()
    logger.info("Daemon shutdown complete.")


def main() -> None:
    args = Args()
    config = Config(path=args.config_path, args=args, mode=args.mode)

    setup_logger(level=config.log_level, color=config.color)

    anyio.run(async_main)


if __name__ == "__main__":
    main()
