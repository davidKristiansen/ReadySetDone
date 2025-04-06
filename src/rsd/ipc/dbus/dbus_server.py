# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
D-Bus server implementation for the ReadySetDone application.
Implements all IpcServer protocol methods and publishes signals on updates.
"""

import logging
from typing import Any

from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, signal

from rsd.api import deserialize, serialize
from rsd.service import TaskService

from .constants import DBUS_INTERFACE

logger = logging.getLogger(__name__)


class DbusServerInterface(ServiceInterface):
    def __init__(self, task_service: TaskService) -> None:
        self.task_service = task_service
        super().__init__(".".join(DBUS_INTERFACE))

    # ruff: noqa: F821
    @method()
    async def AddTask(self, payload: "s") -> "s":
        task: Any = deserialize(payload)
        logger.debug(f"Received AddTask with payload: {task}")
        await self.task_service.add_task(task)
        await self._broadcast_task_update()
        logger.info(f"Added task: {task.id} - {task.task}")
        return "ok"

    @method()
    async def DeleteTask(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received DeleteTask for ID: {task_id}")
        await self.task_service.delete_task(task_id)
        await self._broadcast_task_update()
        logger.info(f"Deleted task: {task_id}")
        return "ok"

    @method()
    async def UpdateTask(self, payload: "s") -> "s":
        task: Any = deserialize(payload)
        logger.debug(f"Received UpdateTask with payload: {task}")
        await self.task_service.update_task(task)
        await self._broadcast_task_update()
        logger.info(f"Updated task: {task.id}")
        return "ok"

    @method()
    async def MarkDone(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received MarkDone for ID: {task_id}")
        await self.task_service.mark_done(task_id)
        await self._broadcast_task_update()
        logger.info(f"Marked task done: {task_id}")
        return "ok"

    @method()
    async def MarkNotDone(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received MarkNotDone for ID: {task_id}")
        await self.task_service.mark_not_done(task_id)
        await self._broadcast_task_update()
        logger.info(f"Marked task not done: {task_id}")
        return "ok"

    @method()
    async def Toggle(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received Toggle for ID: {task_id}")
        await self.task_service.toggle_done(task_id)
        await self._broadcast_task_update()
        logger.info(f"Toggled task: {task_id}")
        return "ok"

    @method()
    async def Pin(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received Pin for ID: {task_id}")
        await self.task_service.pin_task(task_id)
        await self._broadcast_task_update()
        logger.info(f"Pinned task: {task_id}")
        return "ok"

    @method()
    async def Unpin(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received Unpin for ID: {task_id}")
        await self.task_service.unpin_task(task_id)
        await self._broadcast_task_update()
        logger.info(f"Unpinned task: {task_id}")
        return "ok"

    @method()
    async def SetDescription(self, task_id_payload: "s", desc: "s") -> "s":
        task_id: Any = deserialize(task_id_payload)
        logger.debug(f"Received SetDescription for ID: {task_id}")
        await self.task_service.set_description(task_id, desc)
        logger.info(f"Set description for task: {task_id}")
        return "ok"

    @method()
    async def GetDescription(self, payload: "s") -> "s":
        task_id: Any = deserialize(payload)
        logger.debug(f"Received GetDescription for ID: {task_id}")
        result: Any = await self.task_service.get_description(task_id)
        return result or ""

    @method()
    async def ListTasks(self) -> "s":
        tasks: Any = await self.task_service.list_tasks()
        logger.debug(f"Received ListTasks call, returning {len(tasks)} tasks")
        return serialize(tasks)

    @signal()
    def TaskUpdated(self, payload: str) -> "s":
        logger.debug("TaskUpdated signal emitted")
        return payload

    async def _broadcast_task_update(self) -> None:
        tasks: Any = await self.task_service.list_tasks()
        logger.debug(f"Broadcasting TaskUpdated signal with {len(tasks)} tasks")
        self.TaskUpdated(serialize(tasks))


class DbusServer:
    def __init__(self, task_service: TaskService) -> None:
        self.interface: DbusServerInterface = DbusServerInterface(task_service)

    async def start(self) -> None:
        self._bus: MessageBus = await MessageBus().connect()
        object_path: str = "/" + "/".join(DBUS_INTERFACE)
        self._bus.export(object_path, self.interface)
        await self._bus.request_name(".".join(DBUS_INTERFACE))
        logger.info("D-Bus server started")

    async def stop(self) -> None:
        if self._bus:
            self._bus.disconnect()
            logger.info("D-Bus server stopped")
            self._bus = None
