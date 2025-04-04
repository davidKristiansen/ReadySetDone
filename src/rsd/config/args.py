# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Parses command-line arguments for ReadySetDone.

This module defines:
- CommonArgs: base args shared by both client and daemon
- ClientArgs: args specific to the rsd CLI client
- DaemonArgs: args specific to the rsdd daemon
- Args: unified entrypoint wrapper to choose between modes
"""

import argparse
from pathlib import Path
from typing import Literal, Optional, Union

ColorWhen = Literal["auto", "never", "always", None]
Mode = Literal["cli", "tui", "daemon"]

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "readysetdone" / "config.toml"


class CommonArgs:
    def __init__(
        self, config_path: Optional[Path] = DEFAULT_CONFIG_PATH, verbose: bool = False, color: ColorWhen = None
    ):
        self.config_path = config_path
        self.verbose = verbose
        self.color = color


class ClientArgs:
    def __init__(
        self,
        common: CommonArgs,
        command: Optional[str] = None,
        task: Optional[str] = None,
        done: bool = False,
    ):
        self.common = common
        self.command = command
        self.task = task
        self.done = done


class DaemonArgs:
    def __init__(
        self,
        common: CommonArgs,
        background: bool = False,
    ):
        self.common = common
        self.background = background


class Args:
    def __init__(self, mode: Mode):
        self.mode = mode
        self.args: Union[ClientArgs, DaemonArgs]
        if mode == "client":
            self.args = parse_client_args()
        elif mode == "daemon":
            self.args = parse_daemon_args()
        else:
            raise ValueError(f"Invalid mode: {mode}")

    @property
    def config_path(self) -> Path:
        return self.args.common.config_path

    @property
    def common(self) -> CommonArgs:
        return self.args.common


def parse_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to config.toml (default: $HOME/.config/readysetdone/config.toml)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--color",
        type=str,
        choices=["auto", "never", "always"],
        default="auto",
        help="Control color output: auto, never, or always",
    )


def parse_client_args() -> ClientArgs:
    parser = argparse.ArgumentParser(prog="rsd")
    parse_common_args(parser)

    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list", help="List all tasks (default if no command is given)")

    subparsers.add_parser("tui", help="Launch TUI")

    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("task", type=str, help="Task description")
    add_parser.add_argument("-d", "--done", action="store_true", help="Mark task as done")

    subparsers.add_parser("delete", help="Delete a task")
    subparsers.add_parser("toggle", help="Toggle done state")
    subparsers.add_parser("not-done", help="Mark task as not done")

    args = parser.parse_args()
    common = CommonArgs(config_path=args.config, verbose=args.verbose, color=args.color)
    return ClientArgs(
        common=common,
        command=args.command,
        task=getattr(args, "task", None),
        done=getattr(args, "done", False),
    )


def parse_daemon_args() -> DaemonArgs:
    parser = argparse.ArgumentParser(prog="rsdd")
    parse_common_args(parser)

    parser.add_argument(
        "--background",
        action="store_true",
        help="Run daemon in background (default: run in foreground)",
    )

    args = parser.parse_args()
    common = CommonArgs(config_path=args.config, verbose=args.verbose, color=args.color)
    return DaemonArgs(
        common=common,
        background=args.background,
    )
