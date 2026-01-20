"""Unit tests for config module."""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.config import (
    DictationConfig,
    create_default_config,
    validate_config,
)
from whisper_dictation.platform.detection import PlatformInfo


@pytest.mark.unit
class TestCreateDefaultConfig:
    """Tests for create_default_config function."""

    @patch("whisper_dictation.config.get_platform_info")
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

        assert config.model_name == "large-v3-turbo"
        assert config.hotkey == "cmd_l+alt"
        assert config.use_double_cmd is False
        assert config.languages is None
        assert config.default_language is None
        assert config.max_recording_time == 30.0
        assert config.sample_rate == 16000
        assert config.frames_per_buffer == 1024
        assert (
            config.ui_mode == "cli"
        )  # Default is CLI since rumps might not be available

    @patch("whisper_dictation.config.get_platform_info")
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

        assert config.model_name == "large-v3-turbo"
        assert config.hotkey == "ctrl+alt"
        assert config.ui_mode == "cli"  # Linux always uses CLI

    @patch("whisper_dictation.config.get_platform_info")
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

        config = create_default_config(model="base")

        assert config.model_name == "base"

    @patch("whisper_dictation.config.get_platform_info")
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

    @patch("whisper_dictation.config.get_platform_info")
    def test_use_double_cmd(self, mock_get_platform):
        """Test use_double_cmd parameter."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )

        config = create_default_config(use_double_cmd=True)

        assert config.use_double_cmd is True

    @patch("whisper_dictation.config.get_platform_info")
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

    @patch("whisper_dictation.config.get_platform_info")
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

    @patch("whisper_dictation.config.get_platform_info")
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

    @patch("whisper_dictation.config.get_platform_info")
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

    @patch("whisper_dictation.config.get_platform_info")
    def test_no_gui_forces_cli(self, mock_get_platform):
        """Test that no_gui parameter forces CLI mode."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )

        config = create_default_config(no_gui=True)

        assert config.ui_mode == "cli"

    @patch("whisper_dictation.config.get_platform_info")
    @patch("importlib.util.find_spec")
    def test_gui_mode_when_rumps_available(
        self, mock_find_spec, mock_get_platform, monkeypatch
    ):
        """Test GUI mode is enabled when rumps is available on macOS."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )

        # Mock find_spec to return a spec (indicating rumps is available)
        mock_find_spec.return_value = MagicMock()

        config = create_default_config()

        assert config.ui_mode == "gui"

    @patch("whisper_dictation.config.get_platform_info")
    @patch("importlib.util.find_spec")
    def test_gui_mode_unavailable_without_rumps(
        self, mock_find_spec, mock_get_platform
    ):
        """Test CLI mode is used when rumps is not available."""
        mock_get_platform.return_value = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )

        # Mock find_spec to return None (indicating rumps is not available)
        mock_find_spec.return_value = None

        config = create_default_config()

        # Should default to CLI if rumps not available
        assert config.ui_mode == "cli"


@pytest.mark.unit
class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_gui_on_non_macos_raises_error(self, mock_linux_x11_platform):
        """Test that GUI mode on non-macOS raises ValueError."""
        config = DictationConfig(
            model_name="large-v3-turbo",
            hotkey="ctrl+alt",
            use_double_cmd=False,
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="gui",
            platform=mock_linux_x11_platform,
        )

        with pytest.raises(ValueError, match="GUI mode is only supported on macOS"):
            validate_config(config)

    def test_validate_english_model_with_non_english_language(
        self, mock_linux_x11_platform
    ):
        """Test that .en model with non-English language raises ValueError."""
        config = DictationConfig(
            model_name="base.en",
            hotkey="ctrl+alt",
            use_double_cmd=False,
            languages=["es", "fr"],
            default_language="es",
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="cli",
            platform=mock_linux_x11_platform,
        )

        with pytest.raises(ValueError, match=r"English-only.*languages"):
            validate_config(config)

    def test_validate_english_model_with_english_language(
        self, mock_linux_x11_platform
    ):
        """Test that .en model with English language is valid."""
        config = DictationConfig(
            model_name="base.en",
            hotkey="ctrl+alt",
            use_double_cmd=False,
            languages=["en"],
            default_language="en",
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="cli",
            platform=mock_linux_x11_platform,
        )

        # Should not raise
        validate_config(config)

    def test_validate_valid_macos_gui_config(self, mock_macos_platform):
        """Test that valid macOS GUI config passes validation."""
        config = DictationConfig(
            model_name="large-v3-turbo",
            hotkey="cmd_l+alt",
            use_double_cmd=False,
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="gui",
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
            model_name="large-v3-turbo",
            hotkey="ctrl+alt",
            use_double_cmd=False,
            languages=None,
            default_language=None,
            max_recording_time=30.0,
            sample_rate=16000,
            frames_per_buffer=1024,
            ui_mode="cli",
            platform=mock_linux_x11_platform,
        )

        validate_config(config)

        captured = capsys.readouterr()
        assert "evdev" in captured.out
        assert "Warning" in captured.out
