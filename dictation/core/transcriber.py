"""Abstract base class and implementations for speech-to-text transcription."""

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# Language code mapping from ISO 639-1 to full language names for Qwen3-ASR
LANGUAGE_MAP = {
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "cs": "Czech",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "he": "Hebrew",
    "el": "Greek",
    "ro": "Romanian",
    "hu": "Hungarian",
    "sk": "Slovak",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "et": "Estonian",
    "sl": "Slovenian",
    "ca": "Catalan",
}

SAMPLE_RATE = 16000


class Transcriber(ABC):
    """Abstract base class for speech-to-text transcription."""

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


class Qwen3Transcriber(Transcriber):
    """Transcriber using Qwen3-ASR via transformers.

    On Apple Silicon, PyTorch automatically uses MPS (Metal) for GPU acceleration.
    """

    def __init__(self, model_name: str = "Qwen/Qwen3-ASR-0.6B"):
        """
        Initialize Qwen3-ASR transcriber.

        Args:
            model_name: Qwen3-ASR model name from HuggingFace
        """
        try:
            from qwen_asr import Qwen3ASRModel
        except ImportError:
            raise ImportError(
                "qwen-asr is not installed. Install it with: uv sync"
            ) from None

        self._model_name = model_name
        self.model = Qwen3ASRModel.from_pretrained(model_name)

    def transcribe(
        self, audio: NDArray[np.float32], language: str | None = None
    ) -> str:
        """Transcribe audio using Qwen3-ASR."""
        lang_name = LANGUAGE_MAP.get(language) if language else None

        results = self.model.transcribe((audio, SAMPLE_RATE), language=lang_name)
        if results:
            return results[0].text.strip()
        return ""

    def get_model_name(self) -> str:
        """Get the Qwen3-ASR model name."""
        return self._model_name
