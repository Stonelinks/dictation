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
        description="Cross-platform multilingual dictation powered by Qwen3-ASR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (platform-aware)
  dictation

  # Use a specific model
  dictation -m Qwen/Qwen3-ASR-1.7B

  # Specify languages
  dictation -l en,es,fr

  # Custom hotkey
  dictation -k ctrl+shift
        """,
    )

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help=(
            "Qwen3-ASR model to use. "
            "Default: Qwen/Qwen3-ASR-0.6B. "
            "Use --list-models for available options."
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
            "Qwen3-ASR supports 30+ languages."
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
        print("Available Qwen3-ASR models:")
        print("  Qwen/Qwen3-ASR-0.6B    [default] (fast, lightweight)")
        print("  Qwen/Qwen3-ASR-1.7B              (better quality)")
        sys.exit(0)

    # Parse language list
    if args.language:
        args.language = [lang.strip() for lang in args.language.split(",")]

    return args
