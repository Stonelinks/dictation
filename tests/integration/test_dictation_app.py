"""Integration tests for DictationApp."""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.__main__ import (
    DictationApp,
    create_keyboard_listener,
    create_text_injector,
    create_transcriber,
)
from whisper_dictation.config import DictationConfig


@pytest.mark.integration
class TestCreateTranscriber:
    """Tests for create_transcriber factory function."""

    def test_create_transcriber(self, default_macos_config, mock_whisper_model):
        """Test creating a transcriber."""
        transcriber = create_transcriber(default_macos_config)

        assert transcriber is not None
        assert transcriber.get_model_name() == "large-v3-turbo"


@pytest.mark.integration
class TestCreateTextInjector:
    """Tests for create_text_injector factory function."""

    def test_create_pynput_injector_on_macos(
        self, default_macos_config, mock_pynput_controller
    ):
        """Test creating pynput injector on macOS."""
        injector = create_text_injector(default_macos_config)

        assert injector is not None
        # Should use PynputTextInjector
        mock_pynput_controller["class"].assert_called_once()

    def test_create_pynput_injector_on_x11(
        self, default_linux_config, mock_pynput_controller
    ):
        """Test creating pynput injector on Linux X11."""
        injector = create_text_injector(default_linux_config)

        assert injector is not None
        mock_pynput_controller["class"].assert_called_once()

    @patch("shutil.which")
    def test_create_ydotool_injector_on_wayland(
        self, mock_which, mock_linux_wayland_platform
    ):
        """Test creating ydotool injector on Wayland."""
        mock_which.return_value = "/usr/bin/ydotool"

        config = DictationConfig(
            model_name="large-v3-turbo",
            hotkey="ctrl+alt",
            use_double_cmd=False,
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="cli",
            platform=mock_linux_wayland_platform,
        )

        injector = create_text_injector(config)

        assert injector is not None


