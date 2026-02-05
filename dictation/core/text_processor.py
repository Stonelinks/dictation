"""
Text post-processing utilities for cleaning up transcription output.
"""

import re


def normalize_text(text: str) -> str:
    """
    Normalize transcribed text by fixing spacing and punctuation issues.

    This function:
    - Removes multiple consecutive spaces
    - Fixes spacing around punctuation
    - Strips leading/trailing whitespace
    - Ensures proper spacing after sentence-ending punctuation

    Args:
        text: Raw transcribed text

    Returns:
        Normalized text with proper spacing and punctuation
    """
    if not text:
        return text

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Remove space before punctuation marks
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Ensure single space after punctuation marks (but not at end of string)
    text = re.sub(r"([.,!?;:])(?=[^\s])", r"\1 ", text)

    # Fix multiple spaces that might have been introduced
    text = re.sub(r" +", " ", text)

    # Remove space before closing quotes/parentheses/brackets
    text = re.sub(r'\s+([)\]"\'])', r"\1", text)

    # Remove space after opening quotes/parentheses/brackets
    text = re.sub(r'([(\["\'"])\s+', r"\1", text)

    return text
