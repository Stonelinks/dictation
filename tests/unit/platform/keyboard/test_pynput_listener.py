"""Unit tests for pynput keyboard listener module."""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.platform.keyboard.pynput_listener import (
    PynputDoubleCommandListener,
    PynputKeyboardListener,
    _DoubleCommandHandler,
    _KeyComboHandler,
)


@pytest.mark.unit
class TestPynputKeyboardListenerInitialization:
    """Tests for PynputKeyboardListener initialization."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        listener = PynputKeyboardListener()

        assert listener.key_combination == "cmd_l+alt"
        assert listener._listener is None
        assert listener._on_hotkey is None

    def test_custom_key_combination(self):
        """Test initialization with custom key combination."""
        listener = PynputKeyboardListener(key_combination="ctrl+alt")

        assert listener.key_combination == "ctrl+alt"


@pytest.mark.unit
class TestPynputKeyboardListenerStart:
    """Tests for PynputKeyboardListener start method."""

    def test_start_creates_listener(self, mock_pynput_keyboard):
        """Test that start creates a pynput listener."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)

        # Verify listener was created
        mock_pynput_keyboard["listener_class"].assert_called_once()
        assert listener._listener is not None

    def test_start_twice_raises_error(self, mock_pynput_keyboard):
        """Test that starting twice raises RuntimeError."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)

        with pytest.raises(RuntimeError, match="already running"):
            listener.start(callback)

    def test_start_stores_callback(self, mock_pynput_keyboard):
        """Test that start stores the callback."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)

        assert listener._on_hotkey is callback

    def test_start_calls_listener_start(self, mock_pynput_keyboard):
        """Test that start calls listener.start()."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)

        mock_pynput_keyboard["listener_instance"].start.assert_called_once()


@pytest.mark.unit
class TestPynputKeyboardListenerStop:
    """Tests for PynputKeyboardListener stop method."""

    def test_stop_calls_listener_stop(self, mock_pynput_keyboard):
        """Test that stop calls listener.stop()."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)
        listener.stop()

        mock_pynput_keyboard["listener_instance"].stop.assert_called_once()

    def test_stop_clears_listener(self, mock_pynput_keyboard):
        """Test that stop clears the listener reference."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)
        listener.stop()

        assert listener._listener is None
        assert listener._key_handler is None

    def test_stop_when_not_started(self):
        """Test that stop when not started doesn't raise error."""
        listener = PynputKeyboardListener()

        # Should not raise
        listener.stop()


@pytest.mark.unit
class TestPynputKeyboardListenerIsRunning:
    """Tests for PynputKeyboardListener is_running method."""

    def test_is_running_false_initially(self):
        """Test that is_running is False initially."""
        listener = PynputKeyboardListener()

        assert listener.is_running() is False

    def test_is_running_true_after_start(self, mock_pynput_keyboard):
        """Test that is_running is True after start."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)

        assert listener.is_running() is True

    def test_is_running_false_after_stop(self, mock_pynput_keyboard):
        """Test that is_running is False after stop."""
        listener = PynputKeyboardListener()
        callback = MagicMock()

        listener.start(callback)
        listener.stop()

        assert listener.is_running() is False


@pytest.mark.unit
class TestKeyComboHandler:
    """Tests for _KeyComboHandler internal class."""

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_parse_key_combination_with_special_keys(self, mock_keyboard):
        """Test parsing key combination with special keys."""
        mock_keyboard.Key.cmd_l = MagicMock()
        mock_keyboard.Key.alt = MagicMock()

        callback = MagicMock()
        handler = _KeyComboHandler("cmd_l+alt", callback)

        assert handler.key1 is mock_keyboard.Key.cmd_l
        assert handler.key2 is mock_keyboard.Key.alt

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_parse_key_combination_ctrl_alt(self, mock_keyboard):
        """Test parsing ctrl+alt combination."""
        mock_keyboard.Key.ctrl = MagicMock()
        mock_keyboard.Key.alt = MagicMock()

        callback = MagicMock()
        handler = _KeyComboHandler("ctrl+alt", callback)

        assert handler.key1 is mock_keyboard.Key.ctrl
        assert handler.key2 is mock_keyboard.Key.alt

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_key_combo_triggers_callback(self, mock_keyboard):
        """Test that pressing both keys triggers callback."""
        mock_keyboard.Key.ctrl = MagicMock()
        mock_keyboard.Key.alt = MagicMock()

        callback = MagicMock()
        handler = _KeyComboHandler("ctrl+alt", callback)

        # Press first key
        handler.on_key_press(mock_keyboard.Key.ctrl)
        callback.assert_not_called()

        # Press second key - should trigger callback
        handler.on_key_press(mock_keyboard.Key.alt)
        callback.assert_called_once()

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_key_combo_no_double_trigger(self, mock_keyboard):
        """Test that holding keys doesn't trigger callback multiple times."""
        mock_keyboard.Key.ctrl = MagicMock()
        mock_keyboard.Key.alt = MagicMock()

        callback = MagicMock()
        handler = _KeyComboHandler("ctrl+alt", callback)

        # Press both keys
        handler.on_key_press(mock_keyboard.Key.ctrl)
        handler.on_key_press(mock_keyboard.Key.alt)
        callback.assert_called_once()

        # Press again while holding - should not trigger again
        handler.on_key_press(mock_keyboard.Key.ctrl)
        callback.assert_called_once()

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_key_combo_reset_on_release(self, mock_keyboard):
        """Test that releasing keys resets the combo trigger."""
        mock_keyboard.Key.ctrl = MagicMock()
        mock_keyboard.Key.alt = MagicMock()

        callback = MagicMock()
        handler = _KeyComboHandler("ctrl+alt", callback)

        # Press and trigger
        handler.on_key_press(mock_keyboard.Key.ctrl)
        handler.on_key_press(mock_keyboard.Key.alt)
        callback.assert_called_once()

        # Release a key
        handler.on_key_release(mock_keyboard.Key.ctrl)

        # Press again - should trigger again
        handler.on_key_press(mock_keyboard.Key.ctrl)
        assert callback.call_count == 2


