"""Configuration management with platform-aware defaults."""

import importlib.util
from dataclasses import dataclass
from typing import Literal

from .platform.detection import PlatformInfo, get_platform_info


@dataclass
class DictationConfig:
    """Configuration for the dictation application."""

    # Model settings
    model_name: str

    # Hotkey settings
    hotkey: str
    use_double_cmd: bool

    # Language settings
    languages: list[str] | None
    default_language: str | None

    # Recording settings
    max_recording_time: float | None
    sample_rate: int
    frames_per_buffer: int

    # UI settings
    ui_mode: Literal["gui", "cli"]

    # Platform info
    platform: PlatformInfo


def create_default_config(
    model: str | None = None,
    hotkey: str | None = None,
    use_double_cmd: bool = False,
    languages: list[str] | None = None,
    max_time: float | None = 600.0,
    no_gui: bool = False,
) -> DictationConfig:
    """
    Create a configuration with platform-aware defaults.

    Args:
        model: Model name override
        hotkey: Hotkey override
        use_double_cmd: Use double Right-Command on macOS
        languages: List of language codes
        max_time: Maximum recording time in seconds
        no_gui: Force CLI mode (disable GUI)

    Returns:
        DictationConfig: Configuration object
    """
    platform = get_platform_info()

    # Determine model name
    if model is None:
        model = "large-v3-turbo"

    # Determine hotkey
    if hotkey is None:
        if platform.is_macos:
            hotkey = "cmd_l+alt"
        else:
            hotkey = "ctrl+alt"

    # Determine UI mode
    ui_mode: Literal["gui", "cli"]
    if no_gui or not platform.is_macos:
        ui_mode = "cli"
    else:
        # Try to use GUI on macOS if rumps is available
        if importlib.util.find_spec("rumps") is not None:
            ui_mode = "gui"
        else:
            ui_mode = "cli"

    # Parse languages
    default_language = None
    if languages is not None and len(languages) > 0:
        default_language = languages[0]

    return DictationConfig(
        model_name=model,
        hotkey=hotkey,
        use_double_cmd=use_double_cmd,
        languages=languages,
        default_language=default_language,
        max_recording_time=max_time,
        sample_rate=16000,
        frames_per_buffer=1024,
        ui_mode=ui_mode,
        platform=platform,
    )


def validate_config(config: DictationConfig) -> None:
    """
    Validate configuration and raise errors for invalid settings.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    # Check if GUI is requested but not supported
    if config.ui_mode == "gui" and not config.platform.is_macos:
        raise ValueError("GUI mode is only supported on macOS")

    # Check language compatibility with .en models
    if ".en" in config.model_name and config.languages is not None:
        non_english = [lang for lang in config.languages if lang != "en"]
        if non_english:
            raise ValueError(
                f"Model '{config.model_name}' is English-only but languages "
                f"{non_english} were specified"
            )

    # Check if ydotool is needed on Wayland
    if config.platform.is_wayland:
        import shutil

        if not shutil.which("ydotool"):
            print(
                "[!] Warning: ydotool is not installed. Text injection may not work on Wayland."
            )

    # Check if evdev is needed on Linux
    if config.platform.is_linux and importlib.util.find_spec("evdev") is None:
        print(
            "[!] Warning: evdev is not installed. Install it with: uv sync --extra linux"
        )
