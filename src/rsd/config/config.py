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
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def default_config_path() -> Path:
    """Return default config path using XDG_CONFIG_HOME or fallback to ~/.config."""
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "readysetdone" / "config.toml"


@dataclass
class RsdConfig:
    log_level: str = "info"
    log_file_location: str = "${XDG_STATE_HOME}/readysetdone"


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
    rsd: RsdConfig = field(default_factory=RsdConfig)
    cli: CliConfig = field(default_factory=CliConfig)
    tui: TuiConfig = field(default_factory=TuiConfig)
    daemon: DaemonConfig = field(default_factory=DaemonConfig)


def _expand_env_vars(obj: Any) -> Any:
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    return obj


def load_config(path: Path | None = None) -> Config:
    config_path = path or default_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config: {config_path}")

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    expanded = _expand_env_vars(data)

    return Config(
        rsd=RsdConfig(**expanded.get("rsd", {})),
        cli=CliConfig(**expanded.get("cli", {})),
        tui=TuiConfig(**expanded.get("tui", {})),
        daemon=DaemonConfig(**expanded.get("daemon", {})),
    )
