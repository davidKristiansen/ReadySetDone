# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
This module exposes the pub/sub interface for the ReadySetDone application.

The PubSub system is responsible for handling communication via DBus.
It provides methods for subscribing to events and publishing messages.

Exposed Classes:
- PubSub: A wrapper around DbusPubSub for easy interaction.
"""

from .dbus_pubsub import DbusPubsub

# Expose DbusPubSub as PubSub
Pubsub = DbusPubsub
