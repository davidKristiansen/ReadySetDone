# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Handles file I/O with locking using anyio for thread/process safety.
"""

import anyio
import asyncio
from pathlib import Path


class LockedFile:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.lock = asyncio.Lock()

    async def read(self) -> str:
        """Read from the file with locking to ensure safety."""
        async with self.lock:
            async with anyio.open(self.filepath, "r") as f:
                return await f.read()

    async def write(self, data: str) -> None:
        """Write to the file with locking to ensure safety."""
        async with self.lock:
            async with anyio.open(self.filepath, "w") as f:
                await f.write(data)
