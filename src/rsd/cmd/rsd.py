#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Client entrypoint for ReadySetDone (`rsd`).
Responsible for publishing task-related events to the daemon.
"""

import logging
import signal
import sys

import anyio

from rsd.api import deserialize, serialize
from rsd.api.types import Id, Task
from rsd.config import Config
from rsd.config.args import Args
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
    serialize,
    deserialize,
]
logger = logging.getLogger(__name__)


async def shutdown_handler(tg: anyio.abc.TaskGroup):
    with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.warning(f"Received signal {signum}, shutting down...")
            tg.cancel_scope.cancel()
            break


async def async_main() -> None:
    """Client main loop to handle CLI commands and publish messages."""
    args = Args()
    config = Config(path=args.config_path, args=args, mode=args.mode)

    setup_logger(level=config.log_level, color=config.color)

    if args.mode == "tui":
        logger.info("TUI not yet implemented")
        return

    async with anyio.create_task_group() as tg:
        pubsub = Pubsub(
            mode="client",
            task_group=tg,
            serializer=serialize,
            deserializer=deserialize,
        )
        await pubsub.start()

        match args.command:
            case "add":
                task = Task.new(args.task)
                if args.done:
                    task.done = True
                pubsub.publish(TASK_ADD, task)
                logger.debug(f"Added task: {task.task}")

            case "delete":
                pubsub.publish(TASK_DELETE, serialize(Id.new(args.args.delete)))
                logger.debug(f"Delete task: {id}")

            case "toggle":
                pubsub.publish(TASK_TOGGLE, serialize(Id.new(args.args.toggle)))
                logger.debug(f"Toggle task: {id}")

            case "not-done":
                pubsub.publish(
                    TASK_MARK_NOT_DONE, serialize(Id.new(args.args.not_done))
                )
                logger.debug(f"Toggle task: {id}")

            case "list" | None:
                logger.info("Listing tasks not implemented yet")

        # tg.start_soon(shutdown_handler, tg)
        await anyio.Event().wait()

    await pubsub.stop()


def main() -> None:
    """Entrypoint for the rsd client."""
    try:
        anyio.run(async_main)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
