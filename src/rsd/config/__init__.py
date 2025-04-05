# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Public interface for ReadySetDone configuration system.
"""

from .args import Args
from .config import Config

__all__ = ["Config", "Args"]
