"""Command-line argument parsing."""

import argparse
import sys


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
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
        "-l",
        "--language",
        type=str,
        default="en",
        help=(
            "Language code(s) for transcription (e.g., 'en', 'es', 'fr'). "
            "Multiple languages can be comma-separated (e.g., 'en,es,fr'). "
            "The first language is used for transcription. "
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

    return args
