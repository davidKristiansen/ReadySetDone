# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Loads and manages configuration for ReadySetDone.

Supports sections:
- [rsd]    (shared)
- [cli]    (CLI and TUI client)
- [daemon] (daemon service)

Resolves environment variables and provides structured access via flattened fields.
"""

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from rsd.config.args import Args

ColorWhen = Literal["auto", "never", "always"]

_RSD_DATA_HOME = (
    Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    / "readysetdone"
)

_RSD_STATE_HOME = (
    Path(os.getenv("XDG_STATE_HOME") or Path.home() / ".local" / "state")
    / "readysetdone"
)


def _supports_color() -> bool:
    """Return True if the terminal supports color output."""
    return sys.stdout.isatty() and os.getenv("TERM") not in ("dumb", "")


@dataclass
class _CommonConfig:
    log_level: str = "info"
    log_file_location: str = str(_RSD_STATE_HOME / "rsd.log")
    color: bool = _supports_color()


@dataclass
class _CliConfig:
    ui_mode: str = "rich"
    show_timestamps: bool = True
    connect_timeout: int = 10
    reconnect_interval: int = 5


@dataclass
class _DaemonConfig:
    task_store_path: str = str(_RSD_DATA_HOME / "tasks.json")
    description_store_path: str = str(_RSD_DATA_HOME / "descriptions")
    task_polling_interval: int = 3
    shutdown_timeout: int = 5


class Config:
    def __init__(self, path: Path, args: Args, mode: str):
        if not path.exists():
            raise FileNotFoundError(f"Missing config: {path}")

        with path.open("rb") as f:
            raw = tomllib.load(f)

        expanded = _expand_env_vars(raw)

        common = _CommonConfig(**expanded.get("rsd", {}))
        if args.verbose:
            common.log_level = "debug"

        match args.color:
            case "always":
                common.color = True
            case "never":
                common.color = False
            case "auto" | _:
                common.color = _supports_color()

        self.mode = "tui" if args.command == "tui" else mode
        self.log_level = common.log_level
        self.log_file_location = common.log_file_location
        self.color = common.color

        if args.mode in ("cli", "tui"):
            cli = _CliConfig(**expanded.get("cli", {}))
            cli.ui_mode = "textual" if args.command == "tui" else "rich"
            self.ui_mode = cli.ui_mode
            self.show_timestamps = cli.show_timestamps
            self.connect_timeout = cli.connect_timeout
            self.reconnect_interval = cli.reconnect_interval

        elif args.mode == "daemon":
            daemon = _DaemonConfig(**expanded.get("daemon", {}))
            self.task_store_path = daemon.task_store_path
            self.description_store_path = daemon.description_store_path
            self.task_polling_interval = daemon.task_polling_interval
            self.shutdown_timeout = daemon.shutdown_timeout

        else:
            raise ValueError(f"Unknown config mode: {args.mode}")

    @property
    def is_cli(self) -> bool:
        return self.mode == "cli"

    @property
    def is_tui(self) -> bool:
        return self.mode == "tui"

    @property
    def is_daemon(self) -> bool:
        return self.mode == "daemon"


def _expand_env_vars(obj: Any) -> Any:
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    return obj
