"""Quick test for text normalization."""

from whisper_dictation.core.text_processor import normalize_text

# Test with the user's example
test_text = "Mary had a little lamb whose fleece was white as snow. I often saw Mary but I never  saw the little lamb. I'm wondering if there will be spaces in between the  sentences or not? I sure hope they will. Let's see if a question gets recognized."

print("Original text:")
print(repr(test_text))
print("\nNormalized text:")
normalized = normalize_text(test_text)
print(repr(normalized))
print("\nReadable output:")
print(normalized)

# Additional test cases
print("\n" + "="*60)
print("Additional test cases:")
print("="*60)

test_cases = [
    "  Leading spaces",
    "Trailing spaces  ",
    "Multiple   spaces   between   words",
    "Space before punctuation .",
    "No space after.Period",
    "Hello , world !",
    "Text with ( parentheses ) and [ brackets ]",
    'Text with " quotes "',
    "Multiple  spaces  and  bad punctuation .",
]

for test in test_cases:
    print(f"\nOriginal: {repr(test)}")
    print(f"Normalized: {repr(normalize_text(test))}")
