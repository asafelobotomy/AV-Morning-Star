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
