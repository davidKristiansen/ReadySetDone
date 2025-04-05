# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Loads and manages configuration for ReadySetDone.

Supports sections:
- [rsd]    (shared)
- [cli]    (CLI client)
- [tui]    (TUI client)
- [daemon] (daemon service)

Resolves environment variables and provides structured access via dataclasses.
"""

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rsd.config.args import Args, ColorWhen, Mode


def default_config_path() -> Path:
    """Return default config path using XDG_CONFIG_HOME or fallback to ~/.config."""
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "readysetdone" / "config.toml"


def _supports_color() -> bool:
    """Return True if the terminal supports color output."""
    return sys.stdout.isatty() and os.getenv("TERM") not in ("dumb", "")


@dataclass
class RsdConfig:
    log_level: str = "info"
    log_file_location: str = "${XDG_STATE_HOME}/readysetdone"
    color: bool = _supports_color()


@dataclass
class CliConfig:
    ui_mode: str = "rich"
    show_timestamps: bool = True
    connect_timeout: int = 10
    reconnect_interval: int = 5


@dataclass
class TuiConfig:
    ui_mode: str = "textual"
    connect_timeout: int = 10
    reconnect_interval: int = 5


@dataclass
class DaemonConfig:
    task_store_path: str = "${XDG_DATA_HOME}/readysetdone/tasks.json"
    description_store_path: str = "${XDG_DATA_HOME}/readysetdone/descriptions"
    task_polling_interval: int = 3
    shutdown_timeout: int = 30


@dataclass
class Config:
    rsd: RsdConfig
    cli: CliConfig | None = None
    tui: TuiConfig | None = None
    daemon: DaemonConfig | None = None
    mode: Mode = "cli"

    def __init__(self, path: Path, args: Args, mode: Mode):
        if not path.exists():
            raise FileNotFoundError(f"Missing config: {path}")

        with path.open("rb") as f:
            raw = tomllib.load(f)

        expanded = _expand_env_vars(raw)

        rsd = RsdConfig(**expanded.get("rsd", {}))
        if args.common.verbose:
            rsd.log_level = "debug"

        match args.common.color:
            case "always":
                rsd.color = True
            case "never":
                rsd.color = False
            case "auto" | _:
                rsd.color = _supports_color()

        self.rsd = rsd
        self.mode = mode

        if mode == "cli":
            self.cli = CliConfig(**expanded.get("cli", {}))
            self.tui = None
            self.daemon = None
        elif mode == "tui":
            self.tui = TuiConfig(**expanded.get("tui", {}))
            self.cli = None
            self.daemon = None
        elif mode == "daemon":
            self.daemon = DaemonConfig(**expanded.get("daemon", {}))
            self.cli = None
            self.tui = None
        else:
            raise ValueError(f"Unknown config mode: {mode}")

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
