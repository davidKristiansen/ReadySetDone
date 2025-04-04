import anyio
import logging
from typing import Callable, Dict, List
from dbus_next import Message, Signal
from dbus_next.aio import MessageBus

logger = logging.getLogger(__name__)


class DbusPubsub:
    def __init__(self, bus: MessageBus, mode: str):
        """
        Initialize the D-Bus Pub/Sub system.

        Args:
            bus: The MessageBus object used to connect to D-Bus.
            mode: The mode for the pub/sub system, either 'client' or 'daemon'.
        """
        self.bus = bus
        self.mode = mode
        self.subscribers: Dict[str, List[Callable]] = {}

    async def publish(self, topic: str, data: str) -> None:
        """Publish an event to D-Bus on the specified topic."""
        if self.mode != "client":
            raise Exception("Publish operation is only available in client mode.")

        logger.info(f"Publishing to topic: {topic} with data: {data}")
        signal = Signal("/com/example/ReadySetDone", "com.example.ReadySetDone", topic)
        signal.append(data)  # Attach data to the signal
        await self.bus.send(signal)  # Send the signal

    async def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to a topic to receive events."""
        if self.mode != "daemon":
            raise Exception("Subscribe operation is only available in daemon mode.")

        logger.info(f"Subscribing to topic: {topic}")
        self.subscribers[topic] = self.subscribers.get(topic, []) + [callback]

        # Create a signal handler for the topic
        def signal_handler(message: Message):
            # Extract the data and call the callback
            data = message.body[0]  # Assuming data is in the first position
            callback(data)

        self.bus.on_signal(topic, signal_handler)

    async def start(self) -> None:
        """Start the D-Bus connection."""
        logger.info(f"Starting D-Bus connection in {self.mode} mode...")
        await self.bus.connect()

    async def stop(self) -> None:
        """Stop the D-Bus connection."""
        logger.info("Stopping D-Bus connection...")
        await self.bus.disconnect()


class PubSubBuilder:
    def __init__(self):
        """Initialize the PubSub builder."""
        self.bus = MessageBus()  # Initialize D-Bus connection (using dbus-next)
        self.mode = None

    def set_mode(self, mode: str) -> "PubSubBuilder":
        """Set the mode for the pub/sub system ('client' or 'daemon')."""
        self.mode = mode
        return self

    def build(self) -> DbusPubsub:
        """Build and return the DbusPubsub instance."""
        if self.mode not in ["client", "daemon"]:
            raise ValueError("Invalid mode. Must be 'client' or 'daemon'.")
        return DbusPubsub(self.bus, self.mode)
