"""Keyboard listener implementation using evdev (Linux)."""

import threading
from collections.abc import Callable

from .base import KeyboardListener


class EvdevKeyboardListener(KeyboardListener):
    """Keyboard listener using evdev library (Linux)."""

    def __init__(self, key_combination: str = "ctrl+alt"):
        """
        Initialize evdev keyboard listener.

        Args:
            key_combination: Key combination string (e.g., "ctrl+alt")
        """
        try:
            import evdev
            from evdev import InputDevice, categorize, ecodes
        except ImportError:
            raise ImportError(
                "evdev is not installed. Install it with: uv sync --extra linux"
            ) from None

        self.evdev = evdev
        self.categorize = categorize
        self.ecodes = ecodes
        self.InputDevice = InputDevice

        self.key_combination = key_combination
        self._keyboard_device: InputDevice | None = None
        self._listener_thread: threading.Thread | None = None
        self._stop_flag = False
        self._on_hotkey: Callable[[], None] | None = None

    def start(self, on_hotkey: Callable[[], None]) -> None:
        """Start listening for keyboard events."""
        if self._listener_thread is not None:
            raise RuntimeError("Listener is already running")

        # Find keyboard device
        keyboard_path = self._find_keyboard()
        if keyboard_path is None:
            raise RuntimeError(
                "No keyboard device found. Make sure you have read access to /dev/input/event*"
            )

        self._keyboard_device = self.InputDevice(keyboard_path)
        self._on_hotkey = on_hotkey
        self._stop_flag = False

        # Start listening thread
        self._listener_thread = threading.Thread(target=self._listen)
        self._listener_thread.daemon = True
        self._listener_thread.start()

    def stop(self) -> None:
        """Stop listening for keyboard events."""
        self._stop_flag = True
        if self._listener_thread is not None:
            self._listener_thread.join(timeout=1.0)
            self._listener_thread = None
        if self._keyboard_device is not None:
            self._keyboard_device.close()
            self._keyboard_device = None

    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self._listener_thread is not None and self._listener_thread.is_alive()

    def _find_keyboard(self) -> str | None:
        """Find a keyboard device from /dev/input/event*."""
        devices = [self.InputDevice(path) for path in self.evdev.list_devices()]

        for device in devices:
            capabilities = device.capabilities()
            if self.ecodes.EV_KEY in capabilities:
                keys = capabilities[self.ecodes.EV_KEY]
                # Look for keys that are standard on keyboards
                if self.ecodes.KEY_A in keys and self.ecodes.KEY_LEFTCTRL in keys:
                    return device.path

        return None

    def _listen(self) -> None:
        """Internal method that listens for keyboard events."""
        if self._keyboard_device is None:
            return

        # Parse key combination
        key1_name, key2_name = self.key_combination.split("+")
        key1_codes = self._get_key_codes(key1_name)
        key2_codes = self._get_key_codes(key2_name)

        key1_pressed = False
        key2_pressed = False
        combo_active = False

        print(
            f"[*] Listening for {self.key_combination} on {self._keyboard_device.path}"
        )

        try:
            for event in self._keyboard_device.read_loop():
                if self._stop_flag:
                    break

                if event.type == self.ecodes.EV_KEY:
                    key_event = self.categorize(event)
                    keycode = (
                        key_event.keycode
                        if isinstance(key_event.keycode, str)
                        else key_event.keycode[0]
                    )

                    # Check key down events
                    if key_event.keystate == key_event.key_down:
                        if keycode in key1_codes:
                            key1_pressed = True
                        elif keycode in key2_codes:
                            key2_pressed = True

                    # Check key up events
                    elif key_event.keystate == key_event.key_up:
                        if keycode in key1_codes:
                            key1_pressed = False
                        elif keycode in key2_codes:
                            key2_pressed = False

                    # Detect combo press
                    if key1_pressed and key2_pressed:
                        if not combo_active:
                            combo_active = True
                            if self._on_hotkey is not None:
                                self._on_hotkey()
                    else:
                        combo_active = False

        except OSError:
            # Device was closed
            pass

    def _get_key_codes(self, key_name: str) -> list[str]:
        """Get evdev key codes for a key name."""
        key_map = {
            "ctrl": ["KEY_LEFTCTRL", "KEY_RIGHTCTRL"],
            "alt": ["KEY_LEFTALT", "KEY_RIGHTALT"],
            "shift": ["KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"],
            "super": ["KEY_LEFTMETA", "KEY_RIGHTMETA"],
            "cmd": ["KEY_LEFTMETA", "KEY_RIGHTMETA"],
        }

        return key_map.get(key_name.lower(), [f"KEY_{key_name.upper()}"])
