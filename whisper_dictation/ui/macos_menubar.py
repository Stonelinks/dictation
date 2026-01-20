"""macOS menu bar UI for dictation."""

import threading
import time
from collections.abc import Callable

from .base import DictationUI


class MacOSMenuBarUI(DictationUI):
    """macOS menu bar interface using rumps."""

    def __init__(
        self,
        on_start_recording: Callable[[], None],
        on_stop_recording: Callable[[], None],
        languages: list[str] | None = None,
        initial_language: str | None = None,
    ):
        """
        Initialize macOS menu bar UI.

        Args:
            on_start_recording: Callback when user starts recording
            on_stop_recording: Callback when user stops recording
            languages: List of language codes for the language menu
            initial_language: Initial language selection
        """
        try:
            import rumps
        except ImportError:
            raise ImportError(
                "rumps is not installed. Install it with: uv sync --extra macos"
            ) from None

        self.rumps = rumps
        self._on_start_recording = on_start_recording
        self._on_stop_recording = on_stop_recording
        self.languages = languages or []
        self.current_language = initial_language or (
            languages[0] if languages else None
        )
        self.is_recording = False
        self.start_time = 0

        # Create the app
        self.app = self._create_app()

    def _create_app(self):
        """Create the rumps application."""
        app = self.rumps.App("Whisper", "⏯")

        # Build menu
        menu = [
            self.rumps.MenuItem("Start Recording", callback=self._start_recording),
            self.rumps.MenuItem("Stop Recording", callback=None),  # Disabled initially
            None,  # Separator
        ]

        # Add language menu items
        if self.languages:
            for lang in self.languages:
                callback = (
                    self._create_language_callback(lang)
                    if lang != self.current_language
                    else None
                )
                menu.append(self.rumps.MenuItem(lang, callback=callback))
            menu.append(None)  # Separator

        app.menu = menu
        return app

    def _create_language_callback(self, lang: str):
        """Create a callback for language selection."""

        def callback(sender):
            self.current_language = lang
            # Update menu callbacks
            for language in self.languages:
                if language in self.app.menu:
                    if language == lang:
                        self.app.menu[language].set_callback(None)
                    else:
                        self.app.menu[language].set_callback(
                            self._create_language_callback(language)
                        )

        return callback

    def _start_recording(self, sender):
        """Start recording callback."""
        if not self.is_recording:
            self.is_recording = True
            self.start_time = time.time()
            self.app.menu["Start Recording"].set_callback(None)
            self.app.menu["Stop Recording"].set_callback(self._stop_recording)
            self._on_start_recording()
            self._update_title()

    def _stop_recording(self, sender):
        """Stop recording callback."""
        if self.is_recording:
            self.is_recording = False
            self.app.title = "⏯"
            self.app.menu["Stop Recording"].set_callback(None)
            self.app.menu["Start Recording"].set_callback(self._start_recording)
            self._on_stop_recording()

    def _update_title(self):
        """Update the menu bar title with recording timer."""
        if self.is_recording:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.app.title = f"({minutes:02d}:{seconds:02d}) 🔴"
            threading.Timer(1, self._update_title).start()

    def run(self) -> None:
        """Run the menu bar UI (blocking)."""
        print("[*] Starting menu bar app...")
        self.app.run()

    def on_recording_start(self) -> None:
        """Called when recording starts."""
        print("[*] Recording...")

    def on_recording_stop(self) -> None:
        """Called when recording stops."""
        print("[*] Transcribing...")

    def on_transcription_complete(self, text: str) -> None:
        """Called when transcription completes."""
        print(f"[✓] Done: {text}")

    def on_error(self, error: str) -> None:
        """Called when an error occurs."""
        print(f"[!] Error: {error}")

    def get_current_language(self) -> str | None:
        """Get the currently selected language."""
        return self.current_language

    def toggle_recording(self) -> None:
        """Toggle recording state (for keyboard shortcuts)."""
        if self.is_recording:
            self._stop_recording(None)
        else:
            self._start_recording(None)
