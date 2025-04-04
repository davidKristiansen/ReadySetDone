# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Public interface for ReadySetDone configuration system.
"""

from .config import load_config, Config
from .args import parse_args

__all__ = ["Config", "load_config", "parse_args"]
