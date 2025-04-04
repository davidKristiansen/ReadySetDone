# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Shared argument parsing logic for ReadySetDone CLI tools.
Used by both `rsd` and `rsdd`.
"""

import argparse
import os
import sys
from typing import Literal
from importlib.metadata import version as get_version

ColorWhen = Literal["auto", "never", "always"]


def default_config_path() -> str:
    """Return the default config file path from XDG_CONFIG_HOME."""
    xdg_config = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(xdg_config, "readysetdone", "config.toml")


def parse_common_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse common CLI arguments shared between `rsd` and `rsdd`.

    Args:
        argv: Optional list of arguments to parse (default: sys.argv)

    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        add_help=True,
        description="ReadySetDone: terminal-based todo manager",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=default_config_path(),
        help="Path to config file (default: $XDG_CONFIG_HOME/readysetdone/config.toml)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug output",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {get_version('readysetdone')}",
    )

    parser.add_argument(
        "--color",
        type=str,
        choices=["auto", "never", "always"],
        default="auto",
        help="Control color output: auto, never, always (default: auto)",
    )

    return parser.parse_args(argv)
