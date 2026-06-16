# AV Morning Star - Project Structure

**Version**: 0.3.0
**Last Updated**: June 2, 2026

## Root Directory

```
AV-Morning-Star/
├── main.py                          # Main PyQt5 application
├── browser_utils.py                 # Browser detection and cookie utilities
├── constants.py                     # Application constants and configuration
├── start.sh                         # Quick start launcher
├── requirements.txt                 # Python runtime dependencies
├── requirements-dev.txt             # Development-only dependencies (mcp[cli])
├── requirements-lock.txt            # Pinned lockfile (5 runtime packages)
├── VERSION                          # Single source of version truth (0.3.0)
├── README.md                        # Main project documentation
├── CHANGELOG.md                     # Version history and release notes
└── av-morning-star.png              # Application icon (PNG)
│
├── scripts/                         # Build, test, and utility scripts
│   ├── build-appimage.sh            # AppImage builder (reads version from VERSION)
│   ├── test.sh                      # Test runner (imports + unittest suite)
│   └── create_icon.py               # Icon generator
│
├── packaging/                       # Linux packaging metadata
│   ├── com.github.asafelobotomy.avmorningstar.desktop    # Desktop entry
│   └── com.github.asafelobotomy.avmorningstar.appdata.xml  # AppStream metadata
│
├── extractors/                      # Modular platform extractors
│   ├── __init__.py                  # Factory function: get_extractor()
│   ├── base.py                      # BaseExtractor (common interface + filter constants)
│   ├── youtube_ytdlp.py             # YouTube with PO token support
│   ├── odysee.py                    # Odysee/LBRY platform
│   ├── generic.py                   # Fallback for 1000+ yt-dlp sites
│   └── podcast_page.py              # Direct-download podcast pages
│
├── tests/                           # Automated test suite (unittest)
│   ├── __init__.py
│   ├── test_extractors.py           # Extractor and filter-chain tests
│   ├── test_main_logic.py           # Main application logic tests
│   └── test_browser_utils.py        # Browser detection tests
│
├── docs/                            # Project documentation
│   ├── README.md                    # Documentation index
│   ├── ARCHITECTURE.md              # Technical system design
│   ├── AUTHENTICATION_GUIDE.md      # YouTube cookie auth guide
│   ├── BUILD_SUMMARY.md             # Latest AppImage build report
│   ├── CONSTANTS.md                 # Application constants reference
│   ├── EXTRACTORS_COVERAGE_ANALYSIS.md  # Platform coverage
│   ├── GETTING_STARTED.md           # Beginner tutorial
│   ├── ORGANIZATION_COMPLETE.md     # v0.3.0 reorganization record
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── REORGANIZATION.md            # v0.3.0 reorganization notes
│   ├── SECURITY_AUDIT.md            # 8000+ word security review
│   ├── SECURITY_AND_PRIVACY.md      # User-friendly security guide
│   ├── SMART_BROWSER_DETECTION.md   # Auto browser detection feature
│   └── images/                      # Documentation images
│
├── archive/                         # Historical and deprecated files
│   ├── README.md                    # Archive index
│   ├── history/                     # Deprecated code (superseded by active modules)
│   │   ├── youtube_innertube.py     # Old InnerTube extractor
│   │   ├── youtube_oauth.py         # Old OAuth2 flow
│   │   ├── youtube.py.backup        # Backup of previous YouTube extractor
│   │   ├── download_icon.py         # Superseded by create_icon.py
│   │   ├── replace-icon.sh          # Superseded by build-appimage.sh
│   │   └── test_codecs.py           # Superseded by tests/
│   └── legacy/                      # Superseded documentation
│       ├── release-notes.md         # Superseded by CHANGELOG.md
│       ├── REPOSITORY_ORGANIZATION.md  # Superseded by this file
│       ├── docs/                    # Historical development docs (InnerTube era)
│       └── reports/                 # Feb 2026 code review reports
│
├── .github/                         # GitHub / Copilot surface
└── .gitignore                       # Git ignore rules└── .vscode/
    └── mcp.json                     # MCP server configuration```

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
- Bot detection error handling

**extractors/odysee.py**
- Odysee/LBRY platform support
- Inherits from BaseExtractor

**extractors/generic.py**
- Fallback for 1000+ other sites
- Standard yt-dlp options

### Tests

**tests/test_extractors.py**
- Extractor and filter-chain tests

**tests/test_main_logic.py**
- Main application logic tests (closeEvent, thread lifecycle, audio codec mapping)

**tests/test_browser_utils.py**
- Browser detection tests

### Scripts

**start.sh**
- Primary user launcher — sets up virtual environment, installs dependencies, checks FFmpeg, launches `main.py`

**scripts/build-appimage.sh**
- Version-sync check (VERSION vs constants.py)
- PyInstaller executable creation
- AppDir structure generation
- AppImage packaging

**scripts/test.sh**
- Import validation
- FFmpeg verification
- `python3 -m unittest discover -s tests -v`

**scripts/create_icon.py**
- Generates `av-morning-star.png` if missing
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
PyQt5==5.15.11
yt-dlp==2026.6.9
Pillow==12.2.0
```

**requirements-dev.txt**
```
mcp[cli]==1.27.2
```

**requirements-lock.txt**
Pinned lockfile with 5 runtime packages: pillow, PyQt5, PyQt5-Qt5, PyQt5_sip, yt-dlp.

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
- PyQt5==5.15.11: GUI framework
- yt-dlp==2026.6.9: Video downloading engine
- Pillow==12.2.0: Image processing

**Development-Only:**
- mcp[cli]==1.27.2: MCP server tooling (requirements-dev.txt)

**System Dependencies:**
- FFmpeg: Media processing
- Deno (recommended): JavaScript runtime for YouTube

**Optional:**
- Node.js 22+ LTS (alternative to Deno)
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
