#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Daemon entrypoint for ReadySetDone (`rsdd`).
Responsible for receiving, processing, and persisting task events through IPC.
Handles signals to gracefully shutdown.
"""

import logging
import signal

import anyio
from anyio import create_task_group

from rsd.config import Args, Config
from rsd.ipc import get_ipc_server
from rsd.logger import setup_logger
from rsd.service import TaskService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def shutdown_handler(stop_event: anyio.Event) -> None:
    with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.warning(f"Received signal {signum}, shutting down...")
            stop_event.set()
            break


async def async_main() -> None:
    args = Args()
    config = Config(path=args.config_path, args=args, mode=args.mode)

    setup_logger(level=config.log_level, color=config.color)
    task_service = TaskService(config.task_store_path)
    ipc_server = get_ipc_server(task_service)

    async with create_task_group() as tg:
        await ipc_server.start()
        logger.info("Daemon is running. Waiting for events...")

        stop_event = anyio.Event()
        tg.start_soon(shutdown_handler, stop_event)

        await stop_event.wait()
        await ipc_server.stop()

    logger.info("Daemon shutdown complete.")


def main() -> None:
    anyio.run(async_main)


if __name__ == "__main__":
    main()
