# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Handles file I/O with locking using anyio for thread/process safety.
"""

import anyio


class LockedFile:
    def __init__(self, filepath: anyio.Path):
        self.file = anyio.Path(filepath)
        self.lock = anyio.Lock()

    async def read(self) -> str:
        """Read from the file with locking to ensure safety."""
        async with self.lock:
            async with await anyio.open_file(self.file, "r") as f:
                return await f.read()

    async def write(self, data: str) -> None:
        """Write to the file with locking to ensure safety."""
        async with self.lock:
            async with await anyio.open_file(self.file, "w") as f:
                await f.write(data)
