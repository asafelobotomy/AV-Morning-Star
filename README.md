# AV Morning Star - Media Downloader

**Version 0.3.0** | A powerful PyQt5 desktop application for downloading videos and audio from 1000+ websites.

## 🌟 Features

### Core Functionality
- 🎥 **Video Downloads**: Multiple quality options (Best, 4K, 1440p, 1080p, 720p, 480p, 360p)
- 🎵 **Audio Extraction**: MP3, AAC, FLAC, Opus, M4A with quality selection
- 📋 **Playlist Support**: Download entire playlists/channels with multi-selection
- 🔐 **Smart Authentication**: Auto-detects browser cookies for YouTube access
- 🎯 **Dual Mode**: Basic (auto-config) and Advanced (manual settings)

### Advanced Features
- 🎚️ **Audio Processing**:
  - EBU R128 loudness normalization
  - Dynamic audio normalization
  - FFT-based noise reduction
  - Thumbnail embedding
- 📝 **Filename Templates**: Customizable with drag-and-drop tags
- 📑 **Subtitle Support**: Download and embed subtitles
- ⚡ **Real-time Progress**: Live download tracking with status updates
- 🔒 **Privacy First**: Cookieless-first strategy, prompts only when needed

### Smart Browser Detection (New in 0.3.0!)
- 🤖 **Auto Mode**: Automatically finds the best browser with YouTube authentication
- 🔍 **Browser Detection**: Scans Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi
- 🛡️ **Secure**: Read-only access, memory-only cookies, OS keyring encryption
- 💡 **User-Friendly**: Plain-English error messages with actionable recommendations

## 🌐 Supported Sites

Powered by `yt-dlp` (2026.1.31+), supports:
- **YouTube** (with PO token support for 2026)
- **Odysee** / LBRY
- Vimeo, Twitter/X, Facebook, Instagram, TikTok
- **1000+ other sites!**

## ⚙️ Requirements

### Software
- **Python 3.7+**
- **FFmpeg** (for audio/video processing)
- **Deno** or **Node.js 25+** (recommended for YouTube PO tokens)

### Python Packages
- PyQt5 >= 5.15.0
- yt-dlp >= 2026.1.31
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- Pillow >= 10.0.0

## 🚀 Installation

### Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/asafelobotomy/AV-Morning-Star.git
cd AV-Morning-Star

# Run the start script (handles everything automatically)
./start.sh
```

The start script will:
1. Create a virtual environment
2. Install Python dependencies
3. Check for FFmpeg
4. Detect/offer to install Deno (for YouTube)
5. Launch the application

### Manual Installation

1. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3-venv

# Fedora
sudo dnf install ffmpeg python3-virtualenv

# Arch Linux
sudo pacman -S ffmpeg python
```

2. **Install Deno (for YouTube downloads):**
```bash
curl -fsSL https://deno.land/install.sh | sh
echo 'export DENO_INSTALL="$HOME/.deno"' >> ~/.bashrc
echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

3. **Set up Python environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python3 main.py
```

### Build AppImage (Optional)

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

This creates a portable `AV-Morning-Star-0.3.0-x86_64.AppImage` file.

## 📖 Usage

### Basic Workflow

1. **Launch Application**
   ```bash
   ./start.sh  # or: python3 main.py
   ```

2. **Set Up Authentication** (First Time)
   - Go to **Tools > Preferences**
   - Keep "Auto (Recommended)" selected
   - Make sure you're logged into YouTube in your browser (Brave, Firefox, Chrome, etc.)

3. **Download a Video**
   - Paste a YouTube URL (or any supported site)
   - Click "Fetch" to retrieve video information
   - Select the video(s) you want to download
   - Choose format and quality
   - Click "Download Selected"

### Mode Selection

**Basic Mode (Recommended)**
- Auto-detects best quality
- Auto-configures audio settings
- Perfect for most users

**Advanced Mode**
- Manual quality selection
- Audio codec choice (MP3, AAC, FLAC, Opus, M4A)
- Bitrate selection (96-320 kbps)
- Audio enhancement options:
  - EBU R128 normalization
  - Dynamic normalization
  - Noise reduction
  - Thumbnail embedding

### Filename Templates

Customize output filenames with drag-and-drop tags:
- **Title**: Video title
- **Uploader**: Channel/creator name
- **Quality**: Resolution (e.g., "1080p")
- **Format**: Format ID
- **Website**: Platform name
- **ID**: Video ID
- **Upload Date**: Original upload date
- **Download Date**: Current date
- **Duration**: Video length
- **Extension**: File extension

### YouTube Authentication

**How It Works:**
1. App defaults to "Auto" mode
2. Tries cookieless download first (for privacy)
3. If YouTube blocks it, auto-detects your browser
4. Prompts: "Retry with [Browser]?"
5. Uses your browser's login session

**Supported Browsers:**
- Firefox (recommended)
- Chrome / Chromium
- Brave
- Edge
- Opera
- Vivaldi
- Safari (macOS)

