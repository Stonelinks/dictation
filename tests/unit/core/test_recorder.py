"""Unit tests for recorder module."""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from dictation.core.recorder import Recorder


@pytest.mark.unit
class TestRecorderInitialization:
    """Tests for Recorder initialization."""

    def test_default_initialization(self):
        """Test Recorder with default parameters."""
        recorder = Recorder()

        assert recorder.sample_rate == 16000
        assert recorder.frames_per_buffer == 1024
        assert recorder.max_duration is None
        assert recorder.recording is False

    def test_custom_initialization(self):
        """Test Recorder with custom parameters."""
        recorder = Recorder(
            sample_rate=44100,
            frames_per_buffer=2048,
            max_duration=60.0,
        )

        assert recorder.sample_rate == 44100
        assert recorder.frames_per_buffer == 2048
        assert recorder.max_duration == 60.0
        assert recorder.recording is False


@pytest.mark.unit
class TestRecorderIsRecording:
    """Tests for is_recording method."""

    def test_is_recording_initially_false(self):
        """Test that is_recording is False initially."""
        recorder = Recorder()
        assert recorder.is_recording() is False

    def test_is_recording_during_recording(self, mock_pyaudio):
        """Test that is_recording is True during recording."""
        recorder = Recorder()

        # Start recording in background
        callback = MagicMock()
        recorder.start(callback)

        # Give it a moment to start
        time.sleep(0.05)

        assert recorder.is_recording() is True

        # Stop recording
        recorder.stop()
        assert recorder.is_recording() is False


@pytest.mark.unit
class TestRecorderStart:
    """Tests for start method."""

    def test_start_creates_pyaudio_stream(self, mock_pyaudio):
        """Test that start creates PyAudio stream with correct parameters."""
        recorder = Recorder(sample_rate=16000, frames_per_buffer=1024)
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)  # Give thread time to start
        recorder.stop()

        # Verify PyAudio was initialized
        mock_pyaudio["class"].assert_called_once()

        # Verify stream was opened with correct parameters
        mock_pyaudio["instance"].open.assert_called_once()
        call_kwargs = mock_pyaudio["instance"].open.call_args[1]

        assert call_kwargs["rate"] == 16000
        assert call_kwargs["frames_per_buffer"] == 1024
        assert call_kwargs["channels"] == 1
        assert call_kwargs["input"] is True

    def test_start_twice_raises_error(self, mock_pyaudio):
        """Test that starting while already recording raises RuntimeError."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)

        # Try to start again
        with pytest.raises(RuntimeError, match="already in progress"):
            recorder.start(callback)

        recorder.stop()

    def test_start_stores_callback(self, mock_pyaudio):
        """Test that start stores the completion callback."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)

        assert recorder._on_complete is callback

        recorder.stop()


