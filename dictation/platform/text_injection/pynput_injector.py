"""Text injection implementation using pynput (macOS/X11)."""

import time

from pynput import keyboard

from .base import TextInjector


class PynputTextInjector(TextInjector):
    """Text injector using pynput library (works on macOS and X11)."""

    def __init__(self, char_delay: float = 0.0025):
        """
        Initialize pynput text injector.

        Args:
            char_delay: Delay between characters in seconds (default: 0.0025)
        """
        self.char_delay = char_delay
        self.keyboard_controller = keyboard.Controller()

    def inject_text(self, text: str) -> None:
        """
        Inject text into the currently active window.

        Args:
            text: The text to inject (should be pre-normalized)
        """
        # Type each character with a small delay
        for char in text:
            try:
                self.keyboard_controller.type(char)
                if self.char_delay > 0:
                    time.sleep(self.char_delay)
            except Exception as e:
                print(f"Error typing character '{char}': {e}")
