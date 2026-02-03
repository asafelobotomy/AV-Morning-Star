#!/bin/bash
# Quick start script for AV Morning Star

echo "========================================="
echo "  AV Morning Star - Quick Start"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher."
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

# Check if dependencies are installed
if [ ! -f ".venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .venv/.deps_installed
    echo "✓ Dependencies installed"
    echo ""
else
    echo "✓ Dependencies already installed"
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
    if [ "$NODE_VERSION" -ge 25 ]; then
        echo "✓ Node.js $NODE_VERSION is installed (supported)"
        JS_RUNTIME_FOUND=true
    else
        echo "⚠ Node.js version is too old (need v25+)"
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
    echo "Quick install:"
    echo "  curl -fsSL https://deno.land/install.sh | sh"
    echo ""
    echo "Then add to your PATH:"
    echo "  echo 'export DENO_INSTALL=\"\$HOME/.deno\"' >> ~/.bashrc"
    echo "  echo 'export PATH=\"\$DENO_INSTALL/bin:\$PATH\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
    echo "Alternatives:"
    echo "  - Node.js 25+: https://nodejs.org/"
    echo "  - QuickJS: sudo apt install quickjs (or build from source)"
    echo "  - Bun: curl -fsSL https://bun.sh/install | bash"
    echo ""
    echo "See YOUTUBE_FIX_IMPLEMENTATION.md for more details."
    echo ""
    read -p "Would you like to install Deno now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Deno..."
        curl -fsSL https://deno.land/install.sh | sh
        export DENO_INSTALL="$HOME/.deno"
        export PATH="$DENO_INSTALL/bin:$PATH"
        echo ""
        echo "✓ Deno installed successfully!"
        echo "Note: Add Deno to PATH in your shell config for permanent use."
        echo ""
    else
        echo "Continuing without JS runtime (YouTube may not work)..."
        echo ""
    fi
fi
echo ""

# Create icon if it doesn't exist
if [ ! -f "av-morning-star.png" ] && [ ! -f "av-morning-star.svg" ]; then
    echo "Creating application icon..."
    python3 create_icon.py
    echo ""
fi

# Run the application
echo "Starting AV Morning Star..."
echo "========================================="
echo ""
python3 main.py

# Deactivate virtual environment on exit
deactivate
