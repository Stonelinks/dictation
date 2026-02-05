"""Configuration management with platform-aware defaults."""

import importlib.util
from dataclasses import dataclass

from .platform.detection import PlatformInfo, get_platform_info


DEFAULT_MODEL = "Qwen/Qwen3-ASR-0.6B"


@dataclass
class DictationConfig:
    """Configuration for the dictation application."""

    # Model settings
    model_name: str

    # Hotkey settings
    hotkey: str

    # Language settings
    languages: list[str] | None
    default_language: str | None

    # Recording settings
    max_recording_time: float | None
    sample_rate: int
    frames_per_buffer: int

    # Platform info
    platform: PlatformInfo


def create_default_config(
    model: str | None = None,
    hotkey: str | None = None,
    languages: list[str] | None = None,
    max_time: float | None = 600.0,
) -> DictationConfig:
    """
    Create a configuration with platform-aware defaults.

    Args:
        model: Model name override.
        hotkey: Hotkey override.
        languages: List of language codes.
        max_time: Maximum recording time in seconds (``None`` = unlimited).

    Returns:
        DictationConfig: The populated configuration object.
    """
    platform = get_platform_info()

    if model is None:
        model = DEFAULT_MODEL

    # Hotkey
    if hotkey is None:
        hotkey = "cmd_l+alt" if platform.is_macos else "ctrl+alt"

    # Languages
    default_language = languages[0] if languages else None

    return DictationConfig(
        model_name=model,
        hotkey=hotkey,
        languages=languages,
        default_language=default_language,
        max_recording_time=max_time,
        sample_rate=16000,
        frames_per_buffer=1024,
        platform=platform,
    )


def validate_config(config: DictationConfig) -> None:
    """
    Validate a configuration and raise errors for invalid settings.

    Args:
        config: Configuration to validate.

    Raises:
        ValueError: If the configuration is invalid.
    """
    # Wayland requires ydotool
    if config.platform.is_wayland:
        import shutil

        if not shutil.which("ydotool"):
            print(
                "[!] Warning: ydotool is not installed. Text injection may not work on Wayland."
            )

    # Linux requires evdev
    if config.platform.is_linux and importlib.util.find_spec("evdev") is None:
        print(
            "[!] Warning: evdev is not installed. Install it with: uv sync --extra linux"
        )
