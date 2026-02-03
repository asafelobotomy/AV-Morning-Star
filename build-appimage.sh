#!/bin/bash
# Build script for creating AV Morning Star AppImage

set -e

APP_NAME="AV-Morning-Star"
APP_VERSION="0.3.0"
BUILD_DIR="build"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"

echo "Building AV Morning Star AppImage..."

# Clean previous build
rm -rf "${BUILD_DIR}"
mkdir -p "${APPDIR}"

# Create AppDir structure
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/applications"
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
    --add-data "av-morning-star.desktop:." \
    --hidden-import=PyQt5 \
    --hidden-import=yt_dlp \
    --collect-all yt_dlp \
    main.py

# Copy executable to AppDir
cp "dist/${APP_NAME}" "${APPDIR}/usr/bin/"

# Create AppRun script
cat > "${APPDIR}/AppRun" << 'APPRUN_EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/AV-Morning-Star" "$@"
APPRUN_EOF

chmod +x "${APPDIR}/AppRun"

# Copy desktop file
cp av-morning-star.desktop "${APPDIR}/usr/share/applications/"
cp av-morning-star.desktop "${APPDIR}/"

# Create icon if it doesn't exist
if [ ! -f "av-morning-star.png" ]; then
    echo "Creating application icon..."
    python3 create_icon.py
fi

# Copy icon
cp av-morning-star.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/"
cp av-morning-star.png "${APPDIR}/"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
echo "Creating AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "${APPDIR}" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

echo "AppImage created successfully: ${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
echo "You can now run it with: ./${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

deactivate
