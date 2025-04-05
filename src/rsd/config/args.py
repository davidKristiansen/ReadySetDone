# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Parses command-line arguments for ReadySetDone.

This module defines:
- CommonArgs: base args shared by all modes
- CliArgs: arguments for CLI mode
- TuiArgs: arguments for TUI mode
- DaemonArgs: arguments for daemon mode
- Args: unified wrapper to parse and expose arguments
"""

import argparse
import sys
from pathlib import Path
from typing import Literal, Optional

from rsd import __version__

ColorWhen = Literal["auto", "never", "always"]
Mode = Literal["cli", "tui", "daemon"]

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "readysetdone" / "config.toml"


class CommonArgs:
    def __init__(
        self,
        config_path: Optional[Path] = DEFAULT_CONFIG_PATH,
        verbose: bool = False,
        color: Optional[ColorWhen] = None,
    ):
        self.config_path = config_path
        self.verbose = verbose
        self.color = color


class CliArgs:
    def __init__(
        self,
        common: CommonArgs,
        task: Optional[str] = None,
        done: bool = False,
        command: Optional[str] = None,
    ):
        self.common = common
        self.task = task
        self.done = done
        self.command = command


class TuiArgs:
    def __init__(self, common: CommonArgs):
        self.common = common


class DaemonArgs:
    def __init__(self, common: CommonArgs, background: bool = False):
        self.common = common
        self.background = background


class Args:
    def __init__(self):
        prog = Path(sys.argv[0]).name

        if prog == "rsdd":
            self.mode: Mode = "daemon"
            self.args = parse_daemon_args()
        else:
            # Pre-parse just the first positional command
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument("command", nargs="?", default="list")
            known, _ = parser.parse_known_args()

            if known.command == "tui":
                self.mode: Mode = "tui"
                self.args = parse_tui_args()
            else:
                self.mode: Mode = "cli"
                self.args = parse_cli_args()

    @property
    def config_path(self) -> Path:
        return self.args.common.config_path

    @property
    def common(self) -> CommonArgs:
        return self.args.common


def parse_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-v",
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
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--color",
        choices=["auto", "never", "always"],
        help="Control color output: auto, never, or always",
    )


def parse_cli_args() -> CliArgs:
    parser = argparse.ArgumentParser(prog="rsd")
    parse_common_args(parser)
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list", help="List all tasks")
    subparsers.add_parser("tui", help="Launch TUI")

    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("task", type=str, help="Task description")
    add_parser.add_argument("-d", "--done", action="store_true", help="Mark task as done")

    subparsers.add_parser("delete", help="Delete a task")
    subparsers.add_parser("toggle", help="Toggle done state")
    subparsers.add_parser("not-done", help="Mark task as not done")

    args = parser.parse_args()
    common = CommonArgs(config_path=args.config, verbose=args.verbose, color=args.color)
    return CliArgs(
        common=common,
        command=args.command,
        task=getattr(args, "task", None),
        done=getattr(args, "done", False),
    )


def parse_tui_args() -> TuiArgs:
    # Strip 'tui' from sys.argv so it doesn't confuse parse_common_args
    sys.argv.pop(1)
    parser = argparse.ArgumentParser(prog="rsd tui")
    parse_common_args(parser)
    args = parser.parse_args()
    common = CommonArgs(config_path=args.config, verbose=args.verbose, color=args.color)
    return TuiArgs(common=common)


def parse_daemon_args() -> DaemonArgs:
    parser = argparse.ArgumentParser(prog="rsdd")
    parse_common_args(parser)
    parser.add_argument("--background", action="store_true", help="Run in background")
    args = parser.parse_args()
    common = CommonArgs(config_path=args.config, verbose=args.verbose, color=args.color)
    return DaemonArgs(common=common, background=args.background)
