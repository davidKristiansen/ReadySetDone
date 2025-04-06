# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Handles file I/O with locking using anyio for thread/process safety.

Ensures parent directory and file exist before each operation.
"""

import anyio
from anyio import Path


class LockedFile:
    def __init__(self, filepath: Path) -> None:
        self.file = Path(filepath)
        self.lock = anyio.Lock()

    async def read(self) -> str:
        """Read from the file with locking to ensure safety."""
        async with self.lock:
            await self._ensure_exists()
            async with await anyio.open_file(self.file, "r") as f:
                return await f.read()

    async def write(self, data: str) -> None:
        """Write to the file with locking to ensure safety."""
        async with self.lock:
            await self._ensure_exists()
            async with await anyio.open_file(self.file, "w") as f:
                await f.write(data)

    async def _ensure_exists(self) -> None:
        """Ensure parent folder and file exist."""
        await self.file.parent.mkdir(parents=True, exist_ok=True)
        if not await self.file.exists():
            await self.file.write_text("")  # create empty file if missing
