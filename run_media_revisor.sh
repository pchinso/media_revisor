#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

ensure_first_run_setup() {
    if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
        if "$SCRIPT_DIR/.venv/bin/python" -c "import PySide6" >/dev/null 2>&1; then
            return 0
        fi

        echo "Existing .venv is missing dependencies. Installing..."
        "$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip || exit 1
        "$SCRIPT_DIR/.venv/bin/python" -m pip install -e "$SCRIPT_DIR" || exit 1
        return 0
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "python3 was not found. Install Python 3.11+ and retry." >&2
        exit 1
    fi

    echo "First run setup: creating .venv and installing dependencies..."
    python3 -m venv "$SCRIPT_DIR/.venv" || exit 1
    "$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip || exit 1
    "$SCRIPT_DIR/.venv/bin/python" -m pip install -e "$SCRIPT_DIR" || exit 1
}

ensure_first_run_setup

if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "Python was not found. Create the project environment first." >&2
    exit 1
fi

exec "$PYTHON" -m media_revisor "$@"
