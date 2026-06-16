#!/bin/bash
# Quick start script for AV Morning Star

echo "========================================="
echo "  AV Morning Star - Quick Start"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.10 or higher."
    exit 1
fi

# Verify Python version is at least 3.10
PY_OK=$(python3 -c "import sys; print(sys.version_info >= (3, 10))" 2>/dev/null)
if [ "$PY_OK" != "True" ]; then
    echo "Error: Python 3.10 or higher is required."
    echo "Your version: $(python3 --version 2>&1)"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies need to be installed or updated (hash-based, not a static sentinel)
REQ_HASH=$(sha256sum requirements.txt | cut -d' ' -f1)
STORED_HASH=""
if [ -f ".venv/.deps_hash" ]; then
    STORED_HASH=$(cat .venv/.deps_hash)
fi
if [ "$REQ_HASH" != "$STORED_HASH" ]; then
    echo "Installing/updating dependencies..."
    pip install --upgrade pip && pip install -r requirements.txt || {
        echo "Error: dependency installation failed. Not updating hash."
        exit 1
    }
    echo "$REQ_HASH" > .venv/.deps_hash
    echo "✓ Dependencies installed"
    echo ""
else
    echo "✓ Dependencies up to date"
    echo ""
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg is not installed!"
    echo "FFmpeg is required for audio extraction and video merging."
    echo ""
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
    echo "  Arch: sudo pacman -S ffmpeg"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg is installed"
    echo ""
fi

# Check for JavaScript runtime (required for YouTube PO tokens)
echo "Checking for JavaScript runtime (required for YouTube)..."
JS_RUNTIME_FOUND=false

if command -v deno &> /dev/null; then
    echo "✓ Deno is installed (recommended)"
    JS_RUNTIME_FOUND=true
elif command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 22 ]; then
        echo "✓ Node.js $NODE_VERSION is installed (supported)"
        JS_RUNTIME_FOUND=true
    else
        echo "⚠ Node.js version is too old (need v22+ LTS)"
    fi
elif command -v qjs &> /dev/null; then
    echo "✓ QuickJS is installed (basic support)"
    JS_RUNTIME_FOUND=true
elif command -v bun &> /dev/null; then
    echo "✓ Bun is installed (supported)"
    JS_RUNTIME_FOUND=true
fi

if [ "$JS_RUNTIME_FOUND" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠  WARNING: No JavaScript runtime detected!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "YouTube requires a JavaScript runtime to generate"
    echo "Proof of Origin (PO) tokens. Without one, YouTube"
    echo "downloads may fail or have limited quality options."
    echo ""
    echo "Recommended: Install Deno (preferred by yt-dlp)"
    echo ""
    echo "Install via your package manager or see the official guide:"
    echo "  https://docs.deno.com/runtime/getting_started/installation/"
    echo ""
    echo "Common options:"
    echo "  Linux (snap):   snap install deno"
    echo "  Linux (cargo):  cargo install deno"
    echo "  macOS (brew):   brew install deno"
    echo ""
    echo "Alternatives:"
    echo "  - Node.js 22+ LTS: https://nodejs.org/"
    echo "  - QuickJS: sudo apt install quickjs (or build from source)"
    echo ""
    echo "After installing, add Deno to your PATH and restart this script."
    echo ""
    read -p "Would you like to continue without a JS runtime? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Continuing without JS runtime (YouTube may not work)..."
        echo ""
    else
        echo "Please install a JS runtime from the link above and re-run this script."
        exit 0
    fi
fi
echo ""

# Create icon if it doesn't exist
if [ ! -f "av-morning-star.png" ] && [ ! -f "av-morning-star.svg" ]; then
    echo "Creating application icon..."
    python3 scripts/create_icon.py
    echo ""
fi

# Run the application
echo "Starting AV Morning Star..."
echo "========================================="
echo ""
python3 main.py

# Deactivate virtual environment on exit
deactivate
