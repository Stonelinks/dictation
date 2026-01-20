# Whisper Dictation Test Suite

Comprehensive pytest-based test suite for the whisper_dictation project.

## Test Organization

```
tests/
├── conftest.py                      # Shared fixtures and mocks
├── unit/                            # Unit tests (fast, isolated)
│   ├── core/
│   │   ├── test_text_processor.py   # Text normalization tests (25 tests)
│   │   ├── test_recorder.py         # Audio recording tests (19 tests)
│   │   └── test_transcriber.py      # Whisper transcription tests (18 tests)
│   ├── platform/
│   │   ├── test_detection.py        # Platform detection tests (12 tests)
│   │   ├── keyboard/
│   │   │   ├── test_pynput_listener.py  # Keyboard listener tests (19 tests)
│   │   │   └── test_evdev_listener.py   # Linux evdev tests (16 tests)
│   │   └── text_injection/
│   │       ├── test_pynput_injector.py  # Text injection tests (15 tests)
│   │       └── test_ydotool_injector.py # Wayland ydotool tests (8 tests)
│   └── test_config.py               # Configuration tests (17 tests)
└── integration/
    └── test_dictation_app.py        # Integration tests (16 tests)
```

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=whisper_dictation --cov-report=term-missing
```

### Run specific test categories
```bash
# Unit tests only
uv run pytest -m unit

# Integration tests
uv run pytest -m integration

# Platform-specific tests
uv run pytest -m macos
uv run pytest -m linux
uv run pytest -m wayland
```

### Run specific test files
```bash
# Test text processor
uv run pytest tests/unit/core/test_text_processor.py

# Test recorder
uv run pytest tests/unit/core/test_recorder.py

# Test configuration
uv run pytest tests/unit/test_config.py
```

## Test Statistics

- **Total Tests**: ~195 tests
- **Unit Tests**: ~165 tests
- **Integration Tests**: ~16 tests
- **Platform-Specific Tests**: ~30 tests (Linux/Wayland specific)

## Coverage Goals

| Module | Target Coverage | Description |
|--------|-----------------|-------------|
| Core modules (text_processor, recorder, transcriber) | 95%+ | Critical business logic |
| Configuration & detection | 90%+ | Platform setup and config |
| Platform-specific code | 80%+ | Keyboard listeners, text injection |
| Overall (core modules only) | 75%+ | Excluding UI and CLI |

## Fixtures

The `conftest.py` file provides comprehensive fixtures for:

### Platform Mocks
- `mock_macos_platform` - macOS platform info
- `mock_macos_apple_silicon_platform` - Apple Silicon Mac
- `mock_linux_x11_platform` - Linux X11 session
- `mock_linux_wayland_platform` - Linux Wayland session

### Configuration Fixtures
- `default_macos_config` - Default macOS configuration
- `default_linux_config` - Default Linux configuration

### Audio Data Fixtures
- `sample_audio` - 1 second synthetic audio
- `empty_audio` - Empty audio array
- `short_audio` - 0.1 second audio

### Mock External Dependencies
- `mock_pyaudio` - Mock PyAudio for recorder tests
- `mock_whisper_model` - Mock faster-whisper for transcription
- `mock_pynput_keyboard` - Mock keyboard listener
- `mock_pynput_controller` - Mock text injection controller
- `mock_evdev` - Mock evdev for Linux keyboard
- `mock_subprocess` - Mock subprocess for ydotool

## Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.macos` - macOS-specific tests
- `@pytest.mark.linux` - Linux-specific tests
- `@pytest.mark.wayland` - Wayland-specific tests

## Key Test Modules

### test_text_processor.py (25 tests)
Tests for the `normalize_text()` function covering:
- Empty strings and whitespace handling
- Space collapsing and punctuation spacing
- Quotes, parentheses, and brackets
- Complex sentence normalization
- Parametrized test cases

### test_recorder.py (19 tests)
Tests for the `Recorder` class covering:
- Initialization with custom/default parameters
- Start/stop lifecycle
- State tracking (is_recording)
- Max duration enforcement
- Audio conversion (int16 → float32)
- Error handling and thread safety

### test_transcriber.py (18 tests)
Tests for `StandardWhisperTranscriber` covering:
- Initialization with different models
- Transcription with/without language parameter
- Segment joining and whitespace handling
- Empty audio handling
- Model name retrieval

### test_detection.py (12 tests)
Tests for platform detection covering:
- macOS detection (Intel and Apple Silicon)
- Linux session type detection (X11 vs Wayland)
- Environment variable fallbacks
- Caching behavior

### test_config.py (17 tests)
Tests for configuration management covering:
- Default configuration for each platform
- Custom parameters (model, hotkey, languages)
- Validation rules (GUI mode, English-only models)
- Dependency warnings (ydotool, evdev)

### test_pynput_listener.py (19 tests)
Tests for keyboard listeners covering:
- Listener lifecycle (start/stop/is_running)
- Key combination parsing and detection
- Double-press detection for double-command mode
- Callback triggering
- State tracking

### test_pynput_injector.py (15 tests)
Tests for text injection covering:
- Character-by-character typing
- Delay between characters
- Empty string handling
- Special characters and punctuation
- Error handling

### test_ydotool_injector.py (8 tests)
Tests for Wayland text injection covering:
- ydotool binary detection
- Subprocess invocation
- Error handling
- Empty text handling

### test_dictation_app.py (16 tests)
Integration tests covering:
- Component initialization
- Recording workflow (start → record → transcribe → inject)
- Error handling during transcription
- Factory functions (create_transcriber, create_text_injector, etc.)
- Multi-language support

## Mocking Strategy

All external dependencies are mocked to ensure:
- **Fast execution** - No real audio hardware or Whisper models needed
- **Reliability** - Tests don't depend on external services
- **Cross-platform** - Can test all platforms on any machine
- **Isolation** - Each test is independent

Mocked dependencies:
- PyAudio (audio recording)
- faster-whisper (transcription)
- pynput (keyboard and text injection)
- evdev (Linux keyboard)
- subprocess (ydotool calls)
- Platform detection (platform.system, platform.machine)

## Notes

### Known Test Limitations

1. **evdev tests on macOS**: The evdev-specific tests may show errors on macOS since evdev is a Linux-only library. These tests are marked with `@pytest.mark.linux` and can be skipped on non-Linux platforms.

2. **GUI tests excluded**: UI modules (cli_ui, macos_menubar) are not tested in this suite as they require more complex integration testing.

3. **Time-based tests**: Some tests involving time.time() mocking (like double-command detection) may be flaky depending on execution speed.

### Migration from Manual Testing

The original `test_text_processor.py` manual test script has been migrated to proper pytest format in `tests/unit/core/test_text_processor.py` with:
- Parametrized test cases
- Clear assertions
- Better organization
- Coverage tracking

## Contributing

When adding new tests:
1. Use appropriate fixtures from `conftest.py`
2. Mark tests with relevant markers (`@pytest.mark.unit`, etc.)
3. Mock all external dependencies
4. Keep tests fast and isolated
5. Aim for high coverage (>90%) on core modules
6. Add docstrings explaining what each test verifies
