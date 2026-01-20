# Whisper Dictation

Cross-platform multilingual dictation using Whisper (via faster-whisper). Press a hotkey to start/stop recording, and the transcribed text is automatically typed into your active window.

## Features

- **Cross-Platform**: Works on macOS Apple Silicon and Linux (X11 & Wayland)
- **Multilingual**: Supports all languages supported by OpenAI Whisper
- **Multiple Interfaces**: macOS menu bar GUI or CLI
- **Platform-Aware**: Automatically detects and adapts to your system
- **Flexible Hotkeys**: Customizable keyboard shortcuts or double-Command on macOS

## Requirements

### All Platforms
- Python 3.10, 3.11, or 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- PortAudio (for PyAudio)

### Platform-Specific

#### macOS
- Microphone permission
- Accessibility permission (for keyboard control)

#### Linux (X11)
- Read access to `/dev/input/event*` (keyboard input)
- PyAudio dependencies

#### Linux (Wayland)
- Read access to `/dev/input/event*` (keyboard input)
- [ydotool](https://github.com/ReimuNotMoe/ydotool) for text injection
- PyAudio dependencies

## Installation

### 1. Install System Dependencies

#### macOS
```bash
# Install PortAudio
brew install portaudio

# Grant microphone and accessibility permissions when prompted
```

#### Ubuntu/Debian (X11)
```bash
# Install PortAudio
sudo apt-get install portaudio19-dev

# Add user to input group for keyboard access
sudo usermod -a -G input $USER
# Log out and back in for group changes to take effect
```

#### Ubuntu/Debian (Wayland)
```bash
# Install PortAudio and ydotool
sudo apt-get install portaudio19-dev ydotool

# Enable and start ydotool service
sudo systemctl enable ydotool
sudo systemctl start ydotool

# Add user to input group for keyboard access
sudo usermod -a -G input $USER
# Log out and back in for group changes to take effect
```

### 2. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Clone and Install

```bash
cd unified-dictation

# macOS (Whisper + GUI)
uv sync --extra macos

# Linux (Whisper + CLI)
uv sync --extra linux
```

## Usage

### Quick Start

```bash
# Run with default settings
./run.sh
# or
uv run whisper-dictation
```

On **macOS**, this starts the menu bar app. Press `Cmd+Option` to start/stop recording.

On **Linux**, this starts CLI mode. Press `Ctrl+Alt` to start/stop recording.

### Command-Line Options

```bash
# Use a specific model
uv run whisper-dictation -m large-v3

# Specify languages
uv run whisper-dictation -l en,es,fr

# Custom hotkey
uv run whisper-dictation -k ctrl+shift

# Use double Right-Command on macOS
uv run whisper-dictation --double-cmd

# Force CLI mode on macOS
uv run whisper-dictation --no-gui

# Set maximum recording time
uv run whisper-dictation -t 60

# List available models
uv run whisper-dictation --list-models
```

### Model Selection

- `tiny` - Fastest, lowest quality (~75MB)
- `base` - Good balance (~150MB)
- `small` - Better quality (~500MB)
- `medium` - High quality (~1.5GB)
- `large` - Best quality (~3GB)
- `large-v2` - Improved large model
- `large-v3` - Latest large model **[default]**
- `turbo` - Fast high-quality model

Add `.en` for English-only models (e.g., `tiny.en`, `base.en`) for better English performance

### Language Support

Specify language codes with `-l`:

```bash
# Single language
uv run whisper-dictation -l en

# Multiple languages (GUI mode allows switching)
uv run whisper-dictation -l en,es,fr,de

# Common language codes:
# en (English), es (Spanish), fr (French), de (German),
# it (Italian), pt (Portuguese), ru (Russian), ja (Japanese),
# zh (Chinese), ko (Korean), ar (Arabic), hi (Hindi)
```

See [Whisper documentation](https://github.com/openai/whisper) for the full list.

### macOS Menu Bar GUI

When running with GUI mode on macOS:
1. A menu bar icon (⏯) appears
2. Click "Start Recording" or use the hotkey
3. Speak into your microphone
4. Click "Stop Recording" or use the hotkey again
5. Text is automatically typed into the active window

**Features:**
- Recording timer in menu bar (🔴)
- Language switching (if multiple languages specified)
- Keyboard shortcut support

## Platform-Specific Notes

### macOS

**Permissions Required:**
1. **Microphone**: System Settings → Privacy & Security → Microphone
2. **Accessibility**: System Settings → Privacy & Security → Accessibility

**Hotkey Options:**
- Default: `Cmd+Option` (cmd_l+alt)
- Double Right-Command: Use `--double-cmd` flag
- Custom: Use `-k` flag (e.g., `-k cmd_l+shift`)

**GUI Menu Bar:**
- Shows recording timer
- Language switching (if multiple languages configured)
- Easy start/stop controls

### Linux (X11)

**Keyboard Access:**
```bash
# Check if you have access to /dev/input/event*
ls -l /dev/input/event*

# If not, add yourself to the input group
sudo usermod -a -G input $USER
# Log out and back in
```

**Hotkey:** Default is `Ctrl+Alt`. Customize with `-k ctrl+shift`.

### Linux (Wayland)

**ydotool Setup:**
```bash
# Install ydotool
sudo apt-get install ydotool

# Enable service
sudo systemctl enable ydotool
sudo systemctl start ydotool

# Check status
systemctl status ydotool
```

**Note:** Wayland's security model requires ydotool for text injection. The pynput method used on X11 doesn't work on Wayland.

## Troubleshooting

### "No keyboard devices found"
**Linux:** You need read access to `/dev/input/event*`. Add yourself to the `input` group:
```bash
sudo usermod -a -G input $USER
```
Log out and back in.

### "ydotool is not installed"
**Linux (Wayland):** Install and start ydotool:
```bash
sudo apt-get install ydotool
sudo systemctl enable --now ydotool
```


### "OSError: [Errno -9996] Invalid input device"
**All platforms:** PortAudio can't access your microphone.
- **macOS:** Grant microphone permission in System Settings
- **Linux:** Check `arecord -l` to list devices, ensure PortAudio is installed

### Text doesn't appear
1. **Check active window**: Click into the target window before recording
2. **macOS**: Grant Accessibility permission
3. **Wayland**: Ensure ydotool service is running
4. **All**: Try typing manually in the target app first to ensure it accepts input

### Poor transcription quality
1. Use a larger model: `-m large-v3`
2. Specify language: `-l en` (or your language)
3. Speak clearly and minimize background noise
4. Check microphone input volume in system settings

## Architecture

The project uses a factory pattern with platform detection:

```
Platform Detection → Factory Functions → Components
                  ↓
        ┌─────────┴──────────┐
        │                    │
    Whisper              evdev/pynput
    Transcriber          Listener
                    │
              ydotool/pynput
              Text Injector
```

**Key Modules:**
- `platform/detection.py` - Platform detection
- `core/transcriber.py` - Whisper transcription
- `core/recorder.py` - Audio recording
- `platform/keyboard/` - Keyboard listeners
- `platform/text_injection/` - Text injectors
- `ui/` - CLI and GUI interfaces

## Development

```bash
# Install in development mode
uv sync --all-extras

# Run directly
uv run python -m whisper_dictation

# Run tests (if you add them)
uv run pytest
```

## License

MIT License - See LICENSE file for details.

## Credits

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Efficient Whisper implementation
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard/mouse control
- [evdev](https://python-evdev.readthedocs.io/) - Linux input device access
- [ydotool](https://github.com/ReimuNotMoe/ydotool) - Wayland automation
- [rumps](https://github.com/jaredks/rumps) - macOS menu bar apps
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio recording

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

This project unifies and improves upon two earlier implementations for seamless cross-platform dictation.
