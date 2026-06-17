#!/bin/bash
# Smoke test: verify imports and run the unit test suite.

set -e

echo "Testing AV Morning Star..."
echo ""

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Checking imports..."
python3 << 'PYEOF'
import sys
print(f"  Python: {sys.version.split()[0]}")
import PyQt5  # noqa: F401
print("  ✓ PyQt5")
import yt_dlp  # noqa: F401
print("  ✓ yt-dlp")
PYEOF

echo ""
echo "Checking file size limits..."
python3 scripts/check_loc.py --warn 200 --fail 400

echo ""
echo "Running unit tests..."
python3 -m unittest discover -s tests -p "test_*.py" -v

echo ""
echo "All checks passed."
