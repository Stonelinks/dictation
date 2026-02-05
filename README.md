# Whisper Dictation

**Hands-free dictation that just works.** Press a hotkey, speak naturally, and watch your words appear in any application—no cloud, no latency, complete privacy.

Powered by OpenAI's Whisper AI model running locally on your machine.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: macOS | Linux](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/whisper-dictation)

---

## Features

- **100+ Languages** - Supports every language Whisper knows (English, Spanish, French, Chinese, Japanese, and [many more](https://github.com/openai/whisper#available-models-and-languages))
- **Cross-Platform** - macOS (Apple Silicon optimized), Linux (X11 & Wayland)
- **Universal Input** - Works in any application: email, docs, chat, IDE, browser
- **100% Private** - All processing happens locally, no internet required
- **Real-Time** - Fast transcription with optimized models
- **Smart Formatting** - Automatic punctuation, capitalization, and spacing
- **Customizable Hotkeys** - Configure your own key combinations

---

## Quick Start

### macOS

```bash
# Install dependencies
brew install portaudio

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd whisper-dictation
uv sync

# Run!
./run.sh
```

**Press `Cmd+Option` to start recording, speak, then press again to transcribe.**

### Linux

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install portaudio19-dev

# For Wayland users, also install ydotool
sudo apt-get install ydotool
sudo systemctl enable --now ydotool

# Add yourself to input group for keyboard access
sudo usermod -a -G input $USER
# Log out and back in for changes to take effect

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd whisper-dictation
uv sync --extra linux

# Run!
./run.sh
```

**Press `Ctrl+Alt` to start recording, speak, then press again to transcribe.**

---

## Installation

### Prerequisites

| Requirement | macOS | Linux (X11) | Linux (Wayland) |
|------------|-------|-------------|-----------------|
| Python 3.10-3.12 | Yes | Yes | Yes |
| [uv](https://docs.astral.sh/uv/) package manager | Yes | Yes | Yes |
| PortAudio | Yes | Yes | Yes |
| Microphone permission | Yes | - | - |
| Accessibility permission | Yes | - | - |
| `/dev/input/event*` access | - | Yes | Yes |
| [ydotool](https://github.com/ReimuNotMoe/ydotool) | - | - | Yes |

### Step-by-Step Installation

<details>
<summary><b>macOS</b></summary>

1. **Install PortAudio**
   ```bash
   brew install portaudio
   ```

2. **Install uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whisper-dictation
   ```

4. **Install Python dependencies**
   ```bash
   uv sync
   ```

5. **Grant permissions when prompted**
   - System Settings → Privacy & Security → Microphone → Enable
   - System Settings → Privacy & Security → Accessibility → Enable your terminal

6. **Run it!**
   ```bash
   ./run.sh
   # or
   uv run whisper-dictation
   ```

</details>

<details>
<summary><b>Linux (X11)</b></summary>

1. **Install system dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install portaudio19-dev
   ```

2. **Grant keyboard access**
   ```bash
   sudo usermod -a -G input $USER
   ```
   **Important:** Log out and back in for this to take effect

3. **Install uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whisper-dictation
   ```

5. **Install Python dependencies**
   ```bash
   uv sync --extra linux
   ```

6. **Run it!**
   ```bash
   ./run.sh
   # or
   uv run whisper-dictation
   ```

</details>

<details>
<summary><b>Linux (Wayland)</b></summary>

1. **Install system dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install portaudio19-dev ydotool
   ```

2. **Enable ydotool service**
   ```bash
   sudo systemctl enable ydotool
   sudo systemctl start ydotool

   # Verify it's running
   systemctl status ydotool
   ```

3. **Grant keyboard access**
   ```bash
   sudo usermod -a -G input $USER
   ```
   **Important:** Log out and back in for this to take effect

4. **Install uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

5. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whisper-dictation
   ```

6. **Install Python dependencies**
   ```bash
   uv sync --extra linux
   ```

7. **Run it!**
   ```bash
   ./run.sh
   # or
   uv run whisper-dictation
   ```

</details>

---

## Usage Guide

### Basic Usage

```bash
./run.sh
# or
uv run whisper-dictation
```

- **macOS**: Uses `Cmd+Option` hotkey
- **Linux**: Uses `Ctrl+Alt` hotkey

### Command-Line Options

```bash
whisper-dictation [OPTIONS]
```

| Option | Description | Example |
|--------|-------------|---------|
| `-m, --model` | Whisper model to use | `-m large-v3` |
| `-l, --language` | Language(s) for transcription | `-l en,es,fr` |
| `-k, --hotkey` | Custom hotkey combination | `-k ctrl+shift` |
| `-t, --max-time` | Max recording time (seconds) | `-t 60` |
| `--list-models` | Show available models | `--list-models` |

**Examples:**

```bash
# English transcription with large model
uv run whisper-dictation -m large-v3 -l en

# Multilingual support
uv run whisper-dictation -l en,es,fr,de

# Short recordings with custom hotkey
uv run whisper-dictation -t 30 -k cmd_l+shift

# Fast model for quick notes
uv run whisper-dictation -m turbo -l en
```

---

## Configuration

### Choosing a Model

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `tiny` | ~75MB | Very Fast | Fair | Quick notes, testing |
| `base` | ~150MB | Fast | Good | Casual dictation |
| `small` | ~500MB | Medium | Very Good | General use |
| `medium` | ~1.5GB | Slow | Excellent | Professional work |
| `large-v3` | ~3GB | Slowest | Best | Maximum accuracy |
| `large-v3-turbo` | ~1.6GB | Medium | Excellent | **Recommended** (default) |
| `turbo` | ~800MB | Fast | Very Good | Speed + quality balance |

**Pro tip:** Add `.en` suffix for English-only models (e.g., `base.en`, `small.en`) for better English performance.

### Language Support

Whisper supports 100+ languages. Specify with `-l`:

```bash
# Single language
whisper-dictation -l en

# Multiple languages (first is used for transcription)
whisper-dictation -l en,es,fr
```

**Popular Language Codes:**
`en` (English) • `es` (Spanish) • `fr` (French) • `de` (German) • `it` (Italian) • `pt` (Portuguese) • `ru` (Russian) • `ja` (Japanese) • `zh` (Chinese) • `ko` (Korean) • `ar` (Arabic) • `hi` (Hindi)

[See full list →](https://github.com/openai/whisper#available-models-and-languages)

### Hotkey Customization

```bash
# macOS examples
whisper-dictation -k cmd_l+alt           # Left Command + Option (default)
whisper-dictation -k cmd_l+shift         # Left Command + Shift

# Linux examples
whisper-dictation -k ctrl+alt            # Ctrl + Alt (default)
whisper-dictation -k ctrl+shift          # Ctrl + Shift
whisper-dictation -k super+space         # Super/Windows + Space
```

**Key names:** `ctrl`, `alt`, `shift`, `cmd_l`, `cmd_r`, `super`, `space`, letters, numbers

---

## Platform-Specific Notes

<details>
<summary><b>macOS - Permissions</b></summary>

### Required Permissions

Both permissions are required. The app will prompt you on first run.

1. **Microphone Access**
   - System Settings → Privacy & Security → Microphone
   - Enable your terminal app (Terminal, iTerm2, etc.)

2. **Accessibility Access** (for keyboard control)
   - System Settings → Privacy & Security → Accessibility
   - Enable your terminal app

</details>

<details>
<summary><b>Linux (X11) - Keyboard Access</b></summary>

### Keyboard Input Access

X11 requires read access to `/dev/input/event*` for global hotkeys.

**Check current access:**
```bash
ls -l /dev/input/event*
```

**Grant access (required):**
```bash
sudo usermod -a -G input $USER
```

**Important:** Log out and back in for changes to take effect.

**Verify it worked:**
```bash
groups | grep input  # Should show "input" in the list
```

</details>

<details>
<summary><b>Linux (Wayland) - ydotool Setup</b></summary>

### Why ydotool?

Wayland's security model prevents direct keyboard simulation. ydotool provides a secure way to inject text.

### Installation & Setup

1. **Install ydotool:**
   ```bash
   sudo apt-get install ydotool
   ```

2. **Enable the service:**
   ```bash
   sudo systemctl enable ydotool
   sudo systemctl start ydotool
   ```

3. **Verify it's running:**
   ```bash
   systemctl status ydotool
   # Should show "active (running)"
   ```

4. **Grant keyboard access:**
   ```bash
   sudo usermod -a -G input $USER
   # Log out and back in
   ```

### Testing ydotool

```bash
# Test text injection
ydotool type "Hello, world!"
```

If this doesn't work, ydotool service isn't running properly.

</details>

---

## Troubleshooting

<details>
<summary><b>"No keyboard devices found" (Linux)</b></summary>

**Problem:** You don't have permission to read keyboard input devices.

**Solution:**
```bash
# Add yourself to the input group
sudo usermod -a -G input $USER

# Log out and back in (required!)
# Then verify:
groups | grep input
```

</details>

<details>
<summary><b>"ydotool is not installed" (Linux Wayland)</b></summary>

**Problem:** ydotool is required for text injection on Wayland but isn't installed.

**Solution:**
```bash
# Install ydotool
sudo apt-get install ydotool

# Enable and start the service
sudo systemctl enable ydotool
sudo systemctl start ydotool

# Verify it's running
systemctl status ydotool
```

</details>

<details>
<summary><b>"OSError: [Errno -9996] Invalid input device"</b></summary>

**Problem:** PortAudio cannot access your microphone.

**Solutions by platform:**

**macOS:**
- Grant microphone permission: System Settings → Privacy & Security → Microphone
- Enable your terminal app (Terminal, iTerm2, etc.)
- Restart the application

**Linux:**
```bash
# List available audio devices
arecord -l

# Verify PortAudio is installed
apt list --installed | grep portaudio

# If not installed
sudo apt-get install portaudio19-dev
```

</details>

<details>
<summary><b>Text doesn't appear after transcription</b></summary>

**Possible causes & solutions:**

1. **Wrong window focus**
   - Click into the target application before stopping recording
   - Some apps require focus to accept input

2. **Missing permissions (macOS)**
   - Grant Accessibility permission: System Settings → Privacy & Security → Accessibility
   - Add and enable your terminal app

3. **ydotool not running (Wayland)**
   ```bash
   systemctl status ydotool  # Should show "active (running)"
   sudo systemctl start ydotool  # If not running
   ```

4. **Application doesn't accept programmatic input**
   - Some apps (especially games, some security software) block programmatic keyboard input
   - Test by typing manually first

</details>

<details>
<summary><b>Poor transcription quality</b></summary>

**Quick fixes:**

1. **Use a larger model**
   ```bash
   whisper-dictation -m large-v3
   ```

2. **Specify your language**
   ```bash
   whisper-dictation -l en  # or your language code
   ```

3. **Environmental improvements:**
   - Speak clearly and at normal pace
   - Minimize background noise
   - Check microphone isn't too far from your mouth
   - Increase microphone input volume in system settings

</details>

<details>
<summary><b>How do I change the recording hotkey?</b></summary>

Use the `-k` or `--hotkey` flag:

```bash
# macOS examples
whisper-dictation -k cmd_l+shift
whisper-dictation -k cmd_r+alt

# Linux examples
whisper-dictation -k ctrl+shift
whisper-dictation -k super+space
```

**Available key names:**
- Modifiers: `ctrl`, `alt`, `shift`, `cmd_l`, `cmd_r`, `super`
- Special: `space`, `tab`, `enter`, `esc`
- Letters: `a`-`z`
- Numbers: `0`-`9`

</details>

<details>
<summary><b>Which model should I use?</b></summary>

**Quick recommendations:**

- **Starting out?** Use the default (`large-v3-turbo`) - good balance
- **Fast computer?** Try `large-v3` for maximum accuracy
- **Older hardware?** Try `small` or `base`
- **English only?** Use `.en` models (e.g., `base.en`, `small.en`)
- **Testing?** Use `tiny` for quick iteration

**Rule of thumb:** Start with default, only change if you have issues.

</details>

<details>
<summary><b>Can I use this offline?</b></summary>

**Yes!** Everything runs locally:
- First run downloads the Whisper model (~1.6GB for default)
- After that, no internet required
- All processing happens on your computer
- Complete privacy - nothing sent to cloud

</details>

<details>
<summary><b>Does it work on Apple Silicon (M1/M2/M3)?</b></summary>

**Yes!** Optimized for Apple Silicon:
- Automatically uses Metal acceleration
- Faster than Intel Macs
- Lower power consumption
- Same installation process

</details>

---

## Development

### Setup Development Environment

```bash
# Install all dependencies including dev tools
uv sync --all-extras
```

### Running & Testing

```bash
# Run directly from source
uv run python -m whisper_dictation

# Run with specific options
uv run python -m whisper_dictation -m base.en -l en

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=whisper_dictation --cov-report=html
```

### Code Quality

```bash
# Format code
./format.sh
# or manually:
uv run ruff format .

# Lint code
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Project Structure

```
whisper-dictation/
├── whisper_dictation/          # Main package
│   ├── __main__.py            # Entry point
│   ├── cli.py                 # Argument parsing
│   ├── config.py              # Configuration
│   ├── core/                  # Core functionality
│   │   ├── recorder.py        # Audio recording
│   │   ├── transcriber.py     # Whisper integration
│   │   └── text_processor.py  # Text normalization
│   ├── platform/              # Platform-specific code
│   │   ├── detection.py       # Platform detection
│   │   ├── keyboard/          # Hotkey listeners
│   │   │   ├── base.py
│   │   │   ├── evdev_listener.py    # Linux
│   │   │   └── pynput_listener.py   # macOS/X11
│   │   └── text_injection/    # Text automation
│   │       ├── base.py
│   │       ├── pynput_injector.py   # macOS/X11
│   │       └── ydotool_injector.py  # Wayland
│   └── ui/                    # User interface
│       ├── base.py
│       └── cli_ui.py          # CLI interface
├── tests/                     # Test suite
├── pyproject.toml            # Project config
├── format.sh                 # Formatting script
└── README.md                 # This file
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Credits

### Core Technologies

| Technology | Purpose | License |
|------------|---------|---------|
| [OpenAI Whisper](https://github.com/openai/whisper) | Speech recognition model | MIT |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Optimized Whisper inference | MIT |
| [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) | Audio recording | MIT |
| [pynput](https://github.com/moses-palmer/pynput) | Keyboard/mouse control | LGPLv3 |
| [evdev](https://python-evdev.readthedocs.io/) | Linux input device access | BSD |
| [ydotool](https://github.com/ReimuNotMoe/ydotool) | Wayland automation | MIT |

---

**Made with care for the open-source community**
