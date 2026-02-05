"""Unit tests for transcriber module."""

import pytest

from dictation.core.transcriber import LANGUAGE_MAP


@pytest.mark.unit
class TestQwen3TranscriberInitialization:
    """Tests for Qwen3Transcriber initialization."""

    def test_default_initialization(self, mock_qwen_asr):
        """Test initialization with default model."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber()

        assert transcriber.get_model_name() == "Qwen/Qwen3-ASR-0.6B"
        mock_qwen_asr["class"].from_pretrained.assert_called_once_with(
            "Qwen/Qwen3-ASR-0.6B"
        )

    def test_custom_model_initialization(self, mock_qwen_asr):
        """Test initialization with custom model name."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber(model_name="Qwen/Qwen3-ASR-1.7B")

        assert transcriber.get_model_name() == "Qwen/Qwen3-ASR-1.7B"
        mock_qwen_asr["class"].from_pretrained.assert_called_once_with(
            "Qwen/Qwen3-ASR-1.7B"
        )

    def test_initialization_without_qwen_asr(self, monkeypatch):
        """Test that missing qwen-asr raises ImportError."""
        import sys

        original_modules = sys.modules.copy()

        for key in list(sys.modules.keys()):
            if key.startswith("qwen_asr"):
                monkeypatch.delitem(sys.modules, key)

        def mock_import(name, *args, **kwargs):
            if name == "qwen_asr":
                raise ImportError("No module named 'qwen_asr'")
            return original_modules.get(name)

        monkeypatch.setattr("builtins.__import__", mock_import)

        from dictation.core.transcriber import Qwen3Transcriber

        with pytest.raises(ImportError, match="qwen-asr is not installed"):
            Qwen3Transcriber()


@pytest.mark.unit
class TestQwen3TranscriberTranscribe:
    """Tests for Qwen3Transcriber transcribe method."""

    def test_transcribe_basic(self, mock_qwen_asr, sample_audio):
        """Test basic transcription."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber()
        result = transcriber.transcribe(sample_audio)

        # Verify model.transcribe was called with audio tuple
        mock_qwen_asr["instance"].transcribe.assert_called_once()
        call_args = mock_qwen_asr["instance"].transcribe.call_args
        audio_arg = call_args[0][0]
        assert isinstance(audio_arg, tuple)
        assert audio_arg[1] == 16000  # sample rate

        # No language specified → language=None passed
        assert call_args[1]["language"] is None

        assert result == "Hello world"

    def test_transcribe_with_language(self, mock_qwen_asr, sample_audio):
        """Test transcription with language parameter."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber()
        transcriber.transcribe(sample_audio, language="es")

        call_kwargs = mock_qwen_asr["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] == "Spanish"

    def test_transcribe_with_none_language(self, mock_qwen_asr, sample_audio):
        """Test transcription with None language passes None."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber()
        transcriber.transcribe(sample_audio, language=None)

        call_kwargs = mock_qwen_asr["instance"].transcribe.call_args[1]
        assert call_kwargs["language"] is None

    def test_transcribe_strips_whitespace(self, mock_qwen_asr, sample_audio):
        """Test that result is stripped of whitespace."""
        from dictation.core.transcriber import Qwen3Transcriber

        mock_qwen_asr["result"].text = "  Text with whitespace  "

        transcriber = Qwen3Transcriber()
        result = transcriber.transcribe(sample_audio)

        assert result == "Text with whitespace"

    def test_transcribe_empty_results(self, mock_qwen_asr, sample_audio):
        """Test handling of empty results list."""
        from dictation.core.transcriber import Qwen3Transcriber

        mock_qwen_asr["instance"].transcribe.return_value = []

        transcriber = Qwen3Transcriber()
        result = transcriber.transcribe(sample_audio)

        assert result == ""


@pytest.mark.unit
class TestQwen3TranscriberGetModelName:
    """Tests for Qwen3Transcriber get_model_name method."""

    def test_get_model_name_default(self, mock_qwen_asr):
        """Test get_model_name with default model."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber()

        assert transcriber.get_model_name() == "Qwen/Qwen3-ASR-0.6B"

    def test_get_model_name_custom(self, mock_qwen_asr):
        """Test get_model_name with custom model."""
        from dictation.core.transcriber import Qwen3Transcriber

        transcriber = Qwen3Transcriber(model_name="Qwen/Qwen3-ASR-1.7B")

        assert transcriber.get_model_name() == "Qwen/Qwen3-ASR-1.7B"


@pytest.mark.unit
class TestLanguageMap:
    """Tests for LANGUAGE_MAP."""

    def test_common_languages_mapped(self):
        """Test that common languages are in the map."""
        assert LANGUAGE_MAP["en"] == "English"
        assert LANGUAGE_MAP["es"] == "Spanish"
        assert LANGUAGE_MAP["fr"] == "French"
        assert LANGUAGE_MAP["de"] == "German"
        assert LANGUAGE_MAP["zh"] == "Chinese"
        assert LANGUAGE_MAP["ja"] == "Japanese"
        assert LANGUAGE_MAP["ko"] == "Korean"

    def test_unknown_language_not_in_map(self):
        """Test that unknown language codes are not in the map."""
        assert "xx" not in LANGUAGE_MAP
        assert "unknown" not in LANGUAGE_MAP
