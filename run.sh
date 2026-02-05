#!/bin/bash
# Launch script for dictation

cd "$(dirname "$0")"

# Find uv executable, handling both regular and sudo contexts
if command -v uv &> /dev/null; then
    # uv is in PATH (normal case)
    UV_CMD="uv"
elif [ -n "$SUDO_USER" ] && [ -x "/home/$SUDO_USER/.local/bin/uv" ]; then
    # Running with sudo, use the original user's uv installation
    UV_CMD="/home/$SUDO_USER/.local/bin/uv"
elif [ -x "$HOME/.local/bin/uv" ]; then
    # Try current user's local bin
    UV_CMD="$HOME/.local/bin/uv"
elif [ -x "/usr/local/bin/uv" ]; then
    # Try system-wide installation
    UV_CMD="/usr/local/bin/uv"
else
    echo "Error: Could not find uv executable" >&2
    echo "Tried: PATH, $HOME/.local/bin/uv, /usr/local/bin/uv" >&2
    exit 1
fi

# Auto-detect platform extras
EXTRAS=""
if [ "$(uname -s)" = "Linux" ]; then
    EXTRAS="--extra linux"
fi

"$UV_CMD" run $EXTRAS dictation "$@"
