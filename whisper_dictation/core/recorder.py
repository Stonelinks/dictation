"""Audio recording functionality."""

import threading
from collections.abc import Callable

import numpy as np
import pyaudio
from numpy.typing import NDArray


class Recorder:
    """Audio recorder for speech dictation."""

    def __init__(
        self,
        sample_rate: int = 16000,
        frames_per_buffer: int = 1024,
        max_duration: float | None = None,
    ):
        """
        Initialize the audio recorder.

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            frames_per_buffer: Number of frames per buffer (default: 1024)
            max_duration: Maximum recording duration in seconds (default: None)
        """
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.max_duration = max_duration
        self.recording = False
        self._stop_flag = threading.Event()
        self._record_thread: threading.Thread | None = None
        self._on_complete: Callable[[NDArray[np.float32]], None] | None = None

    def start(self, on_complete: Callable[[NDArray[np.float32]], None]) -> None:
        """
        Start recording audio.

        Args:
            on_complete: Callback function to call with audio data when recording completes
        """
        if self.recording:
            raise RuntimeError("Recording is already in progress")

        self._on_complete = on_complete
        self._stop_flag.clear()
        self._record_thread = threading.Thread(target=self._record_impl)
        self._record_thread.start()

        # Start auto-stop timer if max_duration is set
        if self.max_duration is not None:
            threading.Timer(self.max_duration, self.stop).start()

    def stop(self) -> None:
        """Stop recording audio."""
        if not self.recording:
            return

        self._stop_flag.set()
        if self._record_thread is not None:
            self._record_thread.join()
            self._record_thread = None

    def is_recording(self) -> bool:
        """
        Check if currently recording.

        Returns:
            bool: True if recording, False otherwise
        """
        return self.recording

    def _record_impl(self) -> None:
        """Internal method that performs the actual recording."""
        self.recording = True

        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                frames_per_buffer=self.frames_per_buffer,
                input=True,
            )

            frames = []

            while not self._stop_flag.is_set():
                try:
                    data = stream.read(
                        self.frames_per_buffer, exception_on_overflow=False
                    )
                    frames.append(data)
                except Exception as e:
                    print(f"Error reading audio stream: {e}")
                    break

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Convert audio data from int16 to float32 normalized to [-1, 1]
            audio_data = (
                np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32)
                / 32768.0
            )

            # Call the completion callback with the audio data
            if self._on_complete is not None and len(audio_data) > 0:
                self._on_complete(audio_data)

        except Exception as e:
            print(f"Recording error: {e}")
        finally:
            self.recording = False