@pytest.mark.integration
class TestCreateKeyboardListener:
    """Tests for create_keyboard_listener factory function."""

    def test_create_pynput_listener_on_macos(
        self, default_macos_config, mock_pynput_keyboard
    ):
        """Test creating pynput listener on macOS."""
        listener = create_keyboard_listener(default_macos_config)

        assert listener is not None
        assert listener.key_combination == "cmd_l+alt"

    def test_create_double_cmd_listener_on_macos(
        self, mock_macos_platform, mock_pynput_keyboard
    ):
        """Test creating double command listener on macOS."""
        config = DictationConfig(
            model_name="large-v3-turbo",
            hotkey="cmd_l+alt",
            use_double_cmd=True,
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="cli",
            platform=mock_macos_platform,
        )

        listener = create_keyboard_listener(config)

        assert listener is not None

    @pytest.mark.skipif(
        pytest.importorskip("sys").platform != "linux", reason="evdev is Linux-only"
    )
    def test_create_evdev_listener_on_linux(self, default_linux_config, mock_evdev):
        """Test creating evdev listener on Linux."""
        with patch(
            "whisper_dictation.platform.keyboard.evdev_listener.evdev", mock_evdev
        ):
            listener = create_keyboard_listener(default_linux_config)

            assert listener is not None
            assert listener.key_combination == "ctrl+alt"


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppInitialization:
    """Tests for DictationApp initialization."""

    @patch("whisper_dictation.__main__.create_ui")
    def test_initialization(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
    ):
        """Test DictationApp initialization."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        app = DictationApp(default_macos_config)

        assert app.config == default_macos_config
        assert app.transcriber is not None
        assert app.text_injector is not None
        assert app.recorder is not None
        assert app.keyboard_listener is not None
        assert app.ui is not None
        assert app.is_recording is False

    @patch("whisper_dictation.__main__.create_ui")
    def test_initialization_creates_components(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
    ):
        """Test that initialization creates all necessary components."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        app = DictationApp(default_macos_config)

        # Verify transcriber was created
        assert app.transcriber.get_model_name() == "large-v3-turbo"

        # Verify recorder was created with correct settings
        assert app.recorder.sample_rate == 16000
        assert app.recorder.frames_per_buffer == 1024
        assert app.recorder.max_duration == 30.0


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppRecordingWorkflow:
    """Tests for DictationApp recording workflow."""

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_start_recording(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test starting recording."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        app = DictationApp(default_macos_config)

        # Start recording
        app.on_start_recording()

        assert app.is_recording is True
        mock_ui.on_recording_start.assert_called_once()

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_stop_recording(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test stopping recording."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        app = DictationApp(default_macos_config)

        # Start then stop recording
        app.on_start_recording()
        app.on_stop_recording()

        assert app.is_recording is False
        mock_ui.on_recording_stop.assert_called_once()

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_start_recording_when_already_recording(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test that starting recording when already recording doesn't restart."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        app = DictationApp(default_macos_config)

        # Start recording twice
        app.on_start_recording()
        app.on_start_recording()

        # Should only call on_recording_start once
        mock_ui.on_recording_start.assert_called_once()

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_recording_complete_success(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test successful recording completion workflow."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        # Configure mock transcriber
        mock_whisper_model["instance"].transcribe.return_value = (
            [MagicMock(text="Test transcription")],
            MagicMock(),
        )

        app = DictationApp(default_macos_config)

        # Simulate recording completion
        app.on_recording_complete(sample_audio)

        # Verify transcription was called
        mock_whisper_model["instance"].transcribe.assert_called_once()

        # Verify text was injected
        mock_pynput_controller["instance"].type.assert_called()

        # Verify UI was notified
        mock_ui.on_transcription_complete.assert_called_once()

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_recording_complete_empty_text(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test recording completion with empty transcription."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        # Configure mock to return empty text
        mock_whisper_model["instance"].transcribe.return_value = ([], MagicMock())

        app = DictationApp(default_macos_config)

        # Simulate recording completion
        app.on_recording_complete(sample_audio)

        # Verify error was reported
        mock_ui.on_error.assert_called_once_with("No text transcribed")

        # Verify text was not injected
        mock_pynput_controller["instance"].type.assert_not_called()

    @patch("whisper_dictation.__main__.create_ui")
    def test_on_recording_complete_error_handling(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test error handling during transcription."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        # Configure mock to raise error
        mock_whisper_model["instance"].transcribe.side_effect = Exception(
            "Transcription failed"
        )

        app = DictationApp(default_macos_config)

        # Simulate recording completion
        app.on_recording_complete(sample_audio)

        # Verify error was reported
        mock_ui.on_error.assert_called_once()
        error_msg = mock_ui.on_error.call_args[0][0]
        assert "Transcription error" in error_msg


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppEndToEnd:
    """End-to-end workflow tests for DictationApp."""

    @patch("whisper_dictation.__main__.create_ui")
    def test_complete_workflow(
        self,
        mock_create_ui,
        default_macos_config,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test complete workflow: start recording → record → transcribe → inject."""
        mock_ui = MagicMock()
        mock_create_ui.return_value = mock_ui

        # Configure mock transcriber
        seg1 = MagicMock()
        seg1.text = "Hello"
        seg2 = MagicMock()
        seg2.text = "world"
        mock_whisper_model["instance"].transcribe.return_value = (
            [seg1, seg2],
            MagicMock(),
        )

        app = DictationApp(default_macos_config)

        # Workflow: start → complete
        app.on_start_recording()
        assert app.is_recording is True

        app.on_recording_complete(sample_audio)

        # Verify transcription was called
        mock_whisper_model["instance"].transcribe.assert_called_once()

        # Verify text was normalized and injected
        # "Hello world" should be injected character by character
        call_count = mock_pynput_controller["instance"].type.call_count
        assert call_count == len("Hello world")

        # Verify UI was notified
        mock_ui.on_transcription_complete.assert_called_once()
        transcribed_text = mock_ui.on_transcription_complete.call_args[0][0]
        assert transcribed_text == "Hello world"

    @patch("whisper_dictation.__main__.create_ui")
    def test_workflow_with_language(
        self,
        mock_create_ui,
        mock_macos_platform,
        mock_whisper_model,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test workflow with specific language."""
        mock_ui = MagicMock()
        mock_ui.get_current_language.return_value = "es"
        mock_create_ui.return_value = mock_ui

        config = DictationConfig(
            model_name="large-v3-turbo",
            hotkey="cmd_l+alt",
            use_double_cmd=False,
            languages=["es", "en"],
            default_language="es",
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="gui",
            platform=mock_macos_platform,
        )

        # Configure mock transcriber
        seg = MagicMock()
        seg.text = "Hola mundo"
        mock_whisper_model["instance"].transcribe.return_value = ([seg], MagicMock())

        app = DictationApp(config)

        # Start recording (should get language from UI)
        app.on_start_recording()
        assert app.current_language == "es"

        app.on_recording_complete(sample_audio)

        # Verify transcription was called with correct language
        call_kwargs = mock_whisper_model["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] == "es"