@pytest.mark.unit
class TestPynputDoubleCommandListener:
    """Tests for PynputDoubleCommandListener."""

    def test_initialization(self):
        """Test double command listener initialization."""
        listener = PynputDoubleCommandListener()

        assert listener._listener is None
        assert listener._on_hotkey is None

    def test_start_creates_listener(self, mock_pynput_keyboard):
        """Test that start creates a listener."""
        listener = PynputDoubleCommandListener()
        callback = MagicMock()

        listener.start(callback)

        mock_pynput_keyboard["listener_class"].assert_called_once()
        assert listener._listener is not None

    def test_stop_clears_listener(self, mock_pynput_keyboard):
        """Test that stop clears the listener."""
        listener = PynputDoubleCommandListener()
        callback = MagicMock()

        listener.start(callback)
        listener.stop()

        assert listener._listener is None

    def test_is_running(self, mock_pynput_keyboard):
        """Test is_running method."""
        listener = PynputDoubleCommandListener()
        callback = MagicMock()

        assert listener.is_running() is False

        listener.start(callback)
        assert listener.is_running() is True

        listener.stop()
        assert listener.is_running() is False


@pytest.mark.unit
class TestDoubleCommandHandler:
    """Tests for _DoubleCommandHandler internal class."""

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_double_press_triggers_callback(self, mock_keyboard):
        """Test that double press within time window triggers callback."""
        mock_keyboard.Key.cmd_r = MagicMock()

        callback = MagicMock()

        # Mock time.time() at the module level where it's imported
        with patch(
            "whisper_dictation.platform.keyboard.pynput_listener.time.time"
        ) as mock_time:
            times = [1.0, 1.3]
            mock_time.side_effect = times

            handler = _DoubleCommandHandler(callback)

            # First press
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            callback.assert_not_called()

            # Second press within 0.5 seconds
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            callback.assert_called_once()

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_slow_double_press_no_trigger(self, mock_keyboard):
        """Test that slow double press doesn't trigger callback."""
        mock_keyboard.Key.cmd_r = MagicMock()

        callback = MagicMock()

        # Mock time.time() at the module level where it's imported
        with patch(
            "whisper_dictation.platform.keyboard.pynput_listener.time.time"
        ) as mock_time:
            times = [1.0, 1.6]
            mock_time.side_effect = times

            handler = _DoubleCommandHandler(callback)

            # First press
            handler.on_key_press(mock_keyboard.Key.cmd_r)

            # Second press after 0.5 seconds
            handler.on_key_press(mock_keyboard.Key.cmd_r)

            # Should not trigger (too slow)
            callback.assert_not_called()

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_single_press_to_stop(self, mock_keyboard):
        """Test that single press after recording stops recording."""
        mock_keyboard.Key.cmd_r = MagicMock()

        callback = MagicMock()

        # Mock time.time() at the module level where it's imported
        with patch(
            "whisper_dictation.platform.keyboard.pynput_listener.time.time"
        ) as mock_time:
            times = [1.0, 1.3, 2.0]
            mock_time.side_effect = times

            handler = _DoubleCommandHandler(callback)

            # Double press to start
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            callback.assert_called_once()

            # Single press to stop
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            assert callback.call_count == 2

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_on_key_release_does_nothing(self, mock_keyboard):
        """Test that on_key_release doesn't do anything."""
        mock_keyboard.Key.cmd_r = MagicMock()

        callback = MagicMock()
        handler = _DoubleCommandHandler(callback)

        # Should not raise or call anything
        handler.on_key_release(mock_keyboard.Key.cmd_r)
        callback.assert_not_called()

    @patch("whisper_dictation.platform.keyboard.pynput_listener.keyboard")
    def test_recording_state_tracking(self, mock_keyboard):
        """Test that recording state is tracked correctly."""
        mock_keyboard.Key.cmd_r = MagicMock()

        callback = MagicMock()

        # Mock time.time() at the module level where it's imported
        with patch(
            "whisper_dictation.platform.keyboard.pynput_listener.time.time"
        ) as mock_time:
            times = [1.0, 1.3, 2.0]
            mock_time.side_effect = times

            handler = _DoubleCommandHandler(callback)

            # Initially not recording
            assert handler.is_recording is False

            # Double press to start
            handler.on_key_press(mock_keyboard.Key.cmd_r)
            handler.on_key_press(mock_keyboard.Key.cmd_r)

            # Now recording
            assert handler.is_recording is True

            # Single press to stop
            handler.on_key_press(mock_keyboard.Key.cmd_r)

            # No longer recording
            assert handler.is_recording is False
