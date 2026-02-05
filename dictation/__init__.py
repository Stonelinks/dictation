"""
Dictation - Cross-platform multilingual dictation powered by Qwen3-ASR.

This package provides a unified interface for speech-to-text dictation across
macOS (Intel & Apple Silicon) and Linux (X11 & Wayland).
"""

__version__ = "2.0.0"

from .config import DictationConfig, create_default_config
from .core.recorder import Recorder
from .core.transcriber import Qwen3Transcriber, Transcriber
from .platform.detection import PlatformInfo, detect_platform, get_platform_info


__all__ = [
    "DictationConfig",
    "PlatformInfo",
    "Qwen3Transcriber",
    "Recorder",
    "Transcriber",
    "__version__",
    "create_default_config",
    "detect_platform",
    "get_platform_info",
]