**Troubleshooting:**
- Make sure you're logged into YouTube in your browser
- Select "Auto (Recommended)" in Preferences
- If specific browser fails, switch to "Auto" mode

## 🏗️ Architecture

### Modular Extractor System

```
extractors/
├── __init__.py          # Factory function
├── base.py              # BaseExtractor (common interface)
├── youtube_ytdlp.py     # YouTube with PO token support
├── odysee.py            # Odysee/LBRY platform
└── generic.py           # Fallback for 1000+ sites
```

**Key Components:**
- `URLScraperThread`: Fetches video metadata using platform extractors
- `DownloadThread`: Downloads videos/audio with progress tracking
- `MediaDownloaderApp`: PyQt5 GUI with dual-mode interface
- `browser_utils`: Browser detection and cookie management

### Threading Model

- **Main Thread**: GUI updates and user interaction
- **Scraper Thread**: Video metadata extraction (non-blocking)
- **Download Thread**: File downloads with progress hooks (non-blocking)
- **Signals/Slots**: Thread-safe communication via PyQt

## 🔒 Security & Privacy

### Cookie Security
✅ **Read-only access** to browser databases  
✅ **Memory-only storage** (never saved to disk)  
✅ **OS keyring encryption** for cookie database access  
✅ **HTTPS-only** connections to video platforms  
✅ **User consent** required before cookie usage  
✅ **Automatic cleanup** when app closes

### Privacy Features
- **Cookieless-first**: Tries unauthenticated access before using cookies
- **Auto-detection**: Only scans when needed
- **No tracking**: No analytics, no telemetry
- **Local processing**: All operations happen on your machine

**Security Audit:** See [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) for comprehensive review.

## 📚 Documentation

Complete documentation is available in the [`docs/`](docs/) folder:

### User Guides
- **[Getting Started](docs/GETTING_STARTED.md)**: Step-by-step tutorial
- **[Authentication Guide](docs/AUTHENTICATION_GUIDE.md)**: YouTube cookie authentication
- **[Security & Privacy](docs/SECURITY_AND_PRIVACY.md)**: Security explained for users
- **[Smart Browser Detection](docs/SMART_BROWSER_DETECTION.md)**: Auto-detection feature

### Technical Documentation
- **[Architecture](docs/ARCHITECTURE.md)**: Modular extractor system design
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Complete project organization
- **[Security Audit](docs/SECURITY_AUDIT.md)**: Comprehensive technical security review
- **[Reorganization](docs/REORGANIZATION.md)**: v0.3.0 reorganization details

### Quick Links
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
- **[Documentation Index](docs/README.md)**: Full documentation guide
- **[Archive](archive/)**: Historical development documentation

## 🐛 Troubleshooting

### YouTube "Sign in to confirm you're not a bot"
**Solution:** Enable browser authentication
1. Open YouTube in your browser and log in
2. In AV Morning Star: Tools > Preferences
3. Select "Auto (Recommended)"
4. Retry download

### "Firefox cookies not found" (or other browser)
**Solution:** Switch to Auto mode
1. Tools > Preferences
2. Select "Auto (Recommended)"
3. App will find available browser automatically

### No JavaScript runtime found (YouTube)
**Solution:** Install Deno
```bash
curl -fsSL https://deno.land/install.sh | sh
source ~/.bashrc
```

### FFmpeg not found
**Solution:** Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## 🤝 Contributing

Contributions are welcome! To add support for a new platform:

1. Create extractor in `extractors/yourplatform.py`
2. Inherit from `BaseExtractor`
3. Override `extract_info()` and `get_download_opts()`
4. Register in `extractors/__init__.py`

See `ARCHITECTURE.md` for detailed guide.

## 📄 License

This project is open source. See LICENSE file for details.

## 🙏 Acknowledgments

- **yt-dlp**: Powerful video download engine
- **PyQt5**: Excellent GUI framework
- **FFmpeg**: Media processing capabilities
- **Deno**: JavaScript runtime for YouTube PO tokens

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check [`docs/`](docs/) folder
- **Security**: See [Security & Privacy Guide](docs/SECURITY_AND_PRIVACY.md)

---

**AV Morning Star v0.3.0** | Built with ❤️ for video archiving enthusiasts

The build process:
1. Creates a Python virtual environment
2. Installs all dependencies
3. Uses PyInstaller to create a standalone executable
4. Packages everything into an AppImage using appimagetool
5. Produces a portable, single-file application

## Troubleshooting

### FFmpeg Not Found
If you get an error about FFmpeg:
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
```

### PyQt5 Installation Issues
If PyQt5 fails to install:
```bash
# Install system dependencies first
sudo apt install python3-pyqt5  # Ubuntu/Debian
```

### Download Fails
- Check your internet connection
- Verify the URL is valid and accessible
- Some sites may require authentication or have geographical restrictions
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

## License

This project is open source and available for personal and educational use.

## Credits

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Packaged with [AppImageKit](https://github.com/AppImage/AppImageKit)

## Disclaimer

This tool is for personal use only. Please respect copyright laws and terms of service of the websites you download from. The developers are not responsible for any misuse of this software.
