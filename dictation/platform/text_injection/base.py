"""Abstract base class for text injection."""

from abc import ABC, abstractmethod


class TextInjector(ABC):
    """Abstract base class for injecting text into the active window."""

    @abstractmethod
    def inject_text(self, text: str) -> None:
        """
        Inject text into the currently active window.

        Args:
            text: The text to inject
        """
        pass
