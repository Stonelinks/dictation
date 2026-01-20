"""Unit tests for pynput text injector module."""

from unittest.mock import call, patch

import pytest

from whisper_dictation.platform.text_injection.pynput_injector import PynputTextInjector


@pytest.mark.unit
class TestPynputTextInjectorInitialization:
    """Tests for PynputTextInjector initialization."""

    def test_default_initialization(self, mock_pynput_controller):
        """Test initialization with default char_delay."""
        injector = PynputTextInjector()

        assert injector.char_delay == 0.0025
        mock_pynput_controller["class"].assert_called_once()

    def test_custom_char_delay(self, mock_pynput_controller):
        """Test initialization with custom char_delay."""
        injector = PynputTextInjector(char_delay=0.01)

        assert injector.char_delay == 0.01

    def test_zero_char_delay(self, mock_pynput_controller):
        """Test initialization with zero char_delay."""
        injector = PynputTextInjector(char_delay=0.0)

        assert injector.char_delay == 0.0


@pytest.mark.unit
class TestPynputTextInjectorInjectText:
    """Tests for inject_text method."""

    def test_inject_simple_text(self, mock_pynput_controller):
        """Test injecting simple text."""
        injector = PynputTextInjector()

        injector.inject_text("Hello")

        # Verify type was called for each character
        assert mock_pynput_controller["instance"].type.call_count == 5
        expected_calls = [call("H"), call("e"), call("l"), call("l"), call("o")]
        mock_pynput_controller["instance"].type.assert_has_calls(expected_calls)

    def test_inject_text_with_spaces(self, mock_pynput_controller):
        """Test injecting text with spaces."""
        injector = PynputTextInjector()

        injector.inject_text("Hello world")

        # Should type all characters including space
        assert mock_pynput_controller["instance"].type.call_count == 11

    def test_inject_empty_string(self, mock_pynput_controller):
        """Test injecting empty string."""
        injector = PynputTextInjector()

        injector.inject_text("")

        # Should not type anything
        mock_pynput_controller["instance"].type.assert_not_called()

    def test_inject_text_with_punctuation(self, mock_pynput_controller):
        """Test injecting text with punctuation."""
        injector = PynputTextInjector()

        injector.inject_text("Hello, world!")

        # Should type all characters including punctuation
        assert mock_pynput_controller["instance"].type.call_count == 13
        # Check that punctuation is included
        call_args_list = [
            call[0][0]
            for call in mock_pynput_controller["instance"].type.call_args_list
        ]
        assert "," in call_args_list
        assert "!" in call_args_list

    def test_inject_text_with_numbers(self, mock_pynput_controller):
        """Test injecting text with numbers."""
        injector = PynputTextInjector()

        injector.inject_text("Test 123")

        assert mock_pynput_controller["instance"].type.call_count == 8
        call_args_list = [
            call[0][0]
            for call in mock_pynput_controller["instance"].type.call_args_list
        ]
        assert "1" in call_args_list
        assert "2" in call_args_list
        assert "3" in call_args_list

    @patch("time.sleep")
    def test_inject_text_with_delay(self, mock_sleep, mock_pynput_controller):
        """Test that delay is applied between characters."""
        injector = PynputTextInjector(char_delay=0.01)

        injector.inject_text("Hi")

        # Should sleep after each character
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.01)

    @patch("time.sleep")
    def test_inject_text_no_delay_when_zero(self, mock_sleep, mock_pynput_controller):
        """Test that no sleep is called when char_delay is zero."""
        injector = PynputTextInjector(char_delay=0.0)

        injector.inject_text("Hi")

        # Should not sleep when delay is 0
        mock_sleep.assert_not_called()

    def test_inject_special_characters(self, mock_pynput_controller):
        """Test injecting special characters."""
        injector = PynputTextInjector()

        injector.inject_text("@#$%")

        assert mock_pynput_controller["instance"].type.call_count == 4
        call_args_list = [
            call[0][0]
            for call in mock_pynput_controller["instance"].type.call_args_list
        ]
        assert "@" in call_args_list
        assert "#" in call_args_list
        assert "$" in call_args_list
        assert "%" in call_args_list

    def test_inject_newline(self, mock_pynput_controller):
        """Test injecting text with newline."""
        injector = PynputTextInjector()

        injector.inject_text("Line1\nLine2")

        assert mock_pynput_controller["instance"].type.call_count == 11
        call_args_list = [
            call[0][0]
            for call in mock_pynput_controller["instance"].type.call_args_list
        ]
        assert "\n" in call_args_list


@pytest.mark.unit
class TestPynputTextInjectorErrorHandling:
    """Tests for error handling in PynputTextInjector."""

    def test_handles_typing_error(self, mock_pynput_controller, capsys):
        """Test that typing errors are handled gracefully."""
        injector = PynputTextInjector()

        # Make type raise an exception for specific character
        def type_side_effect(char):
            if char == "x":
                raise Exception("Typing error")

        mock_pynput_controller["instance"].type.side_effect = type_side_effect

        # Should handle error and continue
        injector.inject_text("text")

        # Should have printed error message for 'x'
        captured = capsys.readouterr()
        assert "Error typing character" in captured.out
        assert "'x'" in captured.out

        # Should have tried to type all characters despite error
        assert mock_pynput_controller["instance"].type.call_count == 4

    def test_continues_after_error(self, mock_pynput_controller):
        """Test that injector continues after encountering error."""
        injector = PynputTextInjector()

        # Make type raise an exception for 'e'
        call_count = [0]

        def type_side_effect(char):
            call_count[0] += 1
            if char == "e":
                raise Exception("Error")

        mock_pynput_controller["instance"].type.side_effect = type_side_effect

        injector.inject_text("hello")

        # Should have tried all 5 characters despite error on 'e'
        assert call_count[0] == 5


@pytest.mark.unit
class TestPynputTextInjectorIntegration:
    """Integration-style tests for PynputTextInjector."""

    @patch("time.sleep")
    def test_full_injection_workflow(self, mock_sleep, mock_pynput_controller):
        """Test complete text injection workflow."""
        injector = PynputTextInjector(char_delay=0.005)

        text = "This is a test."
        injector.inject_text(text)

        # Verify all characters were typed
        assert mock_pynput_controller["instance"].type.call_count == len(text)

        # Verify sleep was called for each character
        assert mock_sleep.call_count == len(text)
        mock_sleep.assert_called_with(0.005)

        # Verify characters were typed in order
        call_args_list = [
            call[0][0]
            for call in mock_pynput_controller["instance"].type.call_args_list
        ]
        assert "".join(call_args_list) == text

    def test_multiple_injections(self, mock_pynput_controller):
        """Test that injector can be reused for multiple injections."""
        injector = PynputTextInjector()

        injector.inject_text("First")
        injector.inject_text("Second")

        # Total calls should be for both texts
        assert mock_pynput_controller["instance"].type.call_count == 11  # 5 + 6
