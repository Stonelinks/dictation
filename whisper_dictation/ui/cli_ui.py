"""CLI user interface for dictation."""

import signal
import sys
import time

from ..core.recorder import Recorder
from ..platform.keyboard.base import KeyboardListener
from .base import DictationUI


class CLIUI(DictationUI):
    """Command-line interface for dictation."""

    def __init__(
        self,
        keyboard_listener: KeyboardListener,
        recorder: Recorder,
        hotkey_description: str = "hotkey",
        on_start_recording=None,
        on_stop_recording=None,
    ):
        """
        Initialize CLI UI.

        Args:
            keyboard_listener: Keyboard listener instance
            recorder: Audio recorder instance
            hotkey_description: Description of the hotkey for user display
            on_start_recording: Callback to call when starting recording
            on_stop_recording: Callback to call when stopping recording
        """
        self.keyboard_listener = keyboard_listener
        self.recorder = recorder
        self.hotkey_description = hotkey_description
        self.on_start_recording_callback = on_start_recording
        self.on_stop_recording_callback = on_stop_recording
        self._running = False
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame) -> None:
        """Handle interrupt signals."""
        print("\n[i] Interrupt received, stopping...")
        self._running = False
        self.keyboard_listener.stop()
        if self.recorder.is_recording():
            self.recorder.stop()
        sys.exit(0)

    def run(self) -> None:
        """Run the CLI UI (blocking)."""
        self._running = True

        print("\n=== Whisper Dictation ===")
        print(f"[*] Press {self.hotkey_description} to start/stop recording")
        print("[*] Press Ctrl+C to exit\n")

        # Start keyboard listener
        self.keyboard_listener.start(self._on_hotkey)

        # Keep running until interrupted
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._signal_handler(None, None)

    def _on_hotkey(self) -> None:
        """Handle hotkey press."""
        if self.recorder.is_recording():
            # Stop recording
            if self.on_stop_recording_callback:
                self.on_stop_recording_callback()
        else:
            # Start recording
            if self.on_start_recording_callback:
                self.on_start_recording_callback()

    def on_recording_start(self) -> None:
        """Called when recording starts."""
        print("[*] Recording started...")

    def on_recording_stop(self) -> None:
        """Called when recording stops."""
        print("[*] Recording stopped.")

    def on_transcription_complete(self, text: str) -> None:
        """Called when transcription completes."""
        print(f"[✓] Transcribed: {text}")

    def on_error(self, error: str) -> None:
        """Called when an error occurs."""
        print(f"[!] Error: {error}")
