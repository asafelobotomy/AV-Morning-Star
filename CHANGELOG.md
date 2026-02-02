# Changelog

All notable changes to AV Morning Star will be documented in this file.

## [1.0.0] - 2026-02-02

### Added
- Initial release of AV Morning Star
- Single video download support
- Playlist/channel multi-video download with checkbox selection
- Video quality options (Best, 1080p, 720p, 480p)
- Audio-only download in MP3 format (192 kbps)
- Real-time download progress tracking
- Support for 1000+ sites via yt-dlp
- PyQt5 GUI with intuitive interface
- AppImage packaging for portable distribution
- Virtual environment setup scripts
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

### Technical
- Threading for non-blocking UI operations
- PyQt signals/slots for thread-safe communication
- yt-dlp integration with progress hooks
- FFmpeg for media processing
- Icon support for better desktop integration
- Status bar updates for all operations

### Fixed
- Progress bar now updates correctly during downloads
- Improved progress calculation from yt-dlp data
- Better handling of long filenames
- Enhanced error feedback

### Dependencies
- PyQt5 >= 5.15.0
- yt-dlp >= 2023.0.0
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- Pillow >= 10.0.0
- FFmpeg (system dependency)
