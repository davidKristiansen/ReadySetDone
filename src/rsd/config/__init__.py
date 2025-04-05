# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Public interface for ReadySetDone configuration system.
"""

from .config import Config
from .args import Args

__all__ = ["Config", "Args"]
