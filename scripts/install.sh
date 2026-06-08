#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://github.com/pshycodr/omniglyph/releases/latest/download"

command -v curl >/dev/null || {
    echo "Error: curl is required"
    exit 1
}

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Downloading OmniGlyph..."

curl -fL \
    "$BASE_URL/omniglyph.bin" \
    -o "$TMPDIR/omniglyph"

curl -fL \
    "$BASE_URL/dev.anishroy.omniglyph.desktop" \
    -o "$TMPDIR/dev.anishroy.omniglyph.desktop"

curl -fL \
    "$BASE_URL/omniglyph.png" \
    -o "$TMPDIR/omniglyph.png"

chmod +x "$TMPDIR/omniglyph"

echo "Installing..."

sudo install -Dm755 \
    "$TMPDIR/omniglyph" \
    /usr/local/bin/omniglyph

sudo install -Dm644 \
    "$TMPDIR/dev.anishroy.omniglyph.desktop" \
    /usr/local/share/applications/dev.anishroy.omniglyph.desktop

sudo install -Dm644 \
    "$TMPDIR/omniglyph.png" \
    /usr/local/share/icons/hicolor/256x256/apps/dev.anishroy.omniglyph.png

sudo gtk-update-icon-cache \
    -f /usr/local/share/icons/hicolor || true

sudo update-desktop-database \
    /usr/local/share/applications || true

echo "Installation complete."
echo "Launch OmniGlyph from your application menu or run:"
echo "  omniglyph"
