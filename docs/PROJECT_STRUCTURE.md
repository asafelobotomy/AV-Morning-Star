# AV Morning Star - Project Structure

**Version**: 0.3.0  
**Last Updated**: February 3, 2026

## Root Directory

```
AV-Morning-Star/
├── main.py                          # Main application entry point
├── browser_utils.py                 # Browser detection utilities
├── create_icon.py                   # Icon generator script
├── start.sh                         # Quick start script
├── test.sh                          # Test script
├── build-appimage.sh                # AppImage builder
├── requirements.txt                 # Python dependencies
├── VERSION                          # Version number file
├── README.md                        # Main project documentation
├── CHANGELOG.md                     # Version history
├── av-morning-star.png              # App icon (PNG)
├── av-morning-star.desktop          # Desktop entry file
│
├── extractors/                      # Modular platform extractors
│   ├── __init__.py                  # Extractor factory
│   ├── base.py                      # BaseExtractor (common interface)
│   ├── youtube_ytdlp.py             # YouTube with PO token support
│   ├── odysee.py                    # Odysee/LBRY platform
│   └── generic.py                   # Fallback for 1000+ sites
│
├── docs/                            # Documentation
│   ├── README.md                    # Documentation index
│   ├── ARCHITECTURE.md              # Technical architecture
│   ├── AUTHENTICATION_GUIDE.md      # YouTube cookie auth guide
│   ├── GETTING_STARTED.md           # Tutorial
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── REORGANIZATION.md            # v0.3.0 reorganization
│   ├── SECURITY_AUDIT.md            # Security review
│   ├── SECURITY_AND_PRIVACY.md      # User security guide
│   └── SMART_BROWSER_DETECTION.md   # Browser detection feature
│
├── archive/                         # Archived files
│   ├── README.md                    # Archive documentation
│   ├── docs/                        # Old development docs
│   └── deprecated/                  # Deprecated code
│
├── .venv/                           # Python virtual environment
├── .github/                         # GitHub configuration
└── .gitignore                       # Git ignore rules
```

## File Descriptions

### Core Application

**main.py** (1354 lines)
- Main GUI application using PyQt5
- `MediaDownloaderApp`: Main window class
- `URLScraperThread`: Video metadata fetching
- `DownloadThread`: Video/audio downloading
- `PreferencesDialog`: Settings dialog
- `FlowLayout`: Custom layout for filename tags

**browser_utils.py** (~100 lines)
- `detect_available_browsers()`: Find installed browsers
- `get_browsers_with_youtube_cookies()`: Check for YouTube auth
- `get_default_browser()`: Auto-select best browser

### Extractor System

**extractors/__init__.py**
- `get_extractor(url, cookies_from_browser)`: Factory function
- Auto-selects appropriate extractor by URL pattern

**extractors/base.py** (521 lines)
- `BaseExtractor`: Common interface for all platforms
- Audio/video option builders
- Format selection logic
- Audio processing (normalization, denoising)

**extractors/youtube_ytdlp.py** (204 lines)
- YouTube-specific handling with PO token support
- Browser cookie authentication
- Remote component integration (ejs:github)
- Bot detection error handling

**extractors/odysee.py**
- Odysee/LBRY platform support
- Inherits from BaseExtractor

**extractors/generic.py**
- Fallback for 1000+ other sites
- Standard yt-dlp options

### Scripts

**start.sh** (~130 lines)
- Virtual environment setup
- Dependency installation
- FFmpeg check
- Deno detection and installation
- Auto-launch application

**test.sh**
- Import validation
- FFmpeg verification
- yt-dlp YouTube test

**build-appimage.sh**
- PyInstaller executable creation
- AppDir structure generation
- AppImage packaging

**create_icon.py**
- Generates application icon if missing
- Creates circular PNG from source

### Documentation

**README.md**
- Main project documentation
- Installation guide
- Usage instructions
- Feature overview

**CHANGELOG.md**
- Version history with semantic versioning
- Added/Changed/Fixed/Deprecated sections
- Migration notes

**ARCHITECTURE.md**
- Modular extractor system design
- Data flow diagrams
- Extension guide
- Platform-specific features

**AUTHENTICATION_GUIDE.md**
- YouTube cookie authentication
- Browser setup instructions
- Troubleshooting guide
- Security explanations

**SECURITY_AUDIT.md** (8000+ words)
- Comprehensive technical security review
- Cookie extraction analysis
- Threat modeling
- Privacy considerations

**SECURITY_AND_PRIVACY.md** (4000+ words)
- User-friendly security guide
- Plain-English explanations
- Best practices
- FAQ

**SMART_BROWSER_DETECTION.md** (5000+ words)
- Auto-detection feature documentation
- Flowcharts and decision trees
- User scenarios
- API reference

**GETTING_STARTED.md**
- Step-by-step tutorial
- First-time user guide
- Common workflows

### Assets

**av-morning-star.png**
- 256x256 application icon
- Used in GUI and AppImage

**av-morning-star.desktop**
- Linux desktop entry file
- Application launcher configuration

### Configuration

**requirements.txt**
```
PyQt5>=5.15.0
yt-dlp>=2026.1.31
requests>=2.28.0
beautifulsoup4>=4.11.0
Pillow>=10.0.0
```

**VERSION**
```
0.3.0
```

**.gitignore**
- Python cache files
- Virtual environment
- Build artifacts
- IDE files

## Dependencies

### Runtime Dependencies

**Python Packages:**
- PyQt5: GUI framework
- yt-dlp: Video downloading engine
- requests: HTTP library
- beautifulsoup4: HTML parsing
- Pillow: Image processing

**System Dependencies:**
- FFmpeg: Media processing
- Deno (recommended): JavaScript runtime for YouTube

**Optional:**
- Node.js 25+ (alternative to Deno)
- QuickJS (alternative JS runtime)
- Bun (alternative JS runtime)

### Development Dependencies

**Build Tools:**
- PyInstaller: Executable creation
- appimagetool: AppImage packaging

**Testing:**
- pytest (optional)
- mypy (optional, type checking)

## Key Concepts

### Modular Extractor Architecture

Each platform has its own extractor class:
1. Inherits from `BaseExtractor`
2. Implements `extract_info()` for metadata
3. Overrides `get_download_opts()` for platform-specific options
4. Registered in factory function

### Threading Model

- **Main Thread**: GUI and user interaction
- **Scraper Thread**: Non-blocking metadata extraction
- **Download Thread**: Non-blocking file downloads
- **Signals/Slots**: Thread-safe PyQt communication

### Smart Browser Detection

1. User selects "Auto (Recommended)" mode
2. App scans filesystem for browser cookie databases
3. Checks which browsers have YouTube auth cookies
4. Prioritizes browsers with active YouTube sessions
5. Prompts user only when authentication needed

## Version History

- **0.3.0** (2026-02-03): Smart browser detection, centered UI, CHANGELOG
- **0.2.0** (2026-02-02): Preferences menu, browser authentication
- **0.1.0** (2026-02-01): Initial release

## Future Enhancements

Potential improvements:
- [ ] Multiple download threads (parallel downloads)
- [ ] Resume incomplete downloads
- [ ] Download queue management
- [ ] Browser profile selection (multi-profile support)
- [ ] Site-specific authentication strategies
- [ ] Custom extractor plugins
- [ ] Download history tracking
- [ ] Automatic update checking

---

For detailed technical information, see `ARCHITECTURE.md`.  
For usage instructions, see `README.md`.  
For version changes, see `CHANGELOG.md`.
