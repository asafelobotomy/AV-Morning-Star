# AV Morning Star v0.3.0 - Build Guide

**Last Updated:** June 2, 2026

---

## Building the AppImage

### Build Command

```bash
bash scripts/build-appimage.sh
```

This script reads the version from the `VERSION` file, creates an AppDir, packages dependencies, and produces a portable AppImage using `appimagetool`.

### Requirements

**System dependencies:**
- Python 3.7+
- FFmpeg
- PyInstaller (`pip install pyinstaller`)
- appimagetool (downloaded automatically by the build script if not present)

**Python runtime dependencies (bundled into the AppImage):**

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | 5.15.11 | GUI framework |
| yt-dlp | 2026.6.9 | Video downloading engine |
| Pillow | 12.2.0 | Image processing |

### JavaScript Runtime (Optional)

Deno or Node.js may be used by yt-dlp for PO token generation. Install via your package manager or follow the [official Deno installation guide](https://deno.land). The build script does not install Deno.

```bash
# Linux (snap)
snap install deno
# Linux (cargo)
cargo install deno
```

### Output

The build produces:

```
AV-Morning-Star-0.3.0-x86_64.AppImage
```

Run it directly on any Linux distribution with glibc 2.6.32+:

```bash
chmod +x AV-Morning-Star-0.3.0-x86_64.AppImage
./AV-Morning-Star-0.3.0-x86_64.AppImage
```

### Running Without Building

To run from source without building an AppImage:

```bash
./start.sh
```

The `start.sh` script creates a virtual environment, installs Python dependencies, and launches `main.py`.

---

## Notes

- The build script writes the version string from `VERSION` into the AppImage metadata.
- AppImage compression uses Squashfs 4.0 with gzip.
- All Python packages listed in `requirements.txt` are bundled; `requirements-dev.txt` (mcp[cli]) is not included in the AppImage.

