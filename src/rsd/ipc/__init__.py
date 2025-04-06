# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
IPC module layout for ReadySetDone.

Defines a clean separation between abstract interfaces and concrete implementations.
This setup allows easy switching between D-Bus and Socket-based IPC.

- `ipc/interface.py`: Abstract base classes for IpcClient and IpcServer.
- `ipc/dbus/__init__.py`: Concrete D-Bus client and server.
- `ipc/socket/__init__.py`: Concrete socket client and server.
- `ipc/__init__.py`: Exports public API and provides factory functions.
"""

from .dbus import DbusClient, DbusServer
from .interface import IpcClient, IpcServer


def get_ipc_client() -> IpcClient:
    """Factory method to get the default IPC client implementation."""
    return DbusClient()


def get_ipc_server(task_service) -> IpcServer:
    """Factory method to get the default IPC server implementation."""
    return DbusServer(task_service)


__all__ = ["IpcClient", "IpcServer", "get_ipc_client", "get_ipc_server"]
