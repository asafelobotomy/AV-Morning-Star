# AV Morning Star - AI Coding Agent Instructions

## Project Overview

AV Morning Star is a **PyQt5 desktop application** for downloading videos/audio from 1000+ sites using yt-dlp. Features modular extractor architecture, browser cookie authentication, and professional audio processing (normalization, denoising).

## Architecture

### Core Components

**Main Application** ([main.py](../main.py)):
- `URLScraperThread`: QThread fetching metadata via platform extractors
- `DownloadThread`: QThread downloading with progress hooks  
- `MediaDownloaderApp`: PyQt5 GUI with dual mode (Basic auto-config / Advanced manual settings)
- `FlowLayout`: Custom wrapping layout for filename template tags

**Extractor System** ([extractors/](../extractors/)):
- `BaseExtractor`: Common interface for all platforms - defines `extract_info()`, `get_download_opts()`, audio/video option builders
- `YouTubeExtractor` ([youtube_ytdlp.py](../extractors/youtube_ytdlp.py)): Handles YouTube's Proof of Origin tokens, browser cookies, bot detection. **Requires external JS runtime (Deno/Node.js 25+)** for PO token generation
- `OdyseeExtractor`: Odysee/LBRY support
- `GenericExtractor`: Fallback for 1000+ other sites
- `get_extractor(url, cookies_from_browser=None)`: Factory function auto-selecting extractor by URL pattern

**Authentication** ([browser_utils.py](../browser_utils.py)):
- `detect_available_browsers()`: Scans for installed browsers by cookie file paths
- `get_browsers_with_youtube_cookies()`: Checks which browsers have YouTube auth cookies (SAPISID/SSID/etc.)
- `get_default_browser()`: Auto-selects best browser (priority: YouTube cookies → first available → None)

### Critical Data Flows

**Fetching Videos**:
```
User URL → URLScraperThread → get_extractor(url, browser) → 
extractor.extract_info() → Returns list[{url, title, uploader, duration, ...}] →
Displayed as checkboxes in GUI
```

**Downloading**:
```
Selected URLs → DownloadThread → For each URL:
  get_extractor(url, browser) → extractor.get_download_opts() → 
  yt_dlp.YoutubeDL(opts).download([url]) with progress_hook
```

**YouTube Authentication Flow** (as of Feb 2026):
```
browser_preference ('auto'/'firefox'/'chrome'/etc.) → 
Resolve to actual browser → Extract cookies via yt-dlp.cookies → 
Pass to yt-dlp as cookiesfrombrowser → YouTube accepts as logged-in user
```

## Critical Dependencies

- **FFmpeg**: Runtime requirement for audio extraction/video merging (NOT in requirements.txt - system package)
- **Deno/Node.js 25+**: Required for YouTube Proof of Origin tokens (checked in [start.sh](../start.sh) lines 73-128). Alternatives: QuickJS, Bun
- **yt-dlp**: Core downloader - avoid version pinning (rapidly evolves to counter bot detection)
- **PyQt5**: GUI framework - prefer pip over system packages to avoid conflicts

## Development Workflows

### Quick start
```bash
./start.sh  # Creates venv, installs deps, checks FFmpeg/Deno, runs app
```

### Testing
```bash
./test.sh  # Validates imports + FFmpeg + yt-dlp against known YouTube video
```

### Building AppImage
```bash
./build-appimage.sh  # PyInstaller → AppDir → AppImage (requires appimagetool)
# Critical: Uses --collect-all yt_dlp to bundle all site extractors
```

### Adding a New Platform

1. **Create extractor** in `extractors/myplatform.py`:
```python
from .base import BaseExtractor

class MyPlatformExtractor(BaseExtractor):
    def __init__(self, url):
        super().__init__(url)
        self.platform_name = "MyPlatform"
    
    def get_download_opts(self, ...):
        opts = super().get_download_opts(...)
        opts['my_custom_option'] = 'value'  # Platform-specific tweaks
        return opts
```

2. **Register in factory** ([extractors/__init__.py](../extractors/__init__.py)):
```python
def get_extractor(url, cookies_from_browser=None):
    if 'myplatform.com' in url.lower():
        return MyPlatformExtractor(url)
    # ... existing checks
```

**No changes to main.py needed** - extractor system is plug-and-play.

## Project Conventions

