"""Unit tests for ydotool text injector module."""

import subprocess
from unittest.mock import patch

import pytest

from dictation.platform.text_injection.ydotool_injector import (
    YdotoolTextInjector,
)


@pytest.mark.unit
@pytest.mark.wayland
class TestYdotoolTextInjectorInitialization:
    """Tests for YdotoolTextInjector initialization."""

    @patch("shutil.which")
    def test_initialization_with_ydotool(self, mock_which):
        """Test initialization when ydotool is available."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()

        assert injector is not None
        mock_which.assert_called_once_with("ydotool")

    @patch("shutil.which")
    def test_initialization_without_ydotool_raises_error(self, mock_which):
        """Test that missing ydotool raises RuntimeError."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="ydotool is not installed"):
            YdotoolTextInjector()


@pytest.mark.unit
@pytest.mark.wayland
class TestYdotoolTextInjectorInjectText:
    """Tests for inject_text method."""

    @patch("shutil.which")
    def test_inject_simple_text(self, mock_which, mock_subprocess):
        """Test injecting simple text."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()
        injector.inject_text("Hello world")

        # Verify subprocess.run was called with correct arguments
        mock_subprocess.assert_called_once_with(
            ["ydotool", "type", "Hello world"], check=True
        )

    @patch("shutil.which")
    def test_inject_empty_string(self, mock_which, mock_subprocess):
        """Test that empty string doesn't call ydotool."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()
        injector.inject_text("")

        # Should not call subprocess.run for empty string
        mock_subprocess.assert_not_called()

    @patch("shutil.which")
    def test_inject_text_with_special_characters(self, mock_which, mock_subprocess):
        """Test injecting text with special characters."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()
        injector.inject_text("Test @#$%")

        mock_subprocess.assert_called_once_with(
            ["ydotool", "type", "Test @#$%"], check=True
        )

    @patch("shutil.which")
    def test_inject_text_with_newlines(self, mock_which, mock_subprocess):
        """Test injecting text with newlines."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()
        injector.inject_text("Line1\nLine2")

        mock_subprocess.assert_called_once_with(
            ["ydotool", "type", "Line1\nLine2"], check=True
        )


@pytest.mark.unit
@pytest.mark.wayland
class TestYdotoolTextInjectorErrorHandling:
    """Tests for error handling in YdotoolTextInjector."""

    @patch("shutil.which")
    def test_handles_subprocess_error(self, mock_which, mock_subprocess, capsys):
        """Test that subprocess errors are handled gracefully."""
        mock_which.return_value = "/usr/bin/ydotool"
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "ydotool")

        injector = YdotoolTextInjector()
        injector.inject_text("Test")

        # Should have printed error message
        captured = capsys.readouterr()
        assert "Failed to inject text with ydotool" in captured.out

    @patch("shutil.which")
    def test_handles_general_exception(self, mock_which, mock_subprocess, capsys):
        """Test that general exceptions are handled gracefully."""
        mock_which.return_value = "/usr/bin/ydotool"
        mock_subprocess.side_effect = Exception("Unexpected error")

        injector = YdotoolTextInjector()
        injector.inject_text("Test")

        # Should have printed error message
        captured = capsys.readouterr()
        assert "Error injecting text" in captured.out


@pytest.mark.unit
@pytest.mark.wayland
class TestYdotoolTextInjectorIntegration:
    """Integration-style tests for YdotoolTextInjector."""

    @patch("shutil.which")
    def test_full_injection_workflow(self, mock_which, mock_subprocess):
        """Test complete text injection workflow."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()
        text = "This is a test message."
        injector.inject_text(text)

        # Verify ydotool was called with correct text
        mock_subprocess.assert_called_once_with(["ydotool", "type", text], check=True)

    @patch("shutil.which")
    def test_multiple_injections(self, mock_which, mock_subprocess):
        """Test that injector can be reused for multiple injections."""
        mock_which.return_value = "/usr/bin/ydotool"

        injector = YdotoolTextInjector()

        injector.inject_text("First")
        injector.inject_text("Second")

        # Should have been called twice
        assert mock_subprocess.call_count == 2

        # Verify calls
        calls = mock_subprocess.call_args_list
        assert calls[0][0][0] == ["ydotool", "type", "First"]
        assert calls[1][0][0] == ["ydotool", "type", "Second"]
