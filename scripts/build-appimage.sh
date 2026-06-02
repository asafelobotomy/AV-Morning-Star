#!/bin/bash
# Build script for creating AV Morning Star AppImage

set -e

APP_NAME="AV-Morning-Star"
APP_VERSION=$(cat VERSION 2>/dev/null || echo "")
BUILD_DIR="build"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"

# Validate that VERSION file and constants.py are in sync
if [ -z "$APP_VERSION" ]; then
    echo "ERROR: Could not read version from VERSION file"
    exit 1
fi
CONSTANTS_VERSION=$(python3 -c \
    "import re; m=re.search(r'APP_VERSION = \"([^\"]+)\"', open('constants.py').read()); print(m.group(1) if m else '')" \
    2>/dev/null || echo "")
if [ -z "$CONSTANTS_VERSION" ]; then
    echo "ERROR: Could not read APP_VERSION from constants.py"
    exit 1
fi
if [ "$APP_VERSION" != "$CONSTANTS_VERSION" ]; then
    echo "ERROR: Version mismatch — VERSION file has '${APP_VERSION}' but constants.py has '${CONSTANTS_VERSION}'"
    echo "Update both files to the same version before building."
    exit 1
fi
echo "Version check passed: ${APP_VERSION}"

echo "Building AV Morning Star AppImage..."

# Clean previous build
rm -rf "${BUILD_DIR}"
mkdir -p "${APPDIR}"

# Create AppDir structure
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/metainfo"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Install Python dependencies in a virtual environment
echo "Setting up Python environment..."
python3 -m venv "${BUILD_DIR}/.venv"
source "${BUILD_DIR}/.venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Create standalone executable with PyInstaller
echo "Creating standalone executable..."
pyinstaller --onefile \
    --windowed \
    --name "${APP_NAME}" \
    --add-data "packaging/com.github.asafelobotomy.avmorningstar.desktop:." \
    --hidden-import=PyQt5 \
    --hidden-import=yt_dlp \
    --collect-all yt_dlp \
    main.py

# Copy executable to AppDir
cp "dist/${APP_NAME}" "${APPDIR}/usr/bin/"

# Create AppRun script with icon support
cat > "${APPDIR}/AppRun" << 'APPRUN_EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"

# Set icon paths for proper icon display
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
export QT_STYLE_OVERRIDE=fusion
export QT_SCALE_FACTOR=1

# Set icon theme search path for PyQt5
export QT_ICON_THEME_SEARCH_PATH="${HERE}/usr/share/icons:${QT_ICON_THEME_SEARCH_PATH}"

# Ensure icon is available to desktop environment
if [ -n "$DISPLAY" ]; then
    export GTK_DATA_PREFIX="${HERE}/usr/share:${GTK_DATA_PREFIX}"
    export ICON_THEME_NAME="hicolor"
fi

exec "${HERE}/usr/bin/AV-Morning-Star" "$@"
APPRUN_EOF

chmod +x "${APPDIR}/AppRun"

# Create icon if it doesn't exist
if [ ! -f "av-morning-star.png" ]; then
    echo "Creating application icon..."
    python3 scripts/create_icon.py
fi

# Copy desktop file (must be done BEFORE icon for appimagetool)
cp packaging/com.github.asafelobotomy.avmorningstar.desktop "${APPDIR}/usr/share/applications/"
cp packaging/com.github.asafelobotomy.avmorningstar.desktop "${APPDIR}/"

# Copy AppStream metadata
if [ -f "packaging/com.github.asafelobotomy.avmorningstar.appdata.xml" ]; then
    cp packaging/com.github.asafelobotomy.avmorningstar.appdata.xml "${APPDIR}/usr/share/metainfo/"
fi

# Copy icon to multiple locations for maximum compatibility
echo "Embedding application icon..."
# XDG standard location (primary)
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
cp av-morning-star.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/av-morning-star.png"

# Legacy pixmaps location (secondary)
mkdir -p "${APPDIR}/usr/share/pixmaps"
cp av-morning-star.png "${APPDIR}/usr/share/pixmaps/av-morning-star.png"

# Root level icon (appimagetool will use this for .DirIcon)
cp av-morning-star.png "${APPDIR}/av-morning-star.png"

# DO NOT manually create .DirIcon - let appimagetool handle it

# Download appimagetool if not present, verifying SHA256 via GitHub API before use.
# Uses the canonical appimagetool repo (not the obsolete AppImageKit repo).
APPIMAGETOOL="appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    wget "$TOOL_URL" -O "$APPIMAGETOOL"
    echo "Verifying checksum via GitHub API..."
    EXPECTED_SHA256=$(python3 - <<'PYEOF'
import json, urllib.request, ssl
ctx = ssl.create_default_context()
req = urllib.request.Request(
    "https://api.github.com/repos/AppImage/appimagetool/releases/tags/continuous",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "build-appimage-sh"}
)
with urllib.request.urlopen(req, context=ctx) as r:
    data = json.load(r)
for asset in data.get("assets", []):
    if asset.get("name") == "appimagetool-x86_64.AppImage":
        digest = asset.get("digest", "")
        if digest.startswith("sha256:"):
            print(digest[7:])
            break
PYEOF
)
    if [ -z "$EXPECTED_SHA256" ]; then
        echo "ERROR: Could not retrieve expected SHA256 from GitHub API"
        rm -f "$APPIMAGETOOL"
        exit 1
    fi
    ACTUAL_SHA256=$(sha256sum "$APPIMAGETOOL" | cut -d' ' -f1)
    if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
        echo "ERROR: SHA256 verification failed for appimagetool"
        echo "  Expected: $EXPECTED_SHA256"
        echo "  Actual:   $ACTUAL_SHA256"
        rm -f "$APPIMAGETOOL"
        exit 1
    fi
    echo "✓ Checksum verified"
    chmod +x "$APPIMAGETOOL"
fi

# Create AppImage
echo "Creating AppImage..."
ARCH=x86_64 ./"$APPIMAGETOOL" "${APPDIR}" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

echo "AppImage created successfully: ${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
echo "You can now run it with: ./${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

deactivate
