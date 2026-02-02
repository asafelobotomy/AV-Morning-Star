# AV Morning Star - AI Coding Agent Instructions

## Project Overview

AV Morning Star is a **PyQt5 desktop application** for downloading videos/audio from 1000+ sites using yt-dlp. It supports single videos, playlists, and channels with quality selection and real-time progress tracking.

## Architecture

**Single-file monolithic design** ([main.py](../main.py)):
- `URLScraperThread`: QThread for fetching video metadata via yt-dlp (lines 23-65)
- `DownloadThread`: QThread for downloading with progress hooks (lines 68-148)
- `MediaDownloaderApp`: Main QMainWindow with all UI logic (lines 151-421)

**Threading model**: All I/O operations (URL fetching, downloads) run in separate QThreads to keep UI responsive. Progress updates use PyQt signals/slots for thread-safe communication.

**yt-dlp integration pattern**:
```python
# Fetching uses extract_flat for efficiency
ydl_opts = {'extract_flat': True, 'quiet': True}

# Downloads use format selectors for quality control
ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

# Audio extraction uses FFmpeg postprocessor
ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', ...}]
```

## Critical Dependencies

- **FFmpeg**: Required at runtime for audio extraction and video merging (not in requirements.txt)
- **yt-dlp**: Core downloader - frequently updated, so version pinning may break functionality
- **PyQt5**: GUI framework - system packages may conflict with pip version

## Development Workflows

### Running the app
```bash
./start.sh  # Handles venv creation, dependency install, and launch
```

### Testing
```bash
./test.sh  # Validates imports, FFmpeg, and yt-dlp functionality
```

### Building AppImage
```bash
./build-appimage.sh  # PyInstaller → AppDir → AppImage (requires appimagetool)
```

## Project Conventions

1. **No separate modules**: Everything in main.py by design for simplicity
2. **Error handling**: GUI errors via QMessageBox, thread errors via pyqtSignal(str)
3. **Path handling**: Uses `os.path.join()` for cross-platform compatibility
4. **Progress tracking**: Must parse yt-dlp's progress hook dictionary (keys vary by version)

## Common Pitfalls

- **Don't use subprocess for yt-dlp**: Use the Python API (YoutubeDL class) for proper progress hooks
- **Video quality selection**: Format strings must be yt-dlp-compatible (e.g., `bestvideo[height<=720]+bestaudio`)
- **Checkbox state**: Track both `self.checkboxes` (UI) and `self.videos_list` (data) in sync
- **AppImage builds**: PyInstaller's `--collect-all yt_dlp` is critical to bundle all extractors

## Key Files

- [main.py](../main.py): Entire application (421 lines)
- [start.sh](../start.sh): Quick start script with venv management
- [build-appimage.sh](../build-appimage.sh): PyInstaller + AppImage build pipeline
- [requirements.txt](../requirements.txt): Python dependencies (no FFmpeg)

## Integration Points

- **yt-dlp extractors**: Auto-detected via URL, supports 1000+ sites
- **FFmpeg**: External system dependency called by yt-dlp for postprocessing
- **OS file browser**: QFileDialog for output path selection
- **System Downloads folder**: Default save location via `os.path.expanduser("~/Downloads")`

## When Modifying Code

- **Adding features**: Extend MediaDownloaderApp class, use QThread for I/O
- **UI changes**: Modify init_ui() method, maintain existing QGroupBox structure
- **Download logic**: Edit DownloadThread.run(), preserve progress_hook pattern
- **New video sources**: yt-dlp handles automatically - test with URL patterns
