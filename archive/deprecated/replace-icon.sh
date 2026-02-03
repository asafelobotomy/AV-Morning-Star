#!/bin/bash
# Script to help replace the icon with the new artwork

echo "==============================================="
echo "  AV Morning Star - Icon Replacement Guide"
echo "==============================================="
echo ""
echo "To use your new beautiful Art Nouveau icon:"
echo ""
echo "1. Save the icon image as: av-morning-star.png"
echo "   Location: $(pwd)/av-morning-star.png"
echo ""
echo "2. The icon will automatically be used in:"
echo "   ✓ App window icon (title bar)"
echo "   ✓ Desktop file (system menu/launcher)"
echo "   ✓ Banner at top of app window (80x80)"
echo "   ✓ Splash screen when app starts (full size)"
echo ""
echo "3. Recommended icon size: 512x512 or 1024x1024 pixels"
echo "   Format: PNG with transparency"
echo ""
echo "Current icon file:"
if [ -f "av-morning-star.png" ]; then
    file av-morning-star.png
    identify av-morning-star.png 2>/dev/null || echo "  (ImageMagick not installed for size info)"
else
    echo "  No icon file found yet"
fi
echo ""
echo "==============================================="
