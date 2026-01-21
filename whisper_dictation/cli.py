"""Command-line argument parsing."""

import argparse
import sys

from .platform.detection import get_platform_info


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    platform = get_platform_info()

    parser = argparse.ArgumentParser(
        description="Cross-platform multilingual dictation using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (platform-aware)
  whisper-dictation

  # Use a specific model
  whisper-dictation -m large-v3

  # Specify languages
  whisper-dictation -l en,es,fr

  # Custom hotkey
  whisper-dictation -k ctrl+shift

  # Force CLI mode on macOS
  whisper-dictation --no-gui
        """,
    )

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help=(
            "Model name to use: tiny, base, small, medium, large, "
            "large-v2, large-v3, large-v3-turbo, turbo. "
            "Add .en for English-only models (e.g., base.en). "
            "Default: 'large-v3-turbo'"
        ),
    )

    parser.add_argument(
        "-k",
        "--hotkey",
        type=str,
        default=None,
        help=(
            "Hotkey combination to start/stop recording. "
            "Format: key1+key2 (e.g., 'cmd_l+alt', 'ctrl+alt', 'ctrl+shift'). "
            "Default: 'cmd_l+alt' on macOS, 'ctrl+alt' on Linux."
        ),
    )

    parser.add_argument(
        "--double-cmd",
        action="store_true",
        help=(
            "macOS only: Use double Right-Command key press to toggle recording "
            "(double-press to start, single-press to stop). Ignores --hotkey."
        ),
    )

    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="en",
        help=(
            "Language code(s) for transcription (e.g., 'en', 'es', 'fr'). "
            "Multiple languages can be comma-separated (e.g., 'en,es,fr'). "
            "If multiple languages are specified, you can switch between them in the GUI. "
            "For CLI mode, the first language is used. "
            "Default: 'en' (English). "
            "See https://github.com/openai/whisper for supported languages."
        ),
    )

    parser.add_argument(
        "-t",
        "--max-time",
        type=float,
        default=600.0,
        help="Maximum recording time in seconds. Default: 600.0",
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Force CLI mode (disable macOS menu bar GUI)",
    )

    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available model names and exit",
    )

    args = parser.parse_args()

    # Handle --list-models
    if args.list_models:
        print("Available model names:")
        print("\nWhisper models:")
        print(
            "  tiny, base, small, medium, large, large-v2, large-v3, large-v3-turbo [default], turbo"
        )
        print("  *.en variants: tiny.en, base.en, small.en, medium.en")
        sys.exit(0)

    # Parse language list
    if args.language:
        args.language = [lang.strip() for lang in args.language.split(",")]

    # Validate double-cmd is macOS only
    if args.double_cmd and not platform.is_macos:
        parser.error("--double-cmd is only supported on macOS")

    return args
