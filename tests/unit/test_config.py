"""Unit tests for config module."""

from unittest.mock import patch

import pytest

from dictation.config import (
    DEFAULT_MODEL,
    DictationConfig,
    create_default_config,
    validate_config,
)
from dictation.platform.detection import PlatformInfo


@pytest.mark.unit
class TestCreateDefaultConfig:
    """Tests for create_default_config function."""

    @patch("dictation.config.get_platform_info")
    def test_default_config_macos(self, mock_get_platform):
        """Test default configuration for macOS."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )

        config = create_default_config()

        assert config.model_name == DEFAULT_MODEL
        assert config.hotkey == "cmd_l+alt"
        assert config.languages is None
        assert config.default_language is None
        assert config.max_recording_time == 600.0
        assert config.sample_rate == 16000
        assert config.frames_per_buffer == 1024

    @patch("dictation.config.get_platform_info")
    def test_default_config_linux(self, mock_get_platform):
        """Test default configuration for Linux."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config()

        assert config.model_name == DEFAULT_MODEL
        assert config.hotkey == "ctrl+alt"

    @patch("dictation.config.get_platform_info")
    def test_custom_model(self, mock_get_platform):
        """Test custom model parameter."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(model="Qwen/Qwen3-ASR-1.7B")

        assert config.model_name == "Qwen/Qwen3-ASR-1.7B"

    @patch("dictation.config.get_platform_info")
    def test_custom_hotkey(self, mock_get_platform):
        """Test custom hotkey parameter."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(hotkey="ctrl+shift")

        assert config.hotkey == "ctrl+shift"

    @patch("dictation.config.get_platform_info")
    def test_languages_parameter(self, mock_get_platform):
        """Test languages parameter sets default language."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(languages=["es", "fr"])

        assert config.languages == ["es", "fr"]
        assert config.default_language == "es"  # First language is default

    @patch("dictation.config.get_platform_info")
    def test_empty_languages_list(self, mock_get_platform):
        """Test empty languages list."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(languages=[])

        assert config.languages == []
        assert config.default_language is None

    @patch("dictation.config.get_platform_info")
    def test_max_time_parameter(self, mock_get_platform):
        """Test max_time parameter."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(max_time=60.0)

        assert config.max_recording_time == 60.0

    @patch("dictation.config.get_platform_info")
    def test_max_time_none(self, mock_get_platform):
        """Test max_time=None (unlimited recording)."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )

        config = create_default_config(max_time=None)

        assert config.max_recording_time is None


@pytest.mark.unit
class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_valid_macos_config(self, mock_macos_platform):
        """Test that valid macOS config passes validation."""
        config = DictationConfig(
            model_name="Qwen/Qwen3-ASR-0.6B",
            hotkey="cmd_l+alt",
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            platform=mock_macos_platform,
        )

        # Should not raise
        validate_config(config)

    @patch("shutil.which")
    def test_validate_wayland_without_ydotool_warns(
        self, mock_which, mock_linux_wayland_platform, capsys
    ):
        """Test that Wayland without ydotool prints a warning."""
        mock_which.return_value = None  # ydotool not found

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

        validate_config(config)

        captured = capsys.readouterr()
        assert "ydotool" in captured.out
        assert "Warning" in captured.out

    @patch("shutil.which")
    def test_validate_wayland_with_ydotool_no_warning(
        self, mock_which, mock_linux_wayland_platform, capsys
    ):
        """Test that Wayland with ydotool doesn't print a warning."""
        mock_which.return_value = "/usr/bin/ydotool"  # ydotool found

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

        validate_config(config)

        captured = capsys.readouterr()
        assert "ydotool" not in captured.out

    @patch("builtins.__import__")
    def test_validate_linux_without_evdev_warns(
        self, mock_import, mock_linux_x11_platform, capsys
    ):
        """Test that Linux without evdev prints a warning."""

        def import_side_effect(name, *args, **kwargs):
            if name == "evdev":
                raise ImportError("No module named 'evdev'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        config = DictationConfig(
            model_name="Qwen/Qwen3-ASR-0.6B",
            hotkey="ctrl+alt",
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            platform=mock_linux_x11_platform,
        )

        validate_config(config)

        captured = capsys.readouterr()
        assert "evdev" in captured.out
        assert "Warning" in captured.out
