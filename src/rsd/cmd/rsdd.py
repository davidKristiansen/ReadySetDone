#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Daemon entrypoint for ReadySetDone (`rsdd`).
Responsible for receiving, processing and persisting task events.
"""

import anyio
import logging

from rsd.daemon import main as daemon_main
from rsd.args import parse_common_args

logger = logging.getLogger(__name__)


async def async_main() -> None:
    """Run the daemon main function with proper async setup."""
    await daemon_main()


def main() -> None:
    """Sync wrapper to run the async entrypoint with AnyIO."""
    args = parse_common_args()

    anyio.run(async_main)


if __name__ == "__main__":
    main()

