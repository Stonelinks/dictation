"""Shared pytest fixtures for all tests."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from dictation.config import DictationConfig
from dictation.platform.detection import PlatformInfo


# Platform Fixtures


@pytest.fixture
def mock_macos_platform():
    """Mock macOS platform info."""
    return PlatformInfo(
        os_name="Darwin",
        is_macos=True,
        is_linux=False,
        is_windows=False,
        is_apple_silicon=False,
        session_type=None,
    )


@pytest.fixture
def mock_macos_apple_silicon_platform():
    """Mock macOS Apple Silicon platform info."""
    return PlatformInfo(
        os_name="Darwin",
        is_macos=True,
        is_linux=False,
        is_windows=False,
        is_apple_silicon=True,
        session_type=None,
    )


@pytest.fixture
def mock_linux_x11_platform():
    """Mock Linux X11 platform info."""
    return PlatformInfo(
        os_name="Linux",
        is_macos=False,
        is_linux=True,
        is_windows=False,
        is_apple_silicon=False,
        session_type="x11",
    )


@pytest.fixture
def mock_linux_wayland_platform():
    """Mock Linux Wayland platform info."""
    return PlatformInfo(
        os_name="Linux",
        is_macos=False,
        is_linux=True,
        is_windows=False,
        is_apple_silicon=False,
        session_type="wayland",
    )


# Configuration Fixtures


@pytest.fixture
def default_macos_config(mock_macos_platform):
    """Default configuration for macOS."""
    return DictationConfig(
        model_name="Qwen/Qwen3-ASR-0.6B",
        hotkey="cmd_l+alt",
        languages=None,
        default_language=None,
        max_recording_time=30.0,
        sample_rate=16000,
        frames_per_buffer=1024,
        platform=mock_macos_platform,
    )


@pytest.fixture
def default_linux_config(mock_linux_x11_platform):
    """Default configuration for Linux X11."""
    return DictationConfig(
        model_name="Qwen/Qwen3-ASR-0.6B",
        hotkey="ctrl+alt",
        languages=None,
        default_language=None,
        max_recording_time=30.0,
        sample_rate=16000,
        frames_per_buffer=1024,
        platform=mock_linux_x11_platform,
    )


# Audio Data Fixtures


@pytest.fixture
def sample_audio():
    """Generate sample audio data (1 second of synthetic speech-like audio)."""
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)

    # Generate synthetic audio: mix of sine waves at speech-like frequencies
    t = np.linspace(0, duration, samples, dtype=np.float32)
    audio = (
        0.3 * np.sin(2 * np.pi * 200 * t)
        + 0.2 * np.sin(2 * np.pi * 400 * t)
        + 0.1 * np.sin(2 * np.pi * 800 * t)
    )

    # Normalize to [-1, 1]
    audio = audio / np.max(np.abs(audio))
    return audio.astype(np.float32)


@pytest.fixture
def empty_audio():
    """Empty audio data."""
    return np.array([], dtype=np.float32)


@pytest.fixture
def short_audio():
    """Short audio data (0.1 seconds)."""
    sample_rate = 16000
    duration = 0.1
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    return audio.astype(np.float32)


# PyAudio Mocks


@pytest.fixture
def mock_pyaudio(mocker):
    """Mock PyAudio for recorder tests."""
    mock_pa_class = mocker.patch("dictation.core.recorder.pyaudio.PyAudio")
    mock_pa_instance = MagicMock()
    mock_pa_class.return_value = mock_pa_instance

    # Mock the stream
    mock_stream = MagicMock()
    mock_pa_instance.open.return_value = mock_stream

    # Mock stream.read() to return sample audio data
    sample_data = np.random.randint(-32768, 32767, 1024, dtype=np.int16).tobytes()
    mock_stream.read.return_value = sample_data

    return {
        "class": mock_pa_class,
        "instance": mock_pa_instance,
        "stream": mock_stream,
    }


# Pynput Mocks


@pytest.fixture
def mock_pynput_keyboard(mocker):
    """Mock pynput.keyboard for keyboard listener tests."""
    mock_listener_class = mocker.patch(
        "dictation.platform.keyboard.pynput_listener.keyboard.Listener"
    )
    mock_listener_instance = MagicMock()
    mock_listener_class.return_value = mock_listener_instance

    # Mock the Key enum
    mock_key = mocker.patch("dictation.platform.keyboard.pynput_listener.keyboard.Key")
    mock_key.ctrl = MagicMock()
    mock_key.alt = MagicMock()
    mock_key.cmd = MagicMock()
    mock_key.cmd_l = MagicMock()
    mock_key.cmd_r = MagicMock()

    return {
        "listener_class": mock_listener_class,
        "listener_instance": mock_listener_instance,
        "key": mock_key,
    }


@pytest.fixture
def mock_pynput_controller(mocker):
    """Mock pynput.keyboard.Controller for text injection tests."""
    mock_controller_class = mocker.patch(
        "dictation.platform.text_injection.pynput_injector.keyboard.Controller"
    )
    mock_controller_instance = MagicMock()
    mock_controller_class.return_value = mock_controller_instance

    return {
        "class": mock_controller_class,
        "instance": mock_controller_instance,
    }


# Evdev Mocks


@pytest.fixture
def mock_evdev(mocker):
    """Mock evdev for Linux keyboard listener tests."""
    mock_input_device = mocker.patch(
        "dictation.platform.keyboard.evdev_listener.evdev.InputDevice"
    )
    mock_list_devices = mocker.patch(
        "dictation.platform.keyboard.evdev_listener.evdev.list_devices"
    )

    mock_list_devices.return_value = ["/dev/input/event0", "/dev/input/event1"]

    mock_device_instance = MagicMock()
    mock_device_instance.name = "Test Keyboard"
    mock_input_device.return_value = mock_device_instance

    # Mock ecodes
    mock_ecodes = mocker.patch(
        "dictation.platform.keyboard.evdev_listener.evdev.ecodes"
    )
    mock_ecodes.KEY_LEFTCTRL = 29
    mock_ecodes.KEY_LEFTALT = 56
    mock_ecodes.EV_KEY = 1

    return {
        "InputDevice": mock_input_device,
        "list_devices": mock_list_devices,
        "device_instance": mock_device_instance,
        "ecodes": mock_ecodes,
    }


# Subprocess Mocks


@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess.run for ydotool tests."""
    mock_run = mocker.patch("subprocess.run")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    return mock_run


# Platform Detection Mocks


@pytest.fixture
def mock_platform_system(mocker):
    """Mock platform.system() for platform detection tests."""
    return mocker.patch("platform.system")


@pytest.fixture
def mock_platform_machine(mocker):
    """Mock platform.machine() for platform detection tests."""
    return mocker.patch("platform.machine")


# Qwen ASR Mocks


@pytest.fixture
def mock_qwen_asr(mocker):
    """Mock qwen_asr for Qwen3Transcriber tests."""
    mock_qwen_asr_module = mocker.MagicMock()
    mocker.patch.dict("sys.modules", {"qwen_asr": mock_qwen_asr_module})

    mock_model_class = MagicMock()
    mock_qwen_asr_module.Qwen3ASRModel = mock_model_class

    mock_model_instance = MagicMock()
    mock_model_class.from_pretrained.return_value = mock_model_instance

    # Mock transcribe to return a list with one result
    mock_result = MagicMock()
    mock_result.text = "Hello world"
    mock_model_instance.transcribe.return_value = [mock_result]

    return {
        "class": mock_model_class,
        "instance": mock_model_instance,
        "result": mock_result,
    }
