"""Configuration management with platformaware defaults."""

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
    Create a configuration with platformaware defaults.

    Args:
        model: Model name override.
        hotkey: Hotkey override.
        use_double_cmd: Use double RightCommand on macOS.
        languages: List of language codes.
        max_time: Maximum recording time in seconds (``None`` = unlimited).
        no_gui: Force CLI mode (disable GUI).

    Returns:
        DictationConfig: The populated configuration object.
    """
    platform = get_platform_info()

    # Model name
    if model is None:
        model = "large-v3-turbo"

    # Hotkey
    if hotkey is None:
        hotkey = "cmd_l+alt" if platform.is_macos else "ctrl+alt"

    # UI mode
    if no_gui or not platform.is_macos:
        ui_mode: Literal["gui", "cli"] = "cli"
    else:
        ui_mode = "gui" if importlib.util.find_spec("rumps") is not None else "cli"

    # Platformspecific default for max_recording_time
    if max_time is None:
        default_max_time = None  # unlimited
    elif platform.is_macos:
        default_max_time = 30.0  # macOS default is 30/s
    else:
        default_max_time = max_time  # keep the supplied default (600/s)

    # Languages
    default_language = languages[0] if languages else None

    return DictationConfig(
        model_name=model,
        hotkey=hotkey,
        use_double_cmd=use_double_cmd,
        languages=languages,
        default_language=default_language,
        max_recording_time=default_max_time,
        sample_rate=16000,
        frames_per_buffer=1024,
        ui_mode=ui_mode,
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
    # GUI only supported on macOS
    if config.ui_mode == "gui" and not config.platform.is_macos:
        raise ValueError("GUI mode is only supported on macOS")

    # .en models must be used with English only
    if ".en" in config.model_name and config.languages is not None:
        non_english = [lang for lang in config.languages if lang != "en"]
        if non_english:
            raise ValueError(
                f"Model '{config.model_name}' is Englishonly but languages "
                f"{non_english} were specified"
            )

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