### Code Organization
- **Modular extractors, monolithic UI**: Platform logic in `extractors/`, all GUI in `main.py` (intentional simplicity)
- **Threading**: ALL I/O in QThread subclasses. Use PyQt signals/slots for thread-safe communication (never modify GUI from worker threads)
- **Error handling**: GUI errors → QMessageBox, thread errors → pyqtSignal(str) → QMessageBox in main thread

### Audio Processing (Advanced Features)
Audio filters in [base.py](../extractors/base.py) `_get_audio_opts()`:
- **Normalization**: `loudnorm=I=-16:LRA=11:TP=-1.5` (EBU R128 broadcast standard)
- **Dynamic normalization**: `dynaudnorm=p=0.95:m=10:s=12:g=5` (alternative for varying volume)
- **Denoising**: `afftdn=nf=-20` (FFT-based noise floor removal)
- Filters chain via `postprocessor_args`: `['-af', ','.join(audio_filters)]`

### Format Selection Patterns
Video quality format strings ([base.py](../extractors/base.py) lines 363-379):
```python
'bestvideo[height<=1080]+bestaudio/bestvideo*+bestaudio/best'  
# Primary: exact height limit + Fallback: any video + audio + Fallback: single best format
```
Always include multiple fallbacks - single format specs fail when unavailable.

### Progress Tracking
yt-dlp progress hook dictionary has version-dependent keys:
```python
def progress_hook(self, d):
    percent = 0
    # Try multiple extraction methods (order matters)
    if '_percent_str' in d:
        percent = float(d['_percent_str'].replace('%', ''))
    elif 'downloaded_bytes' in d and 'total_bytes' in d:
        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
    # ... more fallbacks
```

## Common Pitfalls

1. **YouTube downloads fail**: Missing Deno/Node.js (PO token generation). Check [start.sh](../start.sh) warnings or run `deno --version`
2. **"Sign in to confirm" errors**: Browser cookies not found. User must be logged into YouTube in selected browser. Set `browser_preference='auto'` for smart detection
3. **Format not available**: Used single format spec without fallbacks. Always use `format1/format2/format3` pattern
4. **AppImage missing extractors**: Forgot `--collect-all yt_dlp` in PyInstaller spec ([build-appimage.sh](../build-appimage.sh) line 36)
5. **GUI freezes**: Blocking operation in main thread. Move to QThread with signals
6. **Checkbox state desync**: Modified `self.checkboxes` without updating `self.videos_list` or vice versa

## YouTube-Specific Implementation

### Bot Detection Handling ([main.py](../main.py) lines 467-533)
Smart retry logic:
1. First attempt: Cookieless (works for most public videos)
2. On bot error: Auto-detect browser with YouTube cookies
3. Prompt user: "Retry with {browser}?" 
4. Set `self.cookieless_failed = True` to skip cookieless on next fetch

### User-Friendly Cookie Errors ([main.py](../main.py) lines 401-459)
Parse yt-dlp exceptions into actionable messages:
- "could not find cookies database" → "Browser not installed, try Auto mode"
- "database corrupt" → "Restart browser and retry"
- "permission denied" → "Close browser (may lock cookie files)"

## Key Files

- [main.py](../main.py): Application (1300+ lines with FlowLayout, PreferencesDialog, filename template builder)
- [extractors/base.py](../extractors/base.py): Common extraction logic (521 lines)
- [extractors/youtube_ytdlp.py](../extractors/youtube_ytdlp.py): YouTube with PO token support (204 lines)
- [browser_utils.py](../browser_utils.py): Browser detection/cookie utilities (116 lines)
- [start.sh](../start.sh): Entry point with dependency checks
- [AUTHENTICATION_GUIDE.md](../AUTHENTICATION_GUIDE.md): User-facing YouTube auth docs

## When Modifying Code

- **New platform**: Create extractor in `extractors/`, register in `__init__.py`. See [ARCHITECTURE.md](../ARCHITECTURE.md) lines 100-147
- **UI changes**: Modify `MediaDownloaderApp.init_ui()`. Maintain QGroupBox structure for consistency
- **Download options**: Edit `BaseExtractor._get_video_opts()` or `_get_audio_opts()` for global changes, override in platform extractor for platform-specific
- **Authentication**: Extend `browser_utils.py` for new browsers, add to `detect_available_browsers()` mapping
- **Filename template**: Tags mapped in `MediaDownloaderApp.build_filename_template()` to yt-dlp variables like `%(title)s`, `%(uploader)s`
