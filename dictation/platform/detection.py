"""Platform detection for cross-platform compatibility."""

import os
import platform
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class PlatformInfo:
    """Information about the current platform."""

    os_name: str
    is_macos: bool
    is_linux: bool
    is_windows: bool
    is_apple_silicon: bool
    session_type: Literal["wayland", "x11"] | None

    @property
    def is_wayland(self) -> bool:
        """Check if running on Wayland."""
        return self.session_type == "wayland"

    @property
    def is_x11(self) -> bool:
        """Check if running on X11."""
        return self.session_type == "x11"


def _detect_apple_silicon() -> bool:
    """Detect if running on Apple Silicon (M1/M2/M3/etc)."""
    if platform.system() != "Darwin":
        return False

    machine = platform.machine().lower()
    # Apple Silicon reports as 'arm64'
    return machine == "arm64"


def _detect_session_type() -> Literal["wayland", "x11"] | None:
    """Detect Linux session type (Wayland or X11)."""
    if platform.system() != "Linux":
        return None

    # Check XDG_SESSION_TYPE environment variable
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session_type == "wayland":
        return "wayland"
    elif session_type == "x11":
        return "x11"

    # Fallback: check WAYLAND_DISPLAY
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"

    # Fallback: check DISPLAY (X11)
    if os.environ.get("DISPLAY"):
        return "x11"

    return None


def detect_platform() -> PlatformInfo:
    """
    Detect the current platform and its capabilities.

    Returns:
        PlatformInfo: Information about the current platform
    """
    os_name = platform.system()
    is_macos = os_name == "Darwin"
    is_linux = os_name == "Linux"
    is_windows = os_name == "Windows"
    is_apple_silicon = _detect_apple_silicon()
    session_type = _detect_session_type()

    return PlatformInfo(
        os_name=os_name,
        is_macos=is_macos,
        is_linux=is_linux,
        is_windows=is_windows,
        is_apple_silicon=is_apple_silicon,
        session_type=session_type,
    )


# Global platform info instance
_platform_info: PlatformInfo | None = None


def get_platform_info() -> PlatformInfo:
    """
    Get the cached platform information.

    Returns:
        PlatformInfo: Information about the current platform
    """
    global _platform_info
    if _platform_info is None:
        _platform_info = detect_platform()
    return _platform_info
