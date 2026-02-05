"""Integration tests for DictationApp."""

from unittest.mock import patch

import pytest

from dictation.__main__ import (
    DictationApp,
    create_keyboard_listener,
    create_text_injector,
    create_transcriber,
)
from dictation.config import DictationConfig


@pytest.mark.integration
class TestCreateTranscriber:
    """Tests for create_transcriber factory function."""

    def test_create_transcriber(self, default_linux_config, mock_qwen_asr):
        """Test creating a transcriber."""
        transcriber = create_transcriber(default_linux_config)

        assert transcriber is not None
        assert transcriber.get_model_name() == "Qwen/Qwen3-ASR-0.6B"


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
            model_name="Qwen/Qwen3-ASR-0.6B",
            hotkey="ctrl+alt",
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
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

    @pytest.mark.skipif(
        pytest.importorskip("sys").platform != "linux", reason="evdev is Linux-only"
    )
    def test_create_evdev_listener_on_linux(self, default_linux_config, mock_evdev):
        """Test creating evdev listener on Linux."""
        with patch("dictation.platform.keyboard.evdev_listener.evdev", mock_evdev):
            listener = create_keyboard_listener(default_linux_config)

            assert listener is not None
            assert listener.key_combination == "ctrl+alt"


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppInitialization:
    """Tests for DictationApp initialization."""

    def test_initialization(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
    ):
        """Test DictationApp initialization."""
        app = DictationApp(default_macos_config)

        assert app.config == default_macos_config
        assert app.transcriber is not None
        assert app.text_injector is not None
        assert app.recorder is not None
        assert app.keyboard_listener is not None
        assert app.ui is not None
        assert app.is_recording is False

    def test_initialization_creates_components(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
    ):
        """Test that initialization creates all necessary components."""
        app = DictationApp(default_macos_config)

        # Verify transcriber was created
        assert app.transcriber.get_model_name() == "Qwen/Qwen3-ASR-0.6B"

        # Verify recorder was created with correct settings
        assert app.recorder.sample_rate == 16000
        assert app.recorder.frames_per_buffer == 1024
        assert app.recorder.max_duration == 30.0


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppRecordingWorkflow:
    """Tests for DictationApp recording workflow."""

    def test_on_start_recording(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test starting recording."""
        app = DictationApp(default_macos_config)

        # Start recording
        app.on_start_recording()

        assert app.is_recording is True

    def test_on_stop_recording(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test stopping recording."""
        app = DictationApp(default_macos_config)

        # Start then stop recording
        app.on_start_recording()
        app.on_stop_recording()

        assert app.is_recording is False

    def test_on_start_recording_when_already_recording(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        mock_pyaudio,
    ):
        """Test that starting recording when already recording doesn't restart."""
        app = DictationApp(default_macos_config)

        # Start recording twice
        app.on_start_recording()
        app.on_start_recording()

        # Should still be recording
        assert app.is_recording is True

    def test_on_recording_complete_success(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test successful recording completion workflow."""
        app = DictationApp(default_macos_config)

        # Simulate recording completion
        app.on_recording_complete(sample_audio)

        # Verify transcription was called
        mock_qwen_asr["instance"].transcribe.assert_called_once()

        # Verify text was injected
        mock_pynput_controller["instance"].type.assert_called()

    def test_on_recording_complete_empty_text(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test recording completion with empty transcription."""
        # Configure mock to return empty text
        mock_qwen_asr["result"].text = ""

        app = DictationApp(default_macos_config)

        # Simulate recording completion
        app.on_recording_complete(sample_audio)

        # Verify text was not injected
        mock_pynput_controller["instance"].type.assert_not_called()

    def test_on_recording_complete_error_handling(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test error handling during transcription."""
        # Configure mock to raise error
        mock_qwen_asr["instance"].transcribe.side_effect = Exception(
            "Transcription failed"
        )

        app = DictationApp(default_macos_config)

        # Simulate recording completion - should not raise
        app.on_recording_complete(sample_audio)


@pytest.mark.integration
@pytest.mark.slow
class TestDictationAppEndToEnd:
    """End-to-end workflow tests for DictationApp."""

    def test_complete_workflow(
        self,
        default_macos_config,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test complete workflow: start recording -> record -> transcribe -> inject."""
        app = DictationApp(default_macos_config)

        # Workflow: start -> complete
        app.on_start_recording()
        assert app.is_recording is True

        app.on_recording_complete(sample_audio)

        # Verify transcription was called
        mock_qwen_asr["instance"].transcribe.assert_called_once()

        # Verify text was normalized and injected
        # "Hello world" should be injected character by character
        call_count = mock_pynput_controller["instance"].type.call_count
        assert call_count == len("Hello world")

    def test_workflow_with_language(
        self,
        mock_macos_platform,
        mock_qwen_asr,
        mock_pynput_keyboard,
        mock_pynput_controller,
        sample_audio,
    ):
        """Test workflow with specific language."""
        config = DictationConfig(
            model_name="Qwen/Qwen3-ASR-0.6B",
            hotkey="cmd_l+alt",
            languages=["es", "en"],
            default_language="es",
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            platform=mock_macos_platform,
        )

        # Configure mock transcriber
        mock_qwen_asr["result"].text = "Hola mundo"

        app = DictationApp(config)

        # Start recording
        app.on_start_recording()
        assert app.current_language == "es"

        app.on_recording_complete(sample_audio)

        # Verify transcription was called with correct language
        call_kwargs = mock_qwen_asr["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] == "Spanish"
