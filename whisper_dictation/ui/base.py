"""Abstract base class for user interfaces."""

from abc import ABC, abstractmethod


class DictationUI(ABC):
    """Abstract base class for dictation user interfaces."""

    @abstractmethod
    def run(self) -> None:
        """
        Run the UI (blocking).

        This method should block until the application is terminated.
        """
        pass

    @abstractmethod
    def on_recording_start(self) -> None:
        """Called when recording starts."""
        pass

    @abstractmethod
    def on_recording_stop(self) -> None:
        """Called when recording stops."""
        pass

    @abstractmethod
    def on_transcription_complete(self, text: str) -> None:
        """
        Called when transcription completes.

        Args:
            text: The transcribed text
        """
        pass

    @abstractmethod
    def on_error(self, error: str) -> None:
        """
        Called when an error occurs.

        Args:
            error: Error message
        """
        pass
