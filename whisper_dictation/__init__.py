"""
Whisper Dictation - Cross-platform multilingual dictation using OpenAI Whisper.

This package provides a unified interface for speech-to-text dictation across
macOS (Intel & Apple Silicon) and Linux (X11 & Wayland).
"""

__version__ = "1.0.0"

from .config import DictationConfig, create_default_config
from .core.recorder import Recorder
from .core.transcriber import StandardWhisperTranscriber, WhisperTranscriber
from .platform.detection import PlatformInfo, detect_platform, get_platform_info


__all__ = [
    "DictationConfig",
    "PlatformInfo",
    "Recorder",
    "StandardWhisperTranscriber",
    "WhisperTranscriber",
    "__version__",
    "create_default_config",
    "detect_platform",
    "get_platform_info",
]
