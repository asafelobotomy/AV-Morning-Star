#!/bin/bash
# Simple test script to verify the application works

echo "Testing AV Morning Star components..."
echo ""

# Test 1: Check Python imports
echo "Test 1: Checking Python imports..."
python3 << 'PYEOF'
try:
    import sys
    print(f"  Python version: {sys.version.split()[0]}")
    
    import PyQt5
    print("  ✓ PyQt5 imported successfully")
    
    import yt_dlp
    print("  ✓ yt-dlp imported successfully")
    
    import requests
    print("  ✓ requests imported successfully")
    
    import bs4
    print("  ✓ beautifulsoup4 imported successfully")
    
    print("\nAll imports successful!")
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    print("\nPlease run: pip install -r requirements.txt")
    sys.exit(1)
PYEOF

echo ""

# Test 2: Check FFmpeg
echo "Test 2: Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version | head -n1)
    echo "  ✓ FFmpeg found: $ffmpeg_version"
else
    echo "  ✗ FFmpeg not found (required for audio extraction)"
fi

echo ""

# Test 3: Check yt-dlp functionality
echo "Test 3: Testing yt-dlp (this may take a moment)..."
python3 << 'PYEOF'
import yt_dlp

try:
    # Test with a short YouTube video (testing extraction only, not downloading)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Use a known stable test URL
        info = ydl.extract_info('https://www.youtube.com/watch?v=jNQXAC9IVRw', download=False)
        if info:
            print(f"  ✓ yt-dlp working correctly")
            print(f"  ✓ Successfully extracted video metadata")
        else:
            print("  ⚠ Could not extract video info (may be network issue)")
except Exception as e:
    print(f"  ⚠ yt-dlp test failed: {e}")
    print("  This might be due to network issues or site restrictions")
PYEOF

echo ""
echo "========================================="
echo "Test complete!"
echo ""
echo "If all tests passed, you can:"
echo "  1. Run the app: ./start.sh"
echo "  2. Build AppImage: ./build-appimage.sh"
echo "========================================="
