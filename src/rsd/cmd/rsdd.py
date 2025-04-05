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

from rsd.config.args import Args
from rsd.config.config import Config
from rsd.logger import setup_logger
from rsd.pubsub import PubSub, topics

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def handle_event(topic: str, payload: str) -> None:
    """Process events based on topic."""
    logger.info(f"Processing {topic}: {payload}")
    await anyio.sleep(1)  # Simulated processing work
    logger.info(f"Completed processing {topic}: {payload}")


async def async_main(pubsub: PubSub) -> None:
    """Run the daemon, subscribe to events, and manage tasks."""
    async with create_task_group() as tg:

        async def shutdown_handler():
            with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
                async for signum in signals:
                    logger.warning(f"Received signal {signum}, shutting down...")
                    tg.cancel_scope.cancel()
                    break

        # Start PubSub
        await pubsub.start()

        # Subscribe to PubSub topics and add tasks to task group
        def create_callback(topic: str, payload: str):
            print(topic, payload)

            async def callback(data: str):
                await tg.start(handle_event, topic, data)

            return callback

        pubsub.subscribe("*", lambda topic, payload: handle_event(topic, payload))

        logger.info("Daemon is running. Waiting for events...")

        # Start shutdown handler in parallel
        tg.start_soon(shutdown_handler)

        # Keep running until cancelled (by shutdown signal)
        await anyio.Event().wait()

    # Cleanup after cancellation
    await pubsub.stop()
    logger.info("Daemon shutdown complete.")


def main() -> None:
    args = Args()
    config = Config(path=args.config_path, args=args, mode=args.mode)

    setup_logger(level=config.rsd.log_level, color=config.rsd.color)

    pubsub = PubSub(mode="daemon")
    anyio.run(async_main, pubsub)


if __name__ == "__main__":
    main()
