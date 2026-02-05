"""Text injection implementation using ydotool (Wayland)."""

import shutil
import subprocess

from .base import TextInjector


class YdotoolTextInjector(TextInjector):
    """Text injector using ydotool (works on Wayland)."""

    def __init__(self):
        """Initialize ydotool text injector."""
        # Check if ydotool is available
        if not shutil.which("ydotool"):
            raise RuntimeError(
                "ydotool is not installed or not found in PATH. "
                "Install it with your package manager (e.g., 'sudo apt install ydotool')"
            )

    def inject_text(self, text: str) -> None:
        """
        Inject text into the currently active window using ydotool.

        Args:
            text: The text to inject (should be pre-normalized)
        """
        if not text:
            return

        try:
            subprocess.run(["ydotool", "type", text], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to inject text with ydotool: {e}")
        except Exception as e:
            print(f"Error injecting text: {e}")
