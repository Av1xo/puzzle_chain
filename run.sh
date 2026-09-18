#!/usr/bin/env bash

set -e

VENV_DIR=".venv"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found! Please install Python."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip > /dev/null
pip install -r requirements.txt

python cli.py