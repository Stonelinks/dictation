"""Keyboard listener implementation using pynput (macOS/X11)."""

import time
from collections.abc import Callable

from pynput import keyboard

from .base import KeyboardListener


class PynputKeyboardListener(KeyboardListener):
    """Keyboard listener using pynput library (works on macOS and X11)."""

    def __init__(self, key_combination: str = "cmd_l+alt"):
        """
        Initialize pynput keyboard listener.

        Args:
            key_combination: Key combination string (e.g., "cmd_l+alt", "ctrl+alt")
        """
        self.key_combination = key_combination
        self._listener: keyboard.Listener | None = None
        self._on_hotkey: Callable[[], None] | None = None
        self._key_handler: _KeyComboHandler | None = None

    def start(self, on_hotkey: Callable[[], None]) -> None:
        """Start listening for keyboard events."""
        if self._listener is not None:
            raise RuntimeError("Listener is already running")

        self._on_hotkey = on_hotkey
        self._key_handler = _KeyComboHandler(self.key_combination, on_hotkey)

        self._listener = keyboard.Listener(
            on_press=self._key_handler.on_key_press,
            on_release=self._key_handler.on_key_release,
        )
        self._listener.start()

    def stop(self) -> None:
        """Stop listening for keyboard events."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            self._key_handler = None

    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self._listener is not None


class PynputDoubleCommandListener(KeyboardListener):
    """
    Keyboard listener for double Right-Command key on macOS.

    Double-press Right-Cmd to start, single-press to stop.
    """

    def __init__(self):
        """Initialize double-command keyboard listener."""
        self._listener: keyboard.Listener | None = None
        self._on_hotkey: Callable[[], None] | None = None
        self._key_handler: _DoubleCommandHandler | None = None

    def start(self, on_hotkey: Callable[[], None]) -> None:
        """Start listening for keyboard events."""
        if self._listener is not None:
            raise RuntimeError("Listener is already running")

        self._on_hotkey = on_hotkey
        self._key_handler = _DoubleCommandHandler(on_hotkey)

        self._listener = keyboard.Listener(
            on_press=self._key_handler.on_key_press,
            on_release=self._key_handler.on_key_release,
        )
        self._listener.start()

    def stop(self) -> None:
        """Stop listening for keyboard events."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            self._key_handler = None

    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self._listener is not None


class _KeyComboHandler:
    """Internal handler for key combination events."""

    def __init__(self, key_combination: str, callback: Callable[[], None]):
        """
        Initialize key combination handler.

        Args:
            key_combination: Key combination string (e.g., "cmd_l+alt")
            callback: Callback function to call when combination is pressed
        """
        self.callback = callback
        self.key1, self.key2 = self._parse_key_combination(key_combination)
        self.key1_pressed = False
        self.key2_pressed = False
        self.combo_triggered = False
        self.last_trigger_time = 0
        self.debounce_delay = 0.15  # Minimum time between triggers in seconds

    def _parse_key_combination(self, key_combination: str) -> tuple:
        """Parse key combination string into pynput key objects."""
        key1_name, key2_name = key_combination.split("+")

        # Try to get from keyboard.Key enum first
        key1 = getattr(keyboard.Key, key1_name, None)
        if key1 is None:
            key1 = keyboard.KeyCode.from_char(key1_name)

        key2 = getattr(keyboard.Key, key2_name, None)
        if key2 is None:
            key2 = keyboard.KeyCode.from_char(key2_name)

        return key1, key2

    def on_key_press(self, key):
        """Handle key press events."""
        if key == self.key1:
            self.key1_pressed = True
        elif key == self.key2:
            self.key2_pressed = True

        # Trigger callback when both keys are pressed
        if self.key1_pressed and self.key2_pressed and not self.combo_triggered:
            current_time = time.time()
            # Only trigger if enough time has passed since last trigger
            if current_time - self.last_trigger_time >= self.debounce_delay:
                self.combo_triggered = True
                self.last_trigger_time = current_time
                self.callback()

    def on_key_release(self, key):
        """Handle key release events."""
        if key == self.key1:
            self.key1_pressed = False
        elif key == self.key2:
            self.key2_pressed = False

        # Reset combo trigger when keys are released
        if not self.key1_pressed or not self.key2_pressed:
            self.combo_triggered = False
            self.last_trigger_time = 0


class _DoubleCommandHandler:
    """Internal handler for double Right-Command key events."""

    def __init__(self, callback: Callable[[], None]):
        """
        Initialize double command handler.

        Args:
            callback: Callback function to call when double-command is detected
        """
        self.callback = callback
        self.key = keyboard.Key.cmd_r
        self.last_press_time = 0
        self.is_recording = False

    def on_key_press(self, key):
        """Handle key press events."""
        if key == self.key:
            current_time = time.time()

            if not self.is_recording:
                # Check for double press (within 0.5 seconds)
                if current_time - self.last_press_time < 0.5:
                    self.is_recording = True
                    self.callback()
            else:
                # Single press to stop
                self.is_recording = False
                self.callback()

            self.last_press_time = current_time

    def on_key_release(self, key):
        """Handle key release events."""
        pass
