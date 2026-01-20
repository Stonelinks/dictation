"""Abstract base class and implementations for Whisper transcription."""

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class WhisperTranscriber(ABC):
    """Abstract base class for Whisper transcription."""

    @abstractmethod
    def transcribe(
        self, audio: NDArray[np.float32], language: str | None = None
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Audio data as float32 array normalized to [-1, 1]
            language: Language code (e.g., 'en', 'es', 'fr') or None for auto-detect

        Returns:
            str: Transcribed text
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the loaded model.

        Returns:
            str: Model name
        """
        pass


class StandardWhisperTranscriber(WhisperTranscriber):
    """Whisper transcriber using faster-whisper backend."""

    def __init__(self, model_name: str = "large-v3"):
        """
        Initialize faster-whisper transcriber.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large, etc.)
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper is not installed. Install it with: "
                "uv sync --extra macos (or --extra linux)"
            ) from None

        self.model_name = model_name
        # Use CPU for compatibility (can be changed to "cuda" on NVIDIA GPUs)
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe(
        self, audio: NDArray[np.float32], language: str | None = None
    ) -> str:
        """Transcribe audio using faster-whisper."""
        segments, _info = self.model.transcribe(audio, language=language)
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def get_model_name(self) -> str:
        """Get the faster-whisper model name."""
        return self.model_name
