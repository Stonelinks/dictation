"""Main entry point for the dictation application."""

import fcntl
import sys
import tempfile
from pathlib import Path

from .cli import parse_arguments
from .config import create_default_config, validate_config
from .core.recorder import Recorder
from .core.text_processor import normalize_text
from .core.transcriber import Qwen3Transcriber, Transcriber
from .platform.keyboard.base import KeyboardListener
from .platform.text_injection.base import TextInjector
from .ui.cli_ui import CLIUI


def create_transcriber(config) -> Transcriber:
    """
    Create transcriber based on configuration.

    Args:
        config: DictationConfig instance

    Returns:
        Transcriber: Transcriber instance
    """
    print(f"[*] Loading Qwen3-ASR model: {config.model_name}")
    return Qwen3Transcriber(config.model_name)


def create_text_injector(config) -> TextInjector:
    """
    Create text injector based on platform.

    Args:
        config: DictationConfig instance

    Returns:
        TextInjector: Text injector instance
    """
    if config.platform.is_wayland:
        from .platform.text_injection.ydotool_injector import YdotoolTextInjector

        print("[i] Using ydotool for text injection (Wayland)")
        return YdotoolTextInjector()
    else:
        from .platform.text_injection.pynput_injector import PynputTextInjector

        print("[i] Using pynput for text injection")
        return PynputTextInjector()


def create_keyboard_listener(config) -> KeyboardListener:
    """
    Create keyboard listener based on platform.

    Args:
        config: DictationConfig instance

    Returns:
        KeyboardListener: Keyboard listener instance
    """
    if config.platform.is_linux:
        from .platform.keyboard.evdev_listener import EvdevKeyboardListener

        print(f"[i] Using evdev keyboard listener (hotkey: {config.hotkey})")
        return EvdevKeyboardListener(config.hotkey)
    else:
        from .platform.keyboard.pynput_listener import PynputKeyboardListener

        print(f"[i] Using pynput keyboard listener (hotkey: {config.hotkey})")
        return PynputKeyboardListener(config.hotkey)


class DictationApp:
    """Main application coordinator."""

    def __init__(self, config):
        """
        Initialize the dictation application.

        Args:
            config: DictationConfig instance
        """
        self.config = config

        # Create components
        self.transcriber = create_transcriber(config)
        self.text_injector = create_text_injector(config)
        self.recorder = Recorder(
            sample_rate=config.sample_rate,
            frames_per_buffer=config.frames_per_buffer,
            max_duration=config.max_recording_time,
        )
        self.keyboard_listener = create_keyboard_listener(config)

        # Create CLI UI
        self.ui = CLIUI(
            keyboard_listener=self.keyboard_listener,
            recorder=self.recorder,
            hotkey_description=config.hotkey,
            on_start_recording=self.on_start_recording,
            on_stop_recording=self.on_stop_recording,
        )

        self.current_language = config.default_language
        self.is_recording = False

    def on_start_recording(self) -> None:
        """Handle recording start."""
        if self.is_recording:
            return

        self.is_recording = True
        self.ui.on_recording_start()

        # Start recording with completion callback
        self.recorder.start(self.on_recording_complete)

    def on_stop_recording(self) -> None:
        """Handle recording stop."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.ui.on_recording_stop()
        self.recorder.stop()

    def on_recording_complete(self, audio_data) -> None:
        """
        Handle recording completion.

        Args:
            audio_data: Recorded audio data
        """
        try:
            # Transcribe
            text = self.transcriber.transcribe(audio_data, self.current_language)

            # Normalize text (fix spacing and punctuation)
            if text:
                text = normalize_text(text)

            # Inject text
            if text:
                self.text_injector.inject_text(text)
                self.ui.on_transcription_complete(text)
            else:
                self.ui.on_error("No text transcribed")

        except Exception as e:
            error_msg = f"Transcription error: {e}"
            print(f"[!] {error_msg}")
            self.ui.on_error(error_msg)

    def run(self) -> None:
        """Run the application."""
        self.ui.run()


def _acquire_instance_lock():
    """Acquire a file lock to ensure only one instance is running.

    Uses fcntl.flock() which is automatically released by the OS
    when the process exits (even on crash/kill).

    Returns the open file handle (must be kept alive for the lock duration).
    """
    lock_path = Path(tempfile.gettempdir()) / "dictation.lock"
    lock_file = open(lock_path, "w")  # noqa: SIM115
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock_file.close()
        print(
            "[!] Another instance of dictation is already running.",
            file=sys.stderr,
        )
        sys.exit(1)
    return lock_file


def main() -> None:
    """Main entry point."""
    # Ensure single instance
    lock_file = _acquire_instance_lock()

    # Parse arguments
    args = parse_arguments()

    try:
        # Create configuration
        config = create_default_config(
            model=args.model,
            hotkey=args.hotkey,
            languages=args.language,
            max_time=args.max_time,
        )

        # Validate configuration
        validate_config(config)

        # Print platform info
        print(f"[i] Platform: {config.platform.os_name}")
        if config.platform.is_apple_silicon:
            print("[i] Apple Silicon detected (Metal acceleration via MPS)")
        if config.platform.is_wayland:
            print("[i] Wayland session detected")
        elif config.platform.is_x11:
            print("[i] X11 session detected")

        # Create and run application
        app = DictationApp(config)
        app.run()

    except KeyboardInterrupt:
        print("\n[i] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        lock_file.close()


if __name__ == "__main__":
    main()
