Architecture Overview
=====================

ReadySetDone separates task logic and backend systems cleanly. Here's the layered architecture:

Layers
------

- **api/**: defines what operations are supported (e.g. add, list, mark_done)
- **service/**: implements those operations (filesystem, memory, etc.)
- **pubsub/**: handles how updates are broadcast (e.g. D-Bus pub/sub)
- **daemon/**: receives commands, applies them, and publishes updates
- **client/**: talks to daemon via pubsub; never touches files directly

Execution Flows
---------------

Daemon Mode:

.. code-block::

   [D-Bus call] ---> [Daemon handler] ---> [API impl] --> [task_service] --> [fs_store]
                                                           |
                                                           |---> if change → [pubsub.publish()]

Client Mode:

.. code-block::

   [CLI / TUI] ---> [dbus_pubsub.send_call()] --> daemon
                                            ↳ daemon applies mutation and broadcasts update
