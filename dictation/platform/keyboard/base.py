"""Abstract base class for keyboard listeners."""

from abc import ABC, abstractmethod
from collections.abc import Callable


class KeyboardListener(ABC):
    """Abstract base class for keyboard input listeners."""

    @abstractmethod
    def start(self, on_hotkey: Callable[[], None]) -> None:
        """
        Start listening for keyboard events.

        Args:
            on_hotkey: Callback function to call when the hotkey is pressed
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop listening for keyboard events."""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the listener is currently running.

        Returns:
            bool: True if running, False otherwise
        """
        pass
