#!/usr/bin/env bash
set -e

echo "Building OmniGlyph..."

if [ ! -f "pyproject.toml" ]; then
  echo "Error: Run this script from the project root directory."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Error: .venv not found."
  echo "Run: uv sync"
  exit 1
fi

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Error: Virtual environment not activated."
  echo "Run: source .venv/bin/activate"
  exit 1
fi

if ! command -v nuitka >/dev/null 2>&1; then
  echo "Error: nuitka not found in virtual environment."
  exit 1
fi

echo "Starting Nuitka build..."

nuitka \
    --onefile \
    --enable-plugin=implicit-imports \
    --include-package=gi \
    --include-package=gi.repository \
    --include-data-dir=glyph/db/collections=db/collections \
    --include-package-data=styles \
    --assume-yes-for-downloads \
    --output-dir=out \
    --output-filename=omniglyph.bin \
    glyph/main.py

echo "Build complete."
echo "Binary available at: out/omniglyph.bin"
