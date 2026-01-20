"""Unit tests for platform detection module."""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.platform.detection import (
    PlatformInfo,
    _detect_apple_silicon,
    _detect_session_type,
    detect_platform,
)


@pytest.mark.unit
class TestPlatformInfo:
    """Tests for PlatformInfo dataclass."""

    def test_is_wayland_property(self):
        """Test is_wayland property."""
        info = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="wayland",
        )
        assert info.is_wayland is True
        assert info.is_x11 is False

    def test_is_x11_property(self):
        """Test is_x11 property."""
        info = PlatformInfo(
            os_name="Linux",
            is_macos=False,
            is_linux=True,
            is_windows=False,
            is_apple_silicon=False,
            session_type="x11",
        )
        assert info.is_x11 is True
        assert info.is_wayland is False

    def test_no_session_type(self):
        """Test when session_type is None."""
        info = PlatformInfo(
            os_name="Darwin",
            is_macos=True,
            is_linux=False,
            is_windows=False,
            is_apple_silicon=False,
            session_type=None,
        )
        assert info.is_wayland is False
        assert info.is_x11 is False


@pytest.mark.unit
class TestDetectAppleSilicon:
    """Tests for _detect_apple_silicon function."""

    @patch("platform.system")
    @patch("platform.machine")
    def test_apple_silicon_detected(self, mock_machine, mock_system):
        """Test detection of Apple Silicon (M1/M2/M3)."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"
        assert _detect_apple_silicon() is True

    @patch("platform.system")
    @patch("platform.machine")
    def test_intel_mac(self, mock_machine, mock_system):
        """Test Intel Mac is not detected as Apple Silicon."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "x86_64"
        assert _detect_apple_silicon() is False

    @patch("platform.system")
    @patch("platform.machine")
    def test_non_macos(self, mock_machine, mock_system):
        """Test non-macOS platforms return False."""
        mock_system.return_value = "Linux"
        mock_machine.return_value = "arm64"
        assert _detect_apple_silicon() is False

    @patch("platform.system")
    @patch("platform.machine")
    def test_case_insensitive_machine(self, mock_machine, mock_system):
        """Test that machine type is case-insensitive."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "ARM64"
        assert _detect_apple_silicon() is True


@pytest.mark.unit
class TestDetectSessionType:
    """Tests for _detect_session_type function."""

    @patch("platform.system")
    def test_wayland_via_xdg_session_type(self, mock_system, monkeypatch):
        """Test Wayland detection via XDG_SESSION_TYPE."""
        mock_system.return_value = "Linux"
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        assert _detect_session_type() == "wayland"

    @patch("platform.system")
    def test_x11_via_xdg_session_type(self, mock_system, monkeypatch):
        """Test X11 detection via XDG_SESSION_TYPE."""
        mock_system.return_value = "Linux"
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        assert _detect_session_type() == "x11"

    @patch("platform.system")
    def test_wayland_via_wayland_display(self, mock_system, monkeypatch):
        """Test Wayland detection via WAYLAND_DISPLAY fallback."""
        mock_system.return_value = "Linux"
        monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        assert _detect_session_type() == "wayland"

    @patch("platform.system")
    def test_x11_via_display(self, mock_system, monkeypatch):
        """Test X11 detection via DISPLAY fallback."""
        mock_system.return_value = "Linux"
        monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.setenv("DISPLAY", ":0")
        assert _detect_session_type() == "x11"

    @patch("platform.system")
    def test_non_linux_returns_none(self, mock_system):
        """Test that non-Linux platforms return None."""
        mock_system.return_value = "Darwin"
        assert _detect_session_type() is None

    @patch("platform.system")
    def test_no_env_vars_returns_none(self, mock_system, monkeypatch):
        """Test that missing environment variables return None."""
        mock_system.return_value = "Linux"
        monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.delenv("DISPLAY", raising=False)
        assert _detect_session_type() is None

    @patch("platform.system")
    def test_case_insensitive_xdg_session_type(self, mock_system, monkeypatch):
        """Test that XDG_SESSION_TYPE is case-insensitive."""
        mock_system.return_value = "Linux"
        monkeypatch.setenv("XDG_SESSION_TYPE", "WAYLAND")
        assert _detect_session_type() == "wayland"


@pytest.mark.unit
@pytest.mark.macos
class TestDetectPlatformMacOS:
    """Tests for detect_platform on macOS."""

    @patch("platform.system")
    @patch("platform.machine")
    def test_macos_intel(self, mock_machine, mock_system):
        """Test macOS Intel detection."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "x86_64"

        info = detect_platform()

        assert info.os_name == "Darwin"
        assert info.is_macos is True
        assert info.is_linux is False
        assert info.is_windows is False
        assert info.is_apple_silicon is False
        assert info.session_type is None

    @patch("platform.system")
    @patch("platform.machine")
    def test_macos_apple_silicon(self, mock_machine, mock_system):
        """Test macOS Apple Silicon detection."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        info = detect_platform()

        assert info.os_name == "Darwin"
        assert info.is_macos is True
        assert info.is_apple_silicon is True
        assert info.session_type is None


@pytest.mark.unit
@pytest.mark.linux
class TestDetectPlatformLinux:
    """Tests for detect_platform on Linux."""

    @patch("platform.system")
    def test_linux_wayland(self, mock_system, monkeypatch):
        """Test Linux Wayland detection."""
        mock_system.return_value = "Linux"
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")

        info = detect_platform()

        assert info.os_name == "Linux"
        assert info.is_linux is True
        assert info.is_macos is False
        assert info.is_windows is False
        assert info.is_apple_silicon is False
        assert info.session_type == "wayland"
        assert info.is_wayland is True

    @patch("platform.system")
    def test_linux_x11(self, mock_system, monkeypatch):
        """Test Linux X11 detection."""
        mock_system.return_value = "Linux"
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")

        info = detect_platform()

        assert info.os_name == "Linux"
        assert info.is_linux is True
        assert info.session_type == "x11"
        assert info.is_x11 is True


@pytest.mark.unit
class TestGetPlatformInfo:
    """Tests for get_platform_info caching."""

    def test_caching_behavior(self, monkeypatch):
        """Test that platform info is cached."""
        import whisper_dictation.platform.detection as detection_module

        # Reset the cache
        monkeypatch.setattr(detection_module, "_platform_info", None)

        # Mock platform.system
        mock_system = MagicMock(return_value="Linux")
        monkeypatch.setattr("platform.system", mock_system)

        # First call should detect platform
        info1 = detection_module.get_platform_info()
        first_call_count = mock_system.call_count

        # Second call should use cached value
        info2 = detection_module.get_platform_info()
        second_call_count = mock_system.call_count

        # Should not call platform.system again
        assert second_call_count == first_call_count

        # Both should be the same object
        assert info1 is info2

        # Clean up - reset cache
        monkeypatch.setattr(detection_module, "_platform_info", None)
