"""Main entry point for the whisper dictation application."""

import sys
import threading
from collections.abc import Callable

from .cli import parse_arguments
from .config import create_default_config, validate_config
from .core.recorder import Recorder
from .core.text_processor import normalize_text
from .core.transcriber import StandardWhisperTranscriber, WhisperTranscriber
from .platform.keyboard.base import KeyboardListener
from .platform.text_injection.base import TextInjector
from .ui.base import DictationUI


def create_transcriber(config) -> WhisperTranscriber:
    """
    Create transcriber based on configuration.

    Args:
        config: DictationConfig instance

    Returns:
        WhisperTranscriber: Transcriber instance
    """
    print(f"[*] Loading Whisper model: {config.model_name}")
    return StandardWhisperTranscriber(config.model_name)


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
    Create keyboard listener based on platform and configuration.

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
        from .platform.keyboard.pynput_listener import (
            PynputDoubleCommandListener,
            PynputKeyboardListener,
        )

        if config.use_double_cmd:
            print("[i] Using double Right-Command keyboard listener")
            return PynputDoubleCommandListener()
        else:
            print(f"[i] Using pynput keyboard listener (hotkey: {config.hotkey})")
            return PynputKeyboardListener(config.hotkey)


def create_ui(
    config,
    keyboard_listener: KeyboardListener,
    recorder: Recorder,
    on_start_recording: Callable[[], None],
    on_stop_recording: Callable[[], None],
) -> DictationUI:
    """
    Create UI based on configuration.

    Args:
        config: DictationConfig instance
        keyboard_listener: Keyboard listener instance
        recorder: Recorder instance
        on_start_recording: Callback when recording starts
        on_stop_recording: Callback when recording stops

    Returns:
        DictationUI: UI instance
    """
    if config.ui_mode == "gui":
        from .ui.macos_menubar import MacOSMenuBarUI

        print("[i] Using macOS menu bar GUI")
        return MacOSMenuBarUI(
            on_start_recording=on_start_recording,
            on_stop_recording=on_stop_recording,
            languages=config.languages,
            initial_language=config.default_language,
        )
    else:
        from .ui.cli_ui import CLIUI

        hotkey_desc = "double Right-Cmd" if config.use_double_cmd else config.hotkey
        print("[i] Using CLI interface")
        return CLIUI(
            keyboard_listener=keyboard_listener,
            recorder=recorder,
            hotkey_description=hotkey_desc,
            on_start_recording=on_start_recording,
            on_stop_recording=on_stop_recording,
        )


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

        # Create UI
        self.ui = create_ui(
            config,
            self.keyboard_listener,
            self.recorder,
            self.on_start_recording,
            self.on_stop_recording,
        )

        self.current_language = config.default_language
        self.is_recording = False

    def on_start_recording(self) -> None:
        """Handle recording start."""
        if self.is_recording:
            return

        self.is_recording = True
        self.ui.on_recording_start()

        # Get language from UI if it's a GUI
        if hasattr(self.ui, "get_current_language"):
            self.current_language = self.ui.get_current_language()

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
        # For GUI mode, the keyboard listener needs to be started separately
        # because rumps.App.run() is blocking
        if self.config.ui_mode == "gui":
            import time

            from pynput import keyboard

            # Set up thread exception handler to catch listener errors
            listener_error = []

            def thread_exception_handler(args):
                """Catch exceptions from keyboard listener thread."""
                listener_error.append(args.exc_value)

            original_excepthook = threading.excepthook
            threading.excepthook = thread_exception_handler

            # Create hotkey handler
            def toggle_handler():
                if hasattr(self.ui, "toggle_recording"):
                    self.ui.toggle_recording()

            try:
                # Start keyboard listener
                self.keyboard_listener.start(toggle_handler)

                # Start listener thread
                listener = keyboard.Listener(
                    on_press=lambda key: None, on_release=lambda key: None
                )
                listener.start()

                # Give the thread time to start and check for errors
                time.sleep(0.5)
                if listener_error:
                    raise listener_error[0]
                if not listener.running:
                    raise RuntimeError("Keyboard listener failed to start")

            except Exception as e:
                # Check if this is the PyObjC/accessibility error
                error_type = type(e).__name__
                is_pyobjc_error = (
                    "KeyError" in error_type or "AXIsProcessTrusted" in str(e)
                )

                error_msg = "\n[!] Failed to start keyboard listener.\n\n"
                if is_pyobjc_error:
                    error_msg += (
                        "This appears to be a PyObjC compatibility issue with your macOS version.\n\n"
                        "To fix:\n"
                        "  • Try updating PyObjC packages:\n"
                        "    uv pip install --upgrade pyobjc-core pyobjc-framework-Quartz\n\n"
                        "  • Ensure accessibility permissions are granted:\n"
                        "    System Settings → Privacy & Security → Accessibility\n"
                        "    Add and enable your terminal app (Terminal.app, iTerm2, etc.)\n\n"
                    )
                else:
                    error_msg += (
                        "This is likely due to accessibility permissions not being granted.\n\n"
                        "To fix:\n"
                        "  • Grant accessibility permissions:\n"
                        "    System Settings → Privacy & Security → Accessibility\n"
                        "    Add and enable your terminal app (Terminal.app, iTerm2, etc.)\n\n"
                    )

                error_msg += (
                    "  • Try CLI mode instead (no accessibility permissions required):\n"
                    "    whisper-dictation --no-gui\n\n"
                    f"Technical details: {error_type}: {e}"
                )
                print(error_msg, file=sys.stderr)
                threading.excepthook = original_excepthook
                sys.exit(1)

            # Restore original exception handler
            threading.excepthook = original_excepthook

        # Run UI (blocking)
        self.ui.run()


def main() -> None:
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    try:
        # Create configuration
        config = create_default_config(
            model=args.model,
            hotkey=args.hotkey,
            use_double_cmd=args.double_cmd,
            languages=args.language,
            max_time=args.max_time,
            no_gui=args.no_gui,
        )

        # Validate configuration
        validate_config(config)

        # Print platform info
        print(f"[i] Platform: {config.platform.os_name}")
        if config.platform.is_apple_silicon:
            print("[i] Apple Silicon detected")
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


if __name__ == "__main__":
    main()
