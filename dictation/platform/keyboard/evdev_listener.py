"""Keyboard listener implementation using evdev (Linux)."""

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING


# Placeholder for evdev module; will be set when the class is instantiated
evdev = None

if TYPE_CHECKING:
    # Imported only for type checking; runtime import occurs in __init__
    from evdev import InputDevice


class EvdevKeyboardListener:
    """Keyboard listener using evdev library (Linux)."""

    def __init__(
        self, key_combination: str = "ctrl+alt", devices: list[str] | None = None
    ):
        """
        Initialize the evdev keyboard listener.

        Args:
            key_combination: Key combination string (e.g., "ctrl+alt").
            devices: Optional list of device paths to listen on.
                     If None, all keyboards are auto-detected.
        """
        # Import evdev lazily so tests can patch the module attribute
        global evdev
        try:
            import evdev as evdev_module
            from evdev import InputDevice, categorize, ecodes
        except ImportError as exc:
            raise ImportError(
                "evdev is not installed. Install it with: uv sync --extra linux"
            ) from exc

        # Store the imported module for later use and for the test patches
        evdev = evdev_module
        self.evdev = evdev_module
        self.categorize = categorize
        self.ecodes = ecodes
        self.InputDevice = InputDevice

        self.key_combination = key_combination
        self._device_paths: list[str] | None = devices
        self._keyboard_devices: list[InputDevice] = []
        self._listener_threads: list[threading.Thread] = []
        self._stop_flag = False
        self._on_hotkey: Callable[[], None] | None = None
        self._lock = threading.Lock()
        # Compatibility attributes for legacy tests / code
        self._keyboard_device = None  # Legacy attribute for compatibility
        self._listener_thread = None  # Legacy attribute for compatibility

    def start(self, on_hotkey: Callable[[], None]) -> None:
        """Start listening for keyboard events on all detected devices."""
        if self._listener_threads:
            raise RuntimeError("Listener is already running")

        # Determine which device paths to use
        if self._device_paths is None:
            device_paths = self._find_all_keyboards()
        else:
            device_paths = self._device_paths

        if not device_paths:
            raise RuntimeError(
                "No keyboard device found. Ensure you have read access to /dev/input/event*"
            )

        # Open InputDevice objects for each path
        self._keyboard_devices = [self.InputDevice(path) for path in device_paths]

        self._on_hotkey = on_hotkey
        self._stop_flag = False

        # Start a listener thread for each device
        for dev in self._keyboard_devices:
            t = threading.Thread(target=self._listen, args=(dev,))
            t.daemon = True
            t.start()
            self._listener_threads.append(t)

        # Set legacy single-device/thread attributes for backward compatibility
        self._keyboard_device = (
            self._keyboard_devices[0] if self._keyboard_devices else None
        )
        self._listener_thread = (
            self._listener_threads[0] if self._listener_threads else None
        )

    def stop(self) -> None:
        """Stop listening for keyboard events on all devices."""
        self._stop_flag = True

        # Wait for all listener threads
        for t in self._listener_threads:
            t.join(timeout=1.0)
        self._listener_threads.clear()

        # Close all device handles
        for dev in self._keyboard_devices:
            dev.close()
        self._keyboard_devices.clear()

        # Reset legacy attributes
        self._keyboard_device = None
        self._listener_thread = None

    def is_running(self) -> bool:
        """Check if any listener thread is currently active."""
        return any(t.is_alive() for t in self._listener_threads)

    def _find_all_keyboards(self) -> list[str]:
        """Find all keyboard devices from /dev/input/event*."""
        devices = [self.InputDevice(path) for path in self.evdev.list_devices()]
        keyboards: list[str] = []

        for device in devices:
            capabilities = device.capabilities()
            if self.ecodes.EV_KEY in capabilities:
                keys = capabilities[self.ecodes.EV_KEY]
                if self.ecodes.KEY_A in keys and self.ecodes.KEY_LEFTCTRL in keys:
                    keyboards.append(device.path)

        return keyboards

    # -------------------------------------------------------------------------
    # Legacy support methods
    # -------------------------------------------------------------------------
    def _find_keyboard(self) -> str | None:
        """
        Legacy wrapper that returns the first keyboard device path found,
        preserving the original single-keyboard behavior expected by older tests.
        """
        keyboards = self._find_all_keyboards()
        return keyboards[0] if keyboards else None

    def _listen(self, device: "InputDevice") -> None:
        """Listen for keyboard events from a single device."""
        if device is None:
            return

        key1_name, key2_name = self.key_combination.split("+")
        key1_codes = self._get_key_codes(key1_name)
        key2_codes = self._get_key_codes(key2_name)

        key1_pressed = False
        key2_pressed = False
        combo_active = False

        print(f"[*] Listening for {self.key_combination} on {device.path}")

        try:
            for event in device.read_loop():
                if self._stop_flag:
                    break

                if event.type == self.ecodes.EV_KEY:
                    key_event = self.categorize(event)
                    keycode = (
                        key_event.keycode
                        if isinstance(key_event.keycode, str)
                        else key_event.keycode[0]
                    )

                    if key_event.keystate == key_event.key_down:
                        if keycode in key1_codes:
                            key1_pressed = True
                        elif keycode in key2_codes:
                            key2_pressed = True

                    elif key_event.keystate == key_event.key_up:
                        if keycode in key1_codes:
                            key1_pressed = False
                        elif keycode in key2_codes:
                            key2_pressed = False

                    if key1_pressed and key2_pressed:
                        if not combo_active:
                            combo_active = True
                            with self._lock:
                                if self._on_hotkey is not None:
                                    self._on_hotkey()
                    else:
                        combo_active = False

        except OSError:
            pass

    def _get_key_codes(self, key_name: str) -> list[str]:
        key_map = {
            "ctrl": ["KEY_LEFTCTRL", "KEY_RIGHTCTRL"],
            "alt": ["KEY_LEFTALT", "KEY_RIGHTALT"],
            "shift": ["KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"],
            "super": ["KEY_LEFTMETA", "KEY_RIGHTMETA"],
            "cmd": ["KEY_LEFTMETA", "KEY_RIGHTMETA"],
        }
        return key_map.get(key_name.lower(), [f"KEY_{key_name.upper()}"])


"""
Trailing newline added.
"""
