# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Manages client and daemon mode communications via D-Bus.
"""

import inspect
import logging
from typing import Callable, Optional

from anyio.abc import TaskGroup
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next.service import signal as dbus_signal

logger = logging.getLogger(__name__)

DBUS_INTERFACE = ("com", "readysetdone")


class _DbusInterface(ServiceInterface):
    """Private D-Bus interface for message passing."""

    def __init__(self, interface_name: str, pubsub: "DbusPubsub"):
        super().__init__(interface_name)
        self.pubsub = pubsub
        logger.debug(f"Initialized _DbusInterface with {interface_name}")

    # ruff: noqa: F821
    @method()
    async def Publish(self, topic: "s", payload: "s") -> "s":
        logger.info(f"[DAEMON] Received Publish call: {topic} → {payload}")
        await self.pubsub._dispatch_incoming("Publish", topic, payload)
        return "published"

    @dbus_signal()
    def Broadcast(self, topic: "s", payload: "s") -> "ss":
        logger.info(f"[DAEMON] Emitting Broadcast: {topic} → {payload}")
        return [topic, payload]


class DbusPubsub:
    def __init__(
        self,
        mode: str = "client",
        dbus_interface: tuple[str, ...] = DBUS_INTERFACE,
        task_group: Optional[TaskGroup] = None,
        serializer: Callable | None = None,
        deserializer: Callable | None = None,
    ):
        self.mode = mode
        self.dbus_interface = dbus_interface
        self.interface_name = ".".join(dbus_interface)
        self.object_path = "/" + "/".join(dbus_interface)
        self.bus = None
        self.interface = None
        self.subscribers: dict[str, list[Callable]] = {}
        self.task_group = task_group
        self.serializer = serializer
        self.deserializer = deserializer

        logger.info(
            f"DbusPubsub initialized in {self.mode.upper()} mode with "
            f"TaskGroup={bool(task_group)}"
        )

    async def start(self):
        self.bus = await MessageBus().connect()
        logger.info(f"Connected to D-Bus in {self.mode.upper()} mode")

        if self.mode == "daemon":
            self.interface = _DbusInterface(self.interface_name, self)
            self.bus.export(self.object_path, self.interface)
            await self.bus.request_name(self.interface_name)
            logger.info(
                f"Exported interface {self.interface_name} at {self.object_path}"
            )

        elif self.mode == "client":
            introspection = await self.bus.introspect(
                self.interface_name, self.object_path
            )
            obj = self.bus.get_proxy_object(
                self.interface_name, self.object_path, introspection
            )
            self.interface = obj.get_interface(self.interface_name)
            self.interface.on_broadcast(self._handle_broadcast)
            logger.info("Subscribed to Broadcast signals in CLIENT mode")

    def subscribe(self, topic: str, callback: Callable):
        self.subscribers.setdefault(topic, []).append(callback)
        logger.debug(f"Subscribed callback to topic: {topic}")

    def publish(self, topic: str, payload: str):
        logger.debug(f"Publishing topic: {topic}, payload: {payload}")

        if not isinstance(payload, str):
            payload = self.serializer(payload)

        if self.mode == "client":
            self.task_group.start_soon(self._client_publish, topic, payload)
        elif self.mode == "daemon":
            if self.interface:
                self.interface.Broadcast(topic, payload)
            else:
                logger.warning("Cannot broadcast: D-Bus interface is uninitialized")

    async def _client_publish(self, topic: str, payload: str):
        try:
            result = await self.interface.call_publish(topic, payload)
            logger.info(f"[CLIENT] Publish result: {result}")
        except Exception as e:
            logger.exception(f"[CLIENT] Publish failed: {e}")

    async def _dispatch_incoming(self, method_type: str, topic: str, payload: str):
        logger.debug(f"Dispatching incoming {method_type}: {topic} → {payload}")

        handlers = self.subscribers.get(topic, []) + self.subscribers.get("*", [])
        if not handlers:
            logger.warning(f"No handlers for topic: {topic}")
            return

        payload = self.deserializer(payload)

        for cb in handlers:
            try:
                if inspect.iscoroutinefunction(cb):
                    logger.debug("Dispatching in async mode")
                    await cb(payload)
                else:
                    logger.debug("Dispatching in sync mode")
                    cb(payload)
            except Exception as e:
                logger.exception(f"Handler exception for topic {topic}: {e}")

    async def _handle_broadcast(self, topic: str, payload: str):
        logger.info(f"[CLIENT] Received broadcast: {topic} → {payload}")
        await self._dispatch_incoming("Broadcast", topic, payload)

    async def stop(self):
        if self.bus:
            self.bus.disconnect()
            self.bus = None
            logger.info("Disconnected from D-Bus")
