# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Parses command-line arguments for ReadySetDone.

This module defines:
- Args: unified wrapper to parse and expose arguments
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Literal, Optional

from rsd import __version__

ColorWhen = Literal["auto", "never", "always"]
Mode = Literal["cli", "daemon"]


DEFAULT_CONFIG_PATH = (
    Path(os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
    / "readysetdone"
    / "config.toml"
)


class Args:
    def __init__(self):
        prog = Path(sys.argv[0]).name

        if prog == "rsdd":
            self.mode: Mode = "daemon"
            parsed = _parse_daemon_args()
        else:
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument("command", nargs="?", default="list")
            known, _ = parser.parse_known_args()
            self.mode: Mode = "cli"
            parsed = _parse_cli_args(known.command)

        self.config_path = parsed.common.config_path
        self.verbose = parsed.common.verbose
        self.color = parsed.common.color

        # Flatten cli-specific arguments if they exist
        self.command = getattr(parsed, "command", None)
        self.task = getattr(parsed, "task", None)
        self.done = getattr(parsed, "done", False)
        self.index = getattr(parsed, "index", None)
        self.background = getattr(parsed, "background", False)


class _CommonArgs:
    def __init__(
        self,
        config_path: Optional[Path] = DEFAULT_CONFIG_PATH,
        verbose: bool = False,
        color: Optional[ColorWhen] = None,
    ):
        self.config_path = config_path
        self.verbose = verbose
        self.color = color


class _CliArgs:
    def __init__(
        self,
        common: _CommonArgs,
        task: Optional[str] = None,
        done: bool = False,
        index: Optional[int] = None,
        command: Optional[str] = None,
    ):
        self.common = common
        self.task = task
        self.done = done
        self.index = index
        self.command = command


class _DaemonArgs:
    def __init__(self, common: _CommonArgs, background: bool = False):
        self.common = common
        self.background = background


def _parse_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--version",
        action="version",
        version=f"ReadySetDone version {__version__}",
        help="Show program version and exit",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to config.toml (default: $HOME/.config/readysetdone/config.toml)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "never", "always"],
        help="Control color output: auto, never, or always",
    )


def _parse_cli_args(primary_command: str) -> _CliArgs:
    parser = argparse.ArgumentParser(prog="rsd")
    _parse_common_args(parser)
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list", help="List all tasks")
    subparsers.add_parser("tui", help="Launch TUI")

    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("task", type=str, help="Task description")
    add_parser.add_argument(
        "-d", "--done", action="store_true", help="Mark task as done"
    )

    for cmd in ["done", "toggle", "not-done", "delete", "pin", "unpin", "description"]:
        subparsers.add_parser(cmd, help=f"{cmd.title()} a task").add_argument(
            "index", type=int
        )

    args = parser.parse_args()
    common = _CommonArgs(
        config_path=args.config, verbose=args.verbose, color=args.color
    )
    return _CliArgs(
        common=common,
        command=args.command,
        task=getattr(args, "task", None),
        done=getattr(args, "done", False),
        index=getattr(args, "index", None),
    )


def _parse_daemon_args() -> _DaemonArgs:
    parser = argparse.ArgumentParser(prog="rsdd")
    _parse_common_args(parser)
    parser.add_argument("--background", action="store_true", help="Run in background")
    args = parser.parse_args()
    common = _CommonArgs(
        config_path=args.config, verbose=args.verbose, color=args.color
    )
    return _DaemonArgs(common=common, background=args.background)
