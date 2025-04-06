# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
D-Bus client implementation for ReadySetDone.
Connects to the D-Bus daemon and provides methods to call task-related operations
and receive task update signals.
"""

import logging
from typing import Awaitable, Callable

import anyio
from dbus_next.aio import MessageBus

from rsd.api import deserialize, serialize
from rsd.api.types import Id, Task
from rsd.ipc.interface import IpcClient

from .constants import DBUS_INTERFACE

logger = logging.getLogger(__name__)


class DbusClient(IpcClient):
    def __init__(self) -> None:
        self._on_update: Callable[[list[Task]], Awaitable[None]] | None = None
        self._iface = None

    async def start(self) -> IpcClient:
        """Connect to the D-Bus daemon and subscribe to signals."""
        bus = await MessageBus().connect()
        object_path = "/" + "/".join(DBUS_INTERFACE)
        introspection = await bus.introspect(".".join(DBUS_INTERFACE), object_path)
        proxy = bus.get_proxy_object(
            ".".join(DBUS_INTERFACE), object_path, introspection
        )
        self._iface = proxy.get_interface(".".join(DBUS_INTERFACE))

        # Register signal handler
        self._iface.on_task_updated(self._on_task_updated_signal)

        logger.debug("D-Bus client connected")
        return self

    def _on_task_updated_signal(self, payload: str) -> None:
        """Signal handler that runs in a sync context, delegates to async."""
        anyio.from_thread.run(self._handle_task_updated, payload)

    def _on_task_updated_signal(self, payload: str) -> None:
        """Raw signal handler — just forwards to registered callback."""
        if self._on_update:
            self._on_update(payload)  # handler is now sync!

    def on_task_updated(self, handler: Callable[[list[Task]], Awaitable[None]]) -> None:
        self._on_update = handler

    async def add_task(self, task: Task) -> None:
        await self._iface.call_add_task(serialize(task))

    async def delete_task(self, task_id: Id) -> None:
        await self._iface.call_delete_task(serialize(task_id))

    async def update_task(self, task: Task) -> None:
        await self._iface.call_update_task(serialize(task))

    async def mark_done(self, task_id: Id) -> None:
        await self._iface.call_mark_done(serialize(task_id))

    async def mark_not_done(self, task_id: Id) -> None:
        await self._iface.call_mark_not_done(serialize(task_id))

    async def toggle(self, task_id: Id) -> None:
        await self._iface.call_toggle(serialize(task_id))

    async def pin(self, task_id: Id) -> None:
        await self._iface.call_pin(serialize(task_id))

    async def unpin(self, task_id: Id) -> None:
        await self._iface.call_unpin(serialize(task_id))

    async def set_description(self, task_id: Id, description: str) -> None:
        await self._iface.call_set_description(serialize(task_id), description)

    async def get_description(self, task_id: Id) -> str:
        return await self._iface.call_get_description(serialize(task_id))

    async def list_tasks(self) -> list[Task]:
        payload = await self._iface.call_list_tasks()
        return deserialize(payload)
