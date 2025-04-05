#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright David Kristiansen
# ruff: noqa: F821

"""
Daemon entrypoint for ReadySetDone (`rsdd`).
Responsible for receiving, processing, and persisting task events through pub/sub.
Handles signals to gracefully shutdown.
"""

import logging

import anyio
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next.service import signal as dbus_signal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DBUS_INTERFACE = ("com", "readysetdone")


class RsdInterface(ServiceInterface):
    def __init__(self, interface_name, pubsub):
        super().__init__(interface_name)
        self.pubsub = pubsub
        logger.debug(f"Initialized RsdInterface with {interface_name}")

    @method()
    async def Publish(self, topic: "s", payload: "s") -> "s":
        logger.info(f"[DBUS] Received publish: {topic} → {payload}")
        await self.pubsub._handle_incoming_publish(topic, payload)
        return "published"

    @dbus_signal()
    def Broadcast(self, topic: "s", payload: "s"):
        logger.debug(f"[DBUS] Broadcasting: {topic} → {payload}")
        return (topic, payload)


class DbusPubsub:
    def __init__(self, mode="client", dbus_interface=DBUS_INTERFACE):
        self.mode = mode
        self.dbus_interface = dbus_interface
        self.interface_name = ".".join(dbus_interface)
        self.object_path = "/" + "/".join(dbus_interface)
        self.bus = None
        self.interface = None
        self.subscribers = {}
        logger.debug(f"DbusPubsub initialized in {self.mode.upper()} mode")

    async def start(self):
        self.bus = await MessageBus().connect()
        logger.info("Connected to D-Bus session bus")

        if self.mode == "daemon":
            self.interface = RsdInterface(self.interface_name, self)
            self.bus.export(self.object_path, self.interface)
            await self.bus.request_name(self.interface_name)
            logger.info(f"DbusPubsub started in DAEMON mode at {self.object_path} ({self.interface_name})")
        else:
            logger.info("DbusPubsub started in CLIENT mode")

    def subscribe(self, topic, callback):
        self.subscribers.setdefault(topic, []).append(callback)
        logger.debug(f"Subscribed to topic: {topic}")

    def publish(self, topic, payload):
        logger.debug(f"Publishing to topic: {topic} with payload: {payload}")
        if self.mode == "client":
            anyio.create_task(self._client_publish(topic, payload))
        else:
            if self.interface:
                self.interface.Broadcast(topic, payload)
            else:
                logger.warning("Attempted to broadcast, but interface is not initialized")

    async def _client_publish(self, topic, payload):
        try:
            proxy = await self.bus.introspect(self.interface_name, self.object_path)
            obj = self.bus.get_proxy_object(self.interface_name, self.object_path, proxy)
            iface = obj.get_interface(self.interface_name)
            result = await iface.call_publish(topic, payload)
            logger.info(f"[CLIENT] Publish result from daemon: {result}")
        except Exception as e:
            logger.error(f"[CLIENT] Failed to publish message to {topic}: {e}")

    async def _handle_incoming_publish(self, topic, payload):
        handlers = self.subscribers.get(topic, []) + self.subscribers.get("*", [])

        if not handlers:
            logger.warning(f"[DAEMON] No subscribers for topic: {topic}")

        for cb in handlers:
            try:
                logger.debug(f"Dispatching to subscriber for topic: {topic}")
                await cb(topic, payload)
            except Exception as e:
                logger.exception(f"Error in subscriber callback for topic {topic}: {e}")

    async def stop(self):
        if self.bus:
            logger.info("Disconnecting from D-Bus session bus")
            self.bus.disconnect()
            self.bus = None
        else:
            logger.debug("Stop called but bus was already None")
