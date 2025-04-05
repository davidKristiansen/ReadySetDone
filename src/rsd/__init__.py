# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
ReadySetDone - A terminal-based task management system.
"""

import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _fallback_version() -> str:
    pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject.exists():
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "unknown")
    return "unknown"


try:
    __version__ = version("readysetdone")
except PackageNotFoundError:
    __version__ = _fallback_version()
