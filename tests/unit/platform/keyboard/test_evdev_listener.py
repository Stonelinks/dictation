"""Unit tests for evdev keyboard listener module."""

import sys
from unittest.mock import MagicMock, patch

import pytest


# Skip all tests in this module on non-Linux platforms
pytestmark = [
    pytest.mark.unit,
    pytest.mark.linux,
    pytest.mark.skipif(sys.platform != "linux", reason="evdev is Linux-only"),
]

# Only import on Linux to avoid ImportError
if sys.platform == "linux":
    from whisper_dictation.platform.keyboard.evdev_listener import EvdevKeyboardListener
else:
    EvdevKeyboardListener = None


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerInitialization:
    """Tests for EvdevKeyboardListener initialization."""

    def test_default_initialization(self, mock_evdev):
        """Test initialization with default parameters."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            assert listener.key_combination == "ctrl+alt"
            assert listener._keyboard_device is None
            assert listener._listener_thread is None

    def test_custom_key_combination(self, mock_evdev):
        """Test initialization with custom key combination."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener(key_combination="ctrl+shift")

            assert listener.key_combination == "ctrl+shift"

    def test_initialization_without_evdev_raises_error(self):
        """Test that missing evdev raises ImportError."""
        with (
            patch("builtins.__import__", side_effect=ImportError),
            pytest.raises(ImportError, match="evdev is not installed"),
        ):
            EvdevKeyboardListener()


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerFindKeyboard:
    """Tests for _find_keyboard method."""

    def test_find_keyboard_success(self, mock_evdev):
        """Test finding a keyboard device."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device capabilities
            mock_device = MagicMock()
            mock_device.path = "/dev/input/event0"
            mock_device.capabilities.return_value = {
                mock_evdev["ecodes"].EV_KEY: [
                    mock_evdev["ecodes"].KEY_A,
                    mock_evdev["ecodes"].KEY_LEFTCTRL,
                ]
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            keyboard_path = listener._find_keyboard()

            assert keyboard_path == "/dev/input/event0"

    def test_find_keyboard_no_devices(self, mock_evdev):
        """Test when no devices are found."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            mock_evdev["list_devices"].return_value = []

            listener = EvdevKeyboardListener()
            keyboard_path = listener._find_keyboard()

            assert keyboard_path is None

    def test_find_keyboard_no_keyboard_device(self, mock_evdev):
        """Test when devices exist but none are keyboards."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device without keyboard keys
            mock_device = MagicMock()
            mock_device.capabilities.return_value = {
                123: []  # Not EV_KEY
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            keyboard_path = listener._find_keyboard()

            assert keyboard_path is None


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerStart:
    """Tests for start method."""

    def test_start_finds_keyboard_and_starts_thread(self, mock_evdev):
        """Test that start finds keyboard and starts listening thread."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device capabilities
            mock_device = MagicMock()
            mock_device.path = "/dev/input/event0"
            mock_device.capabilities.return_value = {
                mock_evdev["ecodes"].EV_KEY: [
                    mock_evdev["ecodes"].KEY_A,
                    mock_evdev["ecodes"].KEY_LEFTCTRL,
                ]
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            callback = MagicMock()

            listener.start(callback)

            assert listener._listener_thread is not None
            assert listener._on_hotkey is callback
            assert listener._keyboard_device is not None

    def test_start_twice_raises_error(self, mock_evdev):
        """Test that starting twice raises RuntimeError."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device
            mock_device = MagicMock()
            mock_device.path = "/dev/input/event0"
            mock_device.capabilities.return_value = {
                mock_evdev["ecodes"].EV_KEY: [
                    mock_evdev["ecodes"].KEY_A,
                    mock_evdev["ecodes"].KEY_LEFTCTRL,
                ]
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            callback = MagicMock()

            listener.start(callback)

            with pytest.raises(RuntimeError, match="already running"):
                listener.start(callback)

            listener.stop()

    def test_start_no_keyboard_raises_error(self, mock_evdev):
        """Test that start raises error when no keyboard is found."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            mock_evdev["list_devices"].return_value = []

            listener = EvdevKeyboardListener()
            callback = MagicMock()

            with pytest.raises(RuntimeError, match="No keyboard device found"):
                listener.start(callback)


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerStop:
    """Tests for stop method."""

    def test_stop_sets_stop_flag(self, mock_evdev):
        """Test that stop sets the stop flag."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device
            mock_device = MagicMock()
            mock_device.path = "/dev/input/event0"
            mock_device.capabilities.return_value = {
                mock_evdev["ecodes"].EV_KEY: [
                    mock_evdev["ecodes"].KEY_A,
                    mock_evdev["ecodes"].KEY_LEFTCTRL,
                ]
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            callback = MagicMock()

            listener.start(callback)
            listener.stop()

            assert listener._stop_flag is True
            assert listener._listener_thread is None
            assert listener._keyboard_device is None

    def test_stop_closes_device(self, mock_evdev):
        """Test that stop closes the device."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            # Mock device
            mock_device = MagicMock()
            mock_device.path = "/dev/input/event0"
            mock_device.capabilities.return_value = {
                mock_evdev["ecodes"].EV_KEY: [
                    mock_evdev["ecodes"].KEY_A,
                    mock_evdev["ecodes"].KEY_LEFTCTRL,
                ]
            }
            mock_evdev["InputDevice"].return_value = mock_device

            listener = EvdevKeyboardListener()
            callback = MagicMock()

            listener.start(callback)
            listener.stop()

            # Verify device was closed
            mock_device.close.assert_called_once()


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerIsRunning:
    """Tests for is_running method."""

    def test_is_running_false_initially(self, mock_evdev):
        """Test that is_running is False initially."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            assert listener.is_running() is False


@pytest.mark.unit
@pytest.mark.linux
class TestEvdevKeyboardListenerGetKeyCodes:
    """Tests for _get_key_codes method."""

    def test_get_key_codes_ctrl(self, mock_evdev):
        """Test getting key codes for ctrl."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("ctrl")

            assert key_codes == ["KEY_LEFTCTRL", "KEY_RIGHTCTRL"]

    def test_get_key_codes_alt(self, mock_evdev):
        """Test getting key codes for alt."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("alt")

            assert key_codes == ["KEY_LEFTALT", "KEY_RIGHTALT"]

    def test_get_key_codes_shift(self, mock_evdev):
        """Test getting key codes for shift."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("shift")

            assert key_codes == ["KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"]

    def test_get_key_codes_super(self, mock_evdev):
        """Test getting key codes for super/cmd."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("super")

            assert key_codes == ["KEY_LEFTMETA", "KEY_RIGHTMETA"]

    def test_get_key_codes_unknown_key(self, mock_evdev):
        """Test getting key codes for unknown key."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("unknown")

            assert key_codes == ["KEY_UNKNOWN"]

    def test_get_key_codes_case_insensitive(self, mock_evdev):
        """Test that key name is case-insensitive."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = EvdevKeyboardListener()

            key_codes = listener._get_key_codes("CTRL")

            assert key_codes == ["KEY_LEFTCTRL", "KEY_RIGHTCTRL"]
