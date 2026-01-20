"""Unit tests for transcriber module."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from whisper_dictation.core.transcriber import StandardWhisperTranscriber


@pytest.mark.unit
class TestStandardWhisperTranscriberInitialization:
    """Tests for StandardWhisperTranscriber initialization."""

    def test_default_initialization(self, mock_whisper_model):
        """Test initialization with default model."""
        transcriber = StandardWhisperTranscriber()

        assert transcriber.model_name == "large-v3"
        mock_whisper_model["class"].assert_called_once_with(
            "large-v3", device="cpu", compute_type="int8"
        )

    def test_custom_model_initialization(self, mock_whisper_model):
        """Test initialization with custom model name."""
        transcriber = StandardWhisperTranscriber(model_name="base")

        assert transcriber.model_name == "base"
        mock_whisper_model["class"].assert_called_once_with(
            "base", device="cpu", compute_type="int8"
        )

    def test_initialization_without_faster_whisper(self, monkeypatch):
        """Test that missing faster-whisper raises ImportError."""
        # Remove faster_whisper from sys.modules to simulate it not being installed
        import sys

        original_modules = sys.modules.copy()

        # Remove faster_whisper if it exists
        if "faster_whisper" in sys.modules:
            monkeypatch.delitem(sys.modules, "faster_whisper")

        # Mock the import to raise ImportError
        def mock_import(name, *args, **kwargs):
            if name == "faster_whisper":
                raise ImportError("No module named 'faster_whisper'")
            return original_modules.get(name)

        monkeypatch.setattr("builtins.__import__", mock_import)

        with pytest.raises(ImportError, match="faster-whisper is not installed"):
            StandardWhisperTranscriber()


@pytest.mark.unit
class TestStandardWhisperTranscriberTranscribe:
    """Tests for transcribe method."""

    def test_transcribe_basic(self, mock_whisper_model, sample_audio):
        """Test basic transcription."""
        transcriber = StandardWhisperTranscriber()

        result = transcriber.transcribe(sample_audio)

        # Verify model.transcribe was called
        mock_whisper_model["instance"].transcribe.assert_called_once()
        call_args = mock_whisper_model["instance"].transcribe.call_args

        # Check audio data was passed
        np.testing.assert_array_equal(call_args[0][0], sample_audio)

        # Check result
        assert result == "Hello world"  # Based on mock setup in conftest

    def test_transcribe_with_language(self, mock_whisper_model, sample_audio):
        """Test transcription with language parameter."""
        transcriber = StandardWhisperTranscriber()

        _result = transcriber.transcribe(sample_audio, language="es")

        # Verify language was passed to model
        call_kwargs = mock_whisper_model["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] == "es"

    def test_transcribe_with_none_language(self, mock_whisper_model, sample_audio):
        """Test transcription with None language (auto-detect)."""
        transcriber = StandardWhisperTranscriber()

        _result = transcriber.transcribe(sample_audio, language=None)

        # Verify language=None was passed to model
        call_kwargs = mock_whisper_model["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] is None

    def test_transcribe_joins_segments(self, mock_whisper_model, sample_audio):
        """Test that multiple segments are joined with spaces."""
        transcriber = StandardWhisperTranscriber()

        # Create mock segments
        segment1 = MagicMock()
        segment1.text = "First segment"
        segment2 = MagicMock()
        segment2.text = "Second segment"
        segment3 = MagicMock()
        segment3.text = "Third segment"

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [segment1, segment2, segment3],
            mock_info,
        )

        result = transcriber.transcribe(sample_audio)

        assert result == "First segment Second segment Third segment"

    def test_transcribe_strips_whitespace(self, mock_whisper_model, sample_audio):
        """Test that result is stripped of leading/trailing whitespace."""
        transcriber = StandardWhisperTranscriber()

        # Create mock segment with extra whitespace
        segment = MagicMock()
        segment.text = "  Text with whitespace  "

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [segment],
            mock_info,
        )

        result = transcriber.transcribe(sample_audio)

        assert result == "Text with whitespace"

    def test_transcribe_empty_segments(self, mock_whisper_model, sample_audio):
        """Test transcription with no segments."""
        transcriber = StandardWhisperTranscriber()

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [],
            mock_info,
        )

        result = transcriber.transcribe(sample_audio)

        assert result == ""

    def test_transcribe_single_segment(self, mock_whisper_model, sample_audio):
        """Test transcription with single segment."""
        transcriber = StandardWhisperTranscriber()

        segment = MagicMock()
        segment.text = "Single segment"

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [segment],
            mock_info,
        )

        result = transcriber.transcribe(sample_audio)

        assert result == "Single segment"

    def test_transcribe_with_empty_audio(self, mock_whisper_model, empty_audio):
        """Test transcription with empty audio."""
        transcriber = StandardWhisperTranscriber()

        _result = transcriber.transcribe(empty_audio)

        # Should still work, just return whatever model returns
        mock_whisper_model["instance"].transcribe.assert_called_once()

    def test_transcribe_preserves_segment_order(self, mock_whisper_model, sample_audio):
        """Test that segment order is preserved in result."""
        transcriber = StandardWhisperTranscriber()

        segment1 = MagicMock()
        segment1.text = "One"
        segment2 = MagicMock()
        segment2.text = "Two"
        segment3 = MagicMock()
        segment3.text = "Three"

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [segment1, segment2, segment3],
            mock_info,
        )

        result = transcriber.transcribe(sample_audio)

        assert result == "One Two Three"


@pytest.mark.unit
class TestStandardWhisperTranscriberGetModelName:
    """Tests for get_model_name method."""

    def test_get_model_name_default(self, mock_whisper_model):
        """Test get_model_name with default model."""
        transcriber = StandardWhisperTranscriber()

        assert transcriber.get_model_name() == "large-v3"

    def test_get_model_name_custom(self, mock_whisper_model):
        """Test get_model_name with custom model."""
        transcriber = StandardWhisperTranscriber(model_name="tiny")

        assert transcriber.get_model_name() == "tiny"

    @pytest.mark.parametrize(
        "model_name",
        [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
            "large-v3-turbo",
            "base.en",
        ],
    )
    def test_get_model_name_various_models(self, mock_whisper_model, model_name):
        """Test get_model_name with various model names."""
        transcriber = StandardWhisperTranscriber(model_name=model_name)

        assert transcriber.get_model_name() == model_name


@pytest.mark.unit
class TestStandardWhisperTranscriberIntegration:
    """Integration-style tests for StandardWhisperTranscriber."""

    def test_full_transcription_workflow(self, mock_whisper_model, sample_audio):
        """Test complete transcription workflow."""
        # Create transcriber
        transcriber = StandardWhisperTranscriber(model_name="base")

        # Set up mock for realistic transcription
        seg1 = MagicMock()
        seg1.text = "This is a"
        seg2 = MagicMock()
        seg2.text = "test transcription"

        mock_info = MagicMock()
        mock_whisper_model["instance"].transcribe.return_value = (
            [seg1, seg2],
            mock_info,
        )

        # Transcribe
        result = transcriber.transcribe(sample_audio, language="en")

        # Verify result
        assert result == "This is a test transcription"
        assert transcriber.get_model_name() == "base"

        # Verify model was called correctly
        call_args = mock_whisper_model["instance"].transcribe.call_args
        np.testing.assert_array_equal(call_args[0][0], sample_audio)
        assert call_args[1]["language"] == "en"

    def test_multiple_transcriptions(
        self, mock_whisper_model, sample_audio, short_audio
    ):
        """Test that transcriber can be reused for multiple transcriptions."""
        transcriber = StandardWhisperTranscriber()

        # First transcription
        result1 = transcriber.transcribe(sample_audio, language="en")

        # Second transcription with different audio
        result2 = transcriber.transcribe(short_audio, language="es")

        # Both should succeed
        assert isinstance(result1, str)
        assert isinstance(result2, str)

        # Model should have been called twice
        assert mock_whisper_model["instance"].transcribe.call_count == 2
