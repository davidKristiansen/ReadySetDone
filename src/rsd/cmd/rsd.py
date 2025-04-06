# SPDX-License-Identifier: MIT
# Copyright David Kristiansen

"""
Client entrypoint for ReadySetDone (`rsd`).
Responsible for sending task operations to the daemon and rendering UI.
"""

import logging

import anyio

from rsd.api import get_task_id_by_index
from rsd.api.types import Task
from rsd.config import Config
from rsd.config.args import Args
from rsd.ipc import get_ipc_client
from rsd.logger import setup_logger
from rsd.ui import get_ui

logger = logging.getLogger(__name__)


async def async_main() -> None:
    args = Args()
    config = Config(path=args.config_path, args=args, mode=args.mode)
    setup_logger(level=config.log_level, color=config.color)

    if args.mode == "tui":
        logger.info("TUI not yet implemented")
        return

    ui = get_ui("cli", config.ui_mode)
    ipc = get_ipc_client()
    await ipc.start()

    id = None
    if args.index:
        try:
            id = get_task_id_by_index(await ipc.list_tasks(), args.index)
        except IndexError:
            logger.warning(f"No task found at index {args.index}")

    match args.command:
        case "add":
            task = Task.new(args.task)
            if args.done:
                task.done = True
            if args.pin:
                task.pinned = True
            await ipc.add_task(task)
        case "delete":
            if id:
                await ipc.delete_task(id)
        case "toggle":
            if id:
                await ipc.toggle(id)
        case "not-done":
            if id:
                await ipc.mark_not_done(id)
        case "done":
            if id:
                await ipc.mark_done(id)
        case "pin":
            if id:
                await ipc.pin(id)
        case "unpin":
            if id:
                await ipc.unpin(id)
        case "description":
            if id:
                desc = await ipc.get_description(id)
                ui.render_description(desc)
                return
        case "list" | _:
            pass  # list is the default fallback

    tasks = await ipc.list_tasks()
    ui.render(tasks=tasks, color=config.color, metadata=args.metadata)


def main() -> None:
    # try:
    anyio.run(async_main)
    # except KeyboardInterrupt:
    #     sys.exit(0)
    # except Exception:
    #     logger.exception("Client exited with error")
    #     sys.exit(1)


if __name__ == "__main__":
    main()
