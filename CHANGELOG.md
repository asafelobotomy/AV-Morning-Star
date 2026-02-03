# Changelog

All notable changes to AV Morning Star will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-03

### Added
- **Smart Browser Detection**: Auto-detects browsers with YouTube authentication cookies
- **Auto Mode (Default)**: Automatically selects the best browser for YouTube authentication
- **Cookieless-First Strategy**: Tries unauthenticated access first for privacy, prompts only when needed
- **User-Friendly Error Messages**: Plain-English explanations for cookie/authentication failures
- **Browser Utilities Module**: New `browser_utils.py` for browser detection and cookie management
- **Centered Banner**: Logo and title now centered in the UI for better aesthetics
- **Documentation Organization**: All guides moved to `docs/` folder with comprehensive index
- Comprehensive documentation:
  - `docs/SMART_BROWSER_DETECTION.md`: Feature guide with flowcharts and scenarios
  - `docs/SECURITY_AUDIT.md`: 8000+ word technical security review
  - `docs/SECURITY_AND_PRIVACY.md`: User-friendly security guide
  - `docs/README.md`: Complete documentation index

### Changed
- **Default Authentication**: Changed from hardcoded 'Brave' to 'Auto (Recommended)'
- **Preferences Menu**: Reorganized with Auto mode as first option
- **YouTube Extraction**: Now uses yt-dlp backend instead of InnerTube library
- **PO Token Support**: Enabled remote components for YouTube Proof of Origin tokens
- **Error Handling**: Enhanced with specific messages for browser detection failures
- **Documentation Structure**: Moved 8 documentation files to `docs/` folder
- Version number updated to 0.3.0 across all build files
- Help dialog now references `docs/` folder

### Fixed
- YouTube bot detection bypass using browser cookies
- Download thread now properly receives browser cookie parameter
- Syntax errors in error handling methods
- Banner alignment in main UI

### Technical
- Replaced InnerTube API with yt-dlp backend for YouTube
- Deno 2.6.8 JavaScript runtime support for PO token generation
- Cookie extraction from 7 major browsers (Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi)
- Priority-based browser selection (YouTube cookies > Available > None)
- Memory-only cookie handling (no disk storage)
- OS keyring integration for encrypted browser database access

### Security
- Comprehensive security audit completed (no vulnerabilities found)
- Read-only browser access
- User consent required before cookie usage
- HTTPS-only connections enforced
- Automatic cookie cleanup after use

### Deprecated
- OAuth2 authentication system (removed - too complex)
- Direct InnerTube API (replaced with yt-dlp)
- Hardcoded browser defaults (replaced with auto-detection)

### Documentation
- Archived old development docs to `archive/docs/`
- Archived deprecated scripts to `archive/deprecated/`
- Updated README with current feature set
- Added comprehensive security and privacy documentation

---

## [0.2.0] - 2026-02-02

### Added
- Menu bar with Tools > Preferences, About, Help
- Preferences dialog for browser authentication settings
- YouTube browser cookie authentication
- Support for multiple browsers (Firefox, Chrome, Brave, Edge, etc.)

### Changed
- Moved YouTube authentication from main UI to Preferences menu
- Improved UI organization and clarity

---

## [0.1.0] - 2026-02-01

### Added
- Initial release of AV Morning Star
- Single video download support
- Playlist/channel multi-video download with checkbox selection
- Video quality options (Best, 4K, 1440p, 1080p, 720p, 480p, 360p)
- Audio-only download in multiple formats (MP3, AAC, FLAC, Opus, M4A)
- Audio quality selection (320/256/192/128/96 kbps)
- Advanced audio processing:
  - EBU R128 loudness normalization
  - Dynamic audio normalization
  - FFT-based audio denoising
  - Thumbnail embedding for audio files
- Real-time download progress tracking
- Support for 1000+ sites via yt-dlp
- PyQt5 GUI with intuitive interface
- Modular extractor architecture:
  - `BaseExtractor`: Common interface for all platforms
  - `YouTubeExtractor`: YouTube-specific handling
  - `OdyseeExtractor`: Odysee/LBRY support
  - `GenericExtractor`: Fallback for all other sites
- Filename template builder with drag-and-drop tags
- Subtitle download and embedding
- AppImage packaging for portable distribution
- Virtual environment setup scripts (`start.sh`, `test.sh`)
- Comprehensive documentation

### Features
- **URL Scraping**: Automatically detects single videos vs playlists/channels
- **Multi-selection**: Select/deselect individual videos or use Select All/None
- **Progress Tracking**: Real-time progress bar with status updates
- **Format Options**: Choose between video formats or audio extraction
- **Quality Selection**: Multiple video quality presets
- **Custom Output Path**: Choose where to save downloads
- **Error Handling**: User-friendly error messages and validation
- **Keyboard Shortcuts**: Press Enter to fetch videos
- **Dual Mode**: Basic (auto-detect) and Advanced (manual settings)

### Technical
- Threading for non-blocking UI operations (QThread)
- PyQt signals/slots for thread-safe communication
- yt-dlp integration with progress hooks
- FFmpeg for media processing and audio filters
- Modular platform-specific extractors
- Icon support for better desktop integration
- Status bar updates for all operations
- FlowLayout for wrapping filename template tags

### Dependencies
- Python 3.7+
- PyQt5 >= 5.15.0
- yt-dlp >= 2026.1.31
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- Pillow >= 10.0.0
- FFmpeg (system dependency)
- Deno/Node.js 25+/QuickJS/Bun (for YouTube PO tokens)