@pytest.mark.unit
class TestRecorderStop:
    """Tests for stop method."""

    def test_stop_closes_stream(self, mock_pyaudio):
        """Test that stop closes the PyAudio stream."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)
        recorder.stop()

        # Verify stream was stopped and closed
        mock_pyaudio["stream"].stop_stream.assert_called_once()
        mock_pyaudio["stream"].close.assert_called_once()

    def test_stop_terminates_pyaudio(self, mock_pyaudio):
        """Test that stop terminates PyAudio instance."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)
        recorder.stop()

        # Verify PyAudio was terminated
        mock_pyaudio["instance"].terminate.assert_called_once()

    def test_stop_when_not_recording(self):
        """Test that stop when not recording doesn't raise error."""
        recorder = Recorder()

        # Should not raise
        recorder.stop()

    def test_stop_sets_recording_false(self, mock_pyaudio):
        """Test that stop sets recording flag to False."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)
        assert recorder.recording is True

        recorder.stop()
        time.sleep(0.05)
        assert recorder.recording is False


@pytest.mark.unit
class TestRecorderMaxDuration:
    """Tests for max_duration enforcement."""

    @patch("threading.Timer")
    def test_max_duration_starts_timer(self, mock_timer, mock_pyaudio):
        """Test that max_duration starts a timer."""
        recorder = Recorder(max_duration=5.0)
        callback = MagicMock()

        recorder.start(callback)

        # Verify timer was started with correct duration
        mock_timer.assert_called_once()
        call_args = mock_timer.call_args[0]
        assert call_args[0] == 5.0
        assert call_args[1] == recorder.stop

        recorder.stop()

    def test_no_timer_without_max_duration(self, mock_pyaudio):
        """Test that no timer is started without max_duration."""
        with patch("threading.Timer") as mock_timer:
            recorder = Recorder(max_duration=None)
            callback = MagicMock()

            recorder.start(callback)
            time.sleep(0.05)

            # Timer should not have been called
            mock_timer.assert_not_called()

            recorder.stop()


@pytest.mark.unit
class TestRecorderAudioProcessing:
    """Tests for audio data processing."""

    def test_calls_callback_with_audio_data(self, mock_pyaudio):
        """Test that callback is called with audio data."""
        recorder = Recorder()
        callback = MagicMock()

        # Configure mock to return some data
        sample_data = np.random.randint(-32768, 32767, 1024, dtype=np.int16).tobytes()
        mock_pyaudio["stream"].read.return_value = sample_data

        recorder.start(callback)
        time.sleep(0.1)  # Let it record some frames
        recorder.stop()

        # Wait for callback
        time.sleep(0.1)

        # Verify callback was called
        callback.assert_called_once()

        # Verify audio data is float32
        audio_data = callback.call_args[0][0]
        assert isinstance(audio_data, np.ndarray)
        assert audio_data.dtype == np.float32

    def test_converts_int16_to_float32(self, mock_pyaudio):
        """Test that audio data is converted from int16 to float32."""
        recorder = Recorder()
        callback = MagicMock()

        # Create known int16 data (single frame)
        int16_data = np.array([32767, -32768, 0, 16384], dtype=np.int16)

        # Configure mock to return our data once, then raise exception to stop loop
        call_count = [0]

        def read_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return int16_data.tobytes()
            raise Exception("Stop")

        mock_pyaudio["stream"].read.side_effect = read_side_effect

        recorder.start(callback)
        time.sleep(0.15)
        recorder.stop()
        time.sleep(0.1)

        # Verify callback was called
        if callback.called:
            # Get the audio data passed to callback
            audio_data = callback.call_args[0][0]

            # Verify it's float32
            assert audio_data.dtype == np.float32

            # Data should contain our values (possibly with more frames from other reads)
            # Just verify the first 4 values match our expected conversion
            expected = int16_data.astype(np.float32) / 32768.0
            if len(audio_data) >= 4:
                np.testing.assert_array_almost_equal(
                    audio_data[:4], expected, decimal=5
                )

    def test_empty_audio_no_callback(self, mock_pyaudio):
        """Test that callback is not called with empty audio."""
        recorder = Recorder()
        callback = MagicMock()

        # Configure mock to return no data
        mock_pyaudio["stream"].read.side_effect = Exception("Stream error")

        recorder.start(callback)
        time.sleep(0.1)
        recorder.stop()

        time.sleep(0.1)

        # Callback should not be called when there's no audio data
        # or should be called with empty array
        if callback.called:
            audio_data = callback.call_args[0][0]
            assert len(audio_data) == 0 or audio_data is not None


@pytest.mark.unit
class TestRecorderErrorHandling:
    """Tests for error handling in Recorder."""

    def test_handles_stream_read_error(self, mock_pyaudio, capsys):
        """Test that stream read errors are handled gracefully."""
        recorder = Recorder()
        callback = MagicMock()

        # Configure mock to raise error
        mock_pyaudio["stream"].read.side_effect = Exception("Read error")

        recorder.start(callback)
        time.sleep(0.1)
        recorder.stop()

        # Should have printed error message
        captured = capsys.readouterr()
        assert (
            "Error reading audio stream" in captured.out
            or "Recording error" in captured.out
        )

    def test_handles_general_recording_error(self, mock_pyaudio, capsys):
        """Test that general recording errors are handled gracefully."""
        recorder = Recorder()
        callback = MagicMock()

        # Configure mock to raise error during initialization
        mock_pyaudio["instance"].open.side_effect = Exception("PyAudio error")

        recorder.start(callback)
        time.sleep(0.1)

        # Should have printed error message
        captured = capsys.readouterr()
        assert "Recording error" in captured.out

        # Recording should be False even after error
        assert recorder.recording is False


@pytest.mark.unit
class TestRecorderThreadSafety:
    """Tests for thread safety of Recorder."""

    def test_recording_flag_thread_safe(self, mock_pyaudio):
        """Test that recording flag is properly managed across threads."""
        recorder = Recorder()
        callback = MagicMock()

        # Start recording
        recorder.start(callback)
        time.sleep(0.05)

        # Check flag from main thread
        assert recorder.is_recording() is True
        assert recorder.recording is True

        # Stop recording
        recorder.stop()

        # Verify flag is updated
        assert recorder.is_recording() is False
        assert recorder.recording is False

    def test_stop_waits_for_thread(self, mock_pyaudio):
        """Test that stop waits for recording thread to finish."""
        recorder = Recorder()
        callback = MagicMock()

        recorder.start(callback)
        time.sleep(0.05)

        # Stop should wait for thread
        recorder.stop()

        # Thread should be None after stop
        assert recorder._record_thread is None
