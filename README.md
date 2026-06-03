<div align="center">

<img src="av-morning-star.png" alt="AV Morning Star" width="160">

# AV Morning Star

**Video & Audio Downloader for Linux**

[![Release](https://img.shields.io/github/v/release/asafelobotomy/AV-Morning-Star?style=flat-square)](https://github.com/asafelobotomy/AV-Morning-Star/releases)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-122%20passing-brightgreen?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/platform-Linux%20x86__64-lightgrey?style=flat-square)](#)

[**⬇ Download AppImage**](https://github.com/asafelobotomy/AV-Morning-Star/releases/latest) · [Documentation](docs/README.md) · [Report a Bug](https://github.com/asafelobotomy/AV-Morning-Star/issues)

</div>

---

AV Morning Star is a desktop application for downloading video and audio from YouTube, Odysee, and 1000+ other sites. It wraps [yt-dlp](https://github.com/yt-dlp/yt-dlp) in a clean PyQt5 GUI, adds smart YouTube authentication, real-time progress, audio/video post-processing, and a flexible filename template system — all packaged as a self-contained Linux AppImage.

---

## Screenshots

<div align="center">
<img src="docs/images/app-screenshot.png" alt="AV Morning Star Interface" width="820">
<p><em>Main window — dark mode (default). Light mode available via View menu.</em></p>
</div>

---

## Features

### Downloading
- **Video** — Best, 4K, 1440p, 1080p, 720p, 480p, 360p
- **Audio extraction** — MP3, AAC, FLAC, Opus, M4A, WAV, ALAC with bitrate selection
- **Playlists & channels** — fetch all entries, select the ones you want
- **Subtitle embedding** — download and mux subtitles automatically
- **1000+ sites** — anything yt-dlp supports, including YouTube, Vimeo, Twitch, Odysee, Twitter/X, TikTok, and more

### YouTube Authentication
- **Cookieless by default** — no authentication until YouTube requires it
- **Smart browser detection** — auto-selects the browser where you're already logged in
- **Supported browsers** — Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi
- **User-consent model** — prompts before reading any browser cookies
- **In-memory only** — cookies are never written to disk by this app

### Audio Enhancement (Advanced mode)
- EBU R128 broadcast loudness normalisation
- Dynamic normalisation for varying-volume content
- FFT-based noise reduction
- Thumbnail / album-art embedding

### Video Enhancement (Advanced mode)
- Temporal denoising (`hqdn3d`) for grainy footage
- Camera-shake stabilisation (`deshake`)
- Edge-aware sharpening (unsharp mask)
- Audio post-processing on video tracks
- Output containers: MP4, MKV, WebM, MOV, AVI, FLV

### Filename Templates
Click tags to compose the output filename. Supported tokens:

| Token | Example value |
|---|---|
| Title | `Amazing Video` |
| Uploader | `Channel Name` |
| Quality | `1080p` |
| Format | `mp4` |
| Website | `YouTube` |
| ID | `dQw4w9WgXcQ` |
| Upload Date | `20260603` |
| Timestamp | `1749000000` |
| Duration | `03:45:20` |
| Extension | `mp4` |

### Interface
- **Dark / Light theme** — toggle any time via View menu
- **Basic mode** — one-click download, auto-detects best quality
- **Advanced mode** — full control over codecs, bitrates, and post-processing
- **Real-time progress** — live filename, percentage, and status updates

---

## Installation

### AppImage (recommended)

```bash
# Download
wget https://github.com/asafelobotomy/AV-Morning-Star/releases/download/v0.4.0/AV-Morning-Star-0.4.0-x86_64.AppImage

# Make executable and run
chmod +x AV-Morning-Star-0.4.0-x86_64.AppImage
./AV-Morning-Star-0.4.0-x86_64.AppImage
```

The AppImage is self-contained (~63 MB). It requires:
- **FFmpeg** — for audio/video processing
- **Deno**, **Node.js 25+**, or another JS runtime — for YouTube PO token generation (recommended; app works without it but YouTube reliability improves significantly)

Install FFmpeg:

```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

### From Source

```bash
git clone https://github.com/asafelobotomy/AV-Morning-Star.git
cd AV-Morning-Star
chmod +x start.sh && ./start.sh
```

`start.sh` creates a virtual environment, installs dependencies, and launches the app.

**Manual steps:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**Requirements:** Python 3.10+, FFmpeg, and optionally a JS runtime for YouTube.

### Build AppImage from Source

```bash
chmod +x scripts/build-appimage.sh
./scripts/build-appimage.sh
```

Outputs `AV-Morning-Star-<version>-x86_64.AppImage` in the project root.

---

## Usage

```
1. Launch             →  ./AV-Morning-Star-0.4.0-x86_64.AppImage
2. Set authentication →  Tools > Preferences  (leave on "Auto" by default)
3. Paste a URL        →  YouTube playlist, Odysee channel, any supported site
4. Click Fetch        →  Retrieves title, duration, and uploader for each item
5. Select videos      →  Check the ones you want
6. Choose settings    →  Mode, quality, format (Basic mode does this automatically)
7. Click Download     →  Files saved to your chosen output directory
```

### YouTube Authentication

For most videos no login is needed. When YouTube requires authentication:

1. Make sure you are logged into YouTube in your browser
2. Open **Tools → Preferences** and ensure Authentication is set to **Auto (Recommended)**
3. Re-fetch — the app will detect your browser and ask for confirmation before using cookies

---

## Architecture

```
AV-Morning-Star/
├── main.py                  # GUI application (PyQt5)
├── themes.py                # Dark + Light theme definitions (QSS)
├── constants.py             # Shared string constants
├── browser_utils.py         # Browser cookie detection
├── extractors/
│   ├── base.py              # BaseExtractor interface
│   ├── youtube_ytdlp.py     # YouTube (PO token support)
│   ├── odysee.py            # Odysee / LBRY
│   ├── podcast_page.py      # Podcast RSS feeds
│   └── generic.py           # Fallback (1000+ sites via yt-dlp)
├── scripts/
│   └── build-appimage.sh    # Reproducible AppImage build
├── tests/                   # 122 unit tests (unittest)
└── packaging/               # .desktop and AppStream metadata
```

**Threading model:** the GUI runs on the main thread. Metadata fetching (`URLScraperThread`) and downloads (`DownloadThread`) each run on separate worker threads and communicate back via PyQt signals.

**Adding a new platform:** create `extractors/yourplatform.py` inheriting `BaseExtractor`, implement `extract_info()` and `get_download_opts()`, then register the URL pattern in `extractors/__init__.py`. No changes to `main.py` needed. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Security & Privacy

| Property | Detail |
|---|---|
| Cookieless by default | Authentication only triggered when the site requires it |
| In-memory cookies | Browser cookies are never written to disk by this app |
| Read-only browser access | Cannot modify your browser's stored data |
| User consent | Prompts before reading any browser session |
| No telemetry | Zero analytics, no network calls except to the download target |
| Open source | Inspect the code at any time |

See [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) and [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) for full detail.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "Sign in to confirm you're not a bot" | Log into YouTube in your browser; set Auth to Auto in Preferences |
| "Browser cookies not found" | Close the browser, reopen, retry; or switch to Auto mode |
| "FFmpeg not found" | Install FFmpeg via your package manager (see above) |
| "No JavaScript runtime found" | Install Deno (`snap install deno`) or Node.js 25+ |
| Download stuck / very slow | Check connection; try a different quality setting |
| "Requested format not available" | Choose a lower quality; the video may have limited formats |

---

## Documentation

| Guide | Contents |
|---|---|
| [Getting Started](docs/GETTING_STARTED.md) | Step-by-step first-run walkthrough |
| [Authentication Guide](docs/AUTHENTICATION_GUIDE.md) | YouTube cookie authentication in depth |
| [Smart Browser Detection](docs/SMART_BROWSER_DETECTION.md) | How auto browser selection works |
| [Security & Privacy](docs/SECURITY_AND_PRIVACY.md) | User-facing security explanation |
| [Architecture](docs/ARCHITECTURE.md) | Extractor system and threading model |
| [Project Structure](docs/PROJECT_STRUCTURE.md) | Every file explained |
| [Security Audit](docs/SECURITY_AUDIT.md) | Technical security review |
| [CHANGELOG](CHANGELOG.md) | Version history |

---

## Contributing

Pull requests are welcome. Please:

1. Run the test suite before submitting: `python3 -m unittest discover -s tests -p "test_*.py"`
2. Add or update tests for any changed behaviour
3. Keep changes focused — one concern per PR

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.

---

## Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — video downloading engine
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) — GUI framework
- [FFmpeg](https://ffmpeg.org/) — audio/video processing
- [Deno](https://deno.land/) — JavaScript runtime for YouTube PO tokens

---

> **Disclaimer:** This tool is for personal, lawful use only. Respect copyright law, website terms of service, and creator permissions. The authors are not responsible for misuse.

<div align="center"><sub>AV Morning Star v0.4.0 · Linux x86_64</sub></div>


# AV Morning Star

### Video & Audio Downloader

> A powerful, privacy-first desktop application for downloading videos and audio from 1000+ websites.

[![Release](https://img.shields.io/github/v/release/asafelobotomy/AV-Morning-Star)](https://github.com/asafelobotomy/AV-Morning-Star/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/asafelobotomy/AV-Morning-Star)

**Version 0.3.0** | Built with PyQt5 & yt-dlp | [📖 Full Documentation](docs/README.md)

[Download AppImage](https://github.com/asafelobotomy/AV-Morning-Star/releases/latest) • [Documentation](docs/README.md) • [Report Bug](https://github.com/asafelobotomy/AV-Morning-Star/issues)

</div>

---

## 📸 Screenshots

<div align="center">
<img src="docs/images/app-screenshot.png" alt="AV Morning Star Interface" width="800">
<p><i>Clean, intuitive interface with interactive filename tag selection</i></p>
</div>

---

## 🆕 What's New in v0.3.0

### 📦 AppImage Distribution
- **Self-contained Linux package** (69 MB) - no installation required
- Works on any distribution with glibc 2.6.32+ (Ubuntu 20.04+, Fedora 32+, Arch, etc.)
- Desktop integration with proper icon embedding
- Squashfs 4.0 compression (98.94% efficiency)

### 🎬 Video Enhancement
- **Denoise video** - 3D temporal denoising for grainy footage
- **Stabilize video** - Reduce camera shake with deshake filter
- **Sharpen video** - Unsharp mask with edge-aware settings
- **Audio processing** - Normalization & denoising for video audio
- **Container support** - MP4, MKV, WebM, MOV, AVI, FLV

### 🔧 Build System Improvements
- Enhanced AppImage build script with proper icon handling
- Icon now uses .DirIcon symlink (AppImageKit standard)
- Improved AppRun script with icon environment variables
- Comprehensive build documentation ([BUILD_SUMMARY.md](docs/BUILD_SUMMARY.md))

### 📚 Documentation Updates
- Platform extractor coverage analysis
- Complete build verification checklist
- Distribution guidelines and system requirements
- Enhanced security and privacy documentation

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## ✨ Features

### 🎯 Core Functionality
- **🎥 Video Downloads** – Multiple quality options (Best, 4K, 1440p, 1080p, 720p, 480p, 360p)
- **🎵 Audio Extraction** – MP3, AAC, FLAC, Opus, M4A with bitrate selection
- **📋 Playlist Support** – Download entire playlists/channels with multi-selection
- **🔐 Smart Authentication** – Auto-detects browser cookies for YouTube access
- **🎯 Dual Mode** – Basic (auto-config) & Advanced (manual settings)

### 🚀 Advanced Features
- **🎚️ Audio Enhancement**
  - EBU R128 broadcast-standard loudness normalization
  - Dynamic normalization for varying volume levels
  - FFT-based noise reduction (adaptive filtering)
  - Thumbnail/album art embedding
- **📝 Filename Customization** – click-to-add/remove filename tags (title, uploader, date, duration, etc.)
- **📑 Subtitle Handling** – Download and embed subtitles automatically
- **⚡ Real-time Progress** – Live download tracking with filename and percentage
- **🔒 Privacy-First** – Cookieless by default, authenticated only when needed

### 🧠 Smart Browser Detection (New in v0.3.0!)
- **🤖 Auto Mode** – Intelligently finds the best browser with YouTube authentication
- **🔍 Browser Support** – Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi
- **🛡️ Secure by Design** – Read-only access, in-memory storage, OS keyring encryption
- **💬 User-Friendly** – Plain-English errors with actionable solutions

### 🎬 Video Enhancement (New in v0.3.0!)
- **🎞️ Denoise** – 3D temporal denoising (hqdn3d) for grainy footage
- **🤳 Stabilize** – Camera shake reduction (deshake filter)
- **✨ Sharpen** – Unsharp mask with edge-aware settings
- **🔊 Audio Processing** – Normalization & denoising for video audio tracks
- **📦 Container Support** – MP4, MKV, WebM, MOV, AVI, FLV

## 🌐 Supported Platforms

Powered by **yt-dlp (2026.3.17+)** with support for:

| Category | Platforms |
|----------|-----------|
| **Streaming** | YouTube, Vimeo, Twitch, DailyMotion |
| **Social Media** | Twitter/X, Facebook, Instagram, TikTok, Snapchat |
| **Alternatives** | Odysee/LBRY, Rumble, BitChute |
| **Plus** | **1000+ additional sites** – See [yt-dlp docs](https://github.com/yt-dlp/yt-dlp#supported-sites) |

📌 YouTube includes **PO token support** for 2026+ bot detection bypasses

## ⚙️ Requirements

### 📦 System Dependencies
| Requirement | Purpose | Status |
|-------------|---------|--------|
| **Python 3.10+** | Application runtime | Required |
| **FFmpeg** | Audio/video processing | Required |
| **Deno** or **Node.js 25+** | YouTube PO token generation | Recommended (YouTube downloads) |

### 🐍 Python Packages
All automatically installed via `requirements.txt`:
- `PyQt5 == 5.15.11` – GUI framework
- `yt-dlp == 2026.3.17` – Video downloading
- `Pillow == 12.2.0` – Image handling

## 🚀 Installation

### 📦 AppImage (Recommended - No Installation Required!)

**Download, make executable, and run:**

```bash
# Download the latest AppImage
wget https://github.com/asafelobotomy/AV-Morning-Star/releases/download/v0.3.0/AV-Morning-Star-0.3.0-x86_64.AppImage

# Make it executable
chmod +x AV-Morning-Star-0.3.0-x86_64.AppImage

# Run it!
./AV-Morning-Star-0.3.0-x86_64.AppImage
```

**✨ Benefits:**
- ✅ **No installation required** - Just download and run
- ✅ **Self-contained** - Includes all dependencies (69 MB)
- ✅ **Universal** - Works on any Linux distribution (glibc 2.6.32+)
- ✅ **No conflicts** - Doesn't interfere with system packages
- ✅ **Desktop integration** - Adds to application menu automatically

**Requirements:** FFmpeg (for audio/video processing) and optionally Deno (for YouTube).

---

### ⚡ Quick Start (From Source)

```bash
# Clone the repository
git clone https://github.com/asafelobotomy/AV-Morning-Star.git
cd AV-Morning-Star

# Run the auto-setup script
chmod +x start.sh
./start.sh
```

**The `start.sh` script handles:**
- ✅ Virtual environment creation
- ✅ Python dependency installation
- ✅ FFmpeg availability check
- ✅ Checks whether a JavaScript runtime is available and prints installation guidance if not found (optional, for YouTube)
- ✅ Application launch

### 📋 Manual Installation

#### 1️⃣ Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg
```

**Fedora/RHEL:**
```bash
sudo dnf install -y python3 python3-venv ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S python ffmpeg
```

**macOS:**
```bash
brew install python@3.11 ffmpeg
```

#### 2️⃣ Setup Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3️⃣ Install Deno (Optional, for YouTube)

Install via your package manager or see the **[official installation guide](https://docs.deno.com/runtime/getting_started/installation/)**:

```bash
# Linux (snap)
snap install deno

# Linux (cargo)
cargo install deno

# macOS (Homebrew)
brew install deno
```

**Alternatives to Deno:**
- Node.js 25+ – See [nodejs.org](https://nodejs.org/)
- Bun – See [bun.sh](https://bun.sh/)
- QuickJS – `sudo apt install quickjs`

After installing, verify with `deno --version`.

#### 4️⃣ Launch Application

```bash
python3 main.py
```

### 📦 Build AppImage (Optional)

Create a portable, standalone executable:

```bash
chmod +x scripts/build-appimage.sh
./scripts/build-appimage.sh
```

**Output:** `AV-Morning-Star-0.3.0-x86_64.AppImage` (69 MB)

**Build includes:**
- ✅ All Python dependencies bundled
- ✅ PyQt5 GUI framework
- ✅ yt-dlp with 1000+ site extractors
- ✅ Desktop integration files
- ✅ Application icon (.DirIcon symlink)
- ✅ Squashfs 4.0 with gzip compression (98.94% efficiency)

Share this single file with others – no installation needed!

## 📖 Usage

### 🎬 Basic Workflow

```
1. Launch App         → ./start.sh  or  python3 main.py
2. Configure Auth     → Tools > Preferences (keep "Auto" default)
3. Paste URL          → YouTube, Odysee, etc.
4. Fetch Metadata     → Click "Fetch" button
5. Select Videos      → Check desired videos from list
6. Choose Settings    → Quality, format, mode
7. Download           → Click "Download Selected"
```

### ⚙️ Mode Selection

#### **Basic Mode** (Default - Recommended)
- ✅ Auto-detects best quality
- ✅ Auto-configures audio settings
- ✅ Perfect for 90% of users
- ✅ No technical knowledge required

#### **Advanced Mode**
- Manual video quality selection (4K down to 360p)
- Audio codec choice (MP3, AAC, FLAC, Opus, M4A, WAV, ALAC)
- Bitrate selection (96-320 kbps or lossless)
- Audio enhancements:
  - 🎚️ EBU R128 loudness normalization
  - 🔊 Dynamic normalization
  - 🔇 FFT-based noise reduction
  - 🖼️ Thumbnail embedding
- Video enhancements (for MP4/MKV/WebM/MOV):
  - 🎬 Video denoising
  - 🤳 Stabilization (reduce camera shake)
  - ✨ Sharpening
  - 🔊 Audio processing (normalization/denoising)

### 📝 Filename Templates

Customize output filenames by clicking tags to add or remove them:

| Tag | Example | Use Case |
|-----|---------|----------|
| **Title** | "Amazing Video" | Video name |
| **Uploader** | "Channel Name" | Creator/channel |
| **Quality** | "1080p" | Video resolution |
| **Format** | "mp4" | File format |
| **Website** | "YouTube" | Platform name |
| **ID** | "dQw4w9WgXcQ" | Unique video ID |
| **Upload Date** | "20260203" | Original upload date |
| **Timestamp** | "1749000000" | Unix epoch at download time |
| **Duration** | "03:45:20" | Video length |
| **Extension** | "mp4" | Auto file extension |

**Example:** Drag **Title**, **Uploader**, **Date** → `"Amazing Video - Channel Name - 20260203.mp4"`

### 🔐 YouTube Authentication

#### How It Works
1. **Default "Auto" mode** – Intelligent browser selection
2. **Tries cookieless first** – No authentication needed
3. **YouTube blocks it?** – Auto-detects your browser
4. **Prompts for confirmation** – "Retry with Firefox?"
5. **Uses your login session** – You stay logged in

#### Supported Browsers
✅ Firefox (recommended)
✅ Chrome / Chromium
✅ Brave
✅ Edge
✅ Opera
✅ Vivaldi

#### Troubleshooting YouTube Issues
| Problem | Solution |
|---------|----------|
| "Sign in to confirm" error | Make sure you're logged into YouTube in your browser |
| "Browser cookies not found" | Switch to "Auto" mode in Preferences |
| Repeated "Bot detected" | Wait 15 minutes or try different video |
| Specific browser fails | Use "Auto" mode to try another browser |

⏱️ **Pro Tip:** Keep "Auto (Recommended)" selected – it finds the best browser automatically

## 🏗️ Architecture

### 🔧 Modular Extractor System

```
extractors/
├── __init__.py          # Factory function (get_extractor)
├── base.py              # BaseExtractor (common interface)
├── youtube_ytdlp.py     # YouTube with PO token support
├── odysee.py            # Odysee/LBRY platform
└── generic.py           # Fallback for 1000+ other sites
```

**How It Works:**
1. User provides URL
2. Factory function identifies platform
3. Selects appropriate extractor class
4. Extracts metadata via `extract_info()`
5. Returns standardized format

**Easy to Extend:** Add new platform? Create extractor, inherit from `BaseExtractor`, register in factory. ✨

### 🧵 Threading Model

```
┌─────────────────────────┐
│   Main GUI Thread       │
│  (PyQt5 Event Loop)     │
└────────┬────────────────┘
         │
    ┌────┴─────┬──────────────┐
    │           │              │
    ▼           ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│ Scraper│ │ Download │ │  UI      │
│ Thread │ │  Thread  │ │ Updates  │
│        │ │          │ │ (signals)│
└────────┘ └──────────┘ └──────────┘
```

- **Main Thread** – GUI updates, user interaction
- **Scraper Thread** – Metadata extraction (non-blocking)
- **Download Thread** – File downloads with progress (non-blocking)
- **Communication** – PyQt signals/slots (thread-safe)

## 🔒 Security & Privacy

### 🛡️ Cookie Security

| Feature | Status | Benefit |
|---------|--------|---------|
| **Read-only access** | ✅ | Cannot modify browser data |
| **Memory-only storage** | ✅ | Cookies never written to disk |
| **OS keyring encryption** | ✅ | Protected by system encryption |
| **HTTPS-only** | ✅ | Encrypted connections only |
| **User consent** | ✅ | Must approve before use |
| **Auto cleanup** | ✅ | Destroyed when app closes |

### 🔐 Privacy-First Approach

- **Cookieless by Default** – Authenticates only when YouTube requires it
- **Smart Detection** – Only scans browsers when needed (not on startup)
- **No Tracking** – Zero analytics, no telemetry, no data collection
- **Local Processing** – All operations happen on your computer
- **Open Source** – Inspect the code yourself

### 📋 For Technical Details

See [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) for a comprehensive security review including:
- Cookie handling mechanisms
- Browser database encryption
- Network security
- Data flow analysis

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
- **[Build Summary](docs/BUILD_SUMMARY.md)**: v0.3.0 AppImage build manifest
- **[Extractor Coverage](docs/EXTRACTORS_COVERAGE_ANALYSIS.md)**: Platform support analysis
- **[Security Audit](docs/SECURITY_AUDIT.md)**: Comprehensive technical security review

### Quick Links
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
- **[Latest Release](https://github.com/asafelobotomy/AV-Morning-Star/releases/latest)**: Download AppImage
- **[Documentation Index](docs/README.md)**: Full documentation guide
- **[Archive](archive/)**: Historical development documentation

## ❓ Troubleshooting

### YouTube Issues

#### "Sign in to confirm you're not a bot"
**✓ Solution:**
1. Open YouTube in your default browser and log in
2. Tools > Preferences → Select "Auto (Recommended)"
3. Retry the download

#### "FFmpeg not found"
**✓ Solution:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg

# macOS
brew install ffmpeg
```

#### "No JavaScript runtime found"
**✓ Solution:** Install Deno via your package manager or see the [official installation guide](https://docs.deno.com/runtime/getting_started/installation/).

```bash
# Linux (snap)
snap install deno
# macOS
brew install deno
```

#### Repeated "Bot detected" errors
**✓ Solution:**
- Wait 15-30 minutes (YouTube rate limiting)
- Try a different YouTube video
- Ensure you're logged into YouTube in your browser

### Browser Issues

#### "Browser cookies not found" / "Permission denied"
**✓ Solution:**
1. Close your web browser (some lock cookie files)
2. Switch to "Auto (Recommended)" mode
3. Retry

#### Specific browser authentication fails
**✓ Solution:**
- Make sure browser is installed and accessible
- Sign into YouTube in that browser
- Use "Auto" mode to switch browsers automatically

### Installation Issues

#### "Python 3 not found"
**✓ Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3

# macOS (requires Homebrew)
brew install python@3.11
```

#### "PyQt5 installation fails"
**✓ Solution:**
```bash
# Install system libraries first
sudo apt install python3-dev  # Ubuntu/Debian

# Then reinstall
pip install --upgrade PyQt5
```

#### "pip command not found"
**✓ Solution:**
```bash
python3 -m pip install -r requirements.txt
```

### Download Issues

#### Download stuck or very slow
**✓ Solution:**
- Check your internet connection
- Try a different video
- Increase quality setting might help
- Restart the application

#### "Requested format not available"
**✓ Solution:**
- Some videos have limited formats available
- Try a different quality setting
- Video might be private/restricted

Need more help? Check [Full Documentation](docs/README.md)

## 🤝 Contributing

Want to add support for a new platform? It's easy with our modular architecture!

### 📋 Add New Platform in 4 Steps:

1. **Create extractor file** – `extractors/yourplatform.py`
   ```python
   from .base import BaseExtractor

   class YourPlatformExtractor(BaseExtractor):
       def extract_info(self):
           # Return list of videos with title, url, duration, uploader
           pass

       def get_download_opts(self, ...):
           # Return yt-dlp options for downloading
           pass
   ```

2. **Inherit from BaseExtractor** – Get common functionality for free

3. **Register in factory** – `extractors/__init__.py`
   ```python
   def get_extractor(url, cookies_from_browser=None):
       if 'yourplatform.com' in url.lower():
           return YourPlatformExtractor(url)
       # ... rest of function
   ```

4. **Test it** – No changes to main.py needed!

📖 **Full guide:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 📚 Documentation

### 📖 User Guides
- **[Getting Started](docs/GETTING_STARTED.md)** – Step-by-step tutorial
- **[YouTube Authentication](docs/AUTHENTICATION_GUIDE.md)** – Cookie authentication explained
- **[Security & Privacy](docs/SECURITY_AND_PRIVACY.md)** – User-friendly security guide
- **[Smart Browser Detection](docs/SMART_BROWSER_DETECTION.md)** – Auto-detection feature

### 🔧 Technical Documentation
- **[Architecture](docs/ARCHITECTURE.md)** – Modular system design
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** – Complete file organization
- **[Security Audit](docs/SECURITY_AUDIT.md)** – Technical security review
- **[Code Review (historical)](archive/legacy/reports/CODE_REVIEW_REPORT.md)** – Code quality analysis

### 📋 Project Resources
- **[CHANGELOG.md](CHANGELOG.md)** – Version history and updates
- **[Latest Release](https://github.com/asafelobotomy/AV-Morning-Star/releases/latest)** – Download AppImage
- **[Build Summary](docs/BUILD_SUMMARY.md)** – v0.3.0 build documentation
- **[Archive](archive/)** – Historical development notes
- **[Full Documentation Index](docs/README.md)** – Everything in one place

## 📄 License & Credits

### License
This project is **open source** and available for personal and educational use.
See [LICENSE](LICENSE) file for full details.

### Built With ❤️ By
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** – Powerful video downloading engine
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)** – Excellent GUI framework
- **[FFmpeg](https://ffmpeg.org/)** – Media processing capabilities
- **[Deno](https://deno.land/)** – JavaScript runtime for YouTube PO tokens

## ⚠️ Disclaimer

This tool is for **personal use only**. Please respect:
- ✅ Copyright laws in your jurisdiction
- ✅ Website terms of service
- ✅ Creator permissions and licenses

The developers are **not responsible** for misuse of this software.

---

## 📞 Support

### Getting Help
- **📖 Documentation** – Check [docs/](docs/) folder first
- **🐛 Report Issues** – Use GitHub Issues with details
- **🔒 Security** – See [Security Guide](docs/SECURITY_AND_PRIVACY.md)

### Quick Links
- 🌐 Repository – [github.com/asafelobotomy/AV-Morning-Star](https://github.com/asafelobotomy/AV-Morning-Star)
- 📜 Changelog – [CHANGELOG.md](CHANGELOG.md)
- 🏗️ Architecture – [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

<div align="center">

**AV Morning Star v0.3.0**

Built with 🎥 for video enthusiasts
Maintained with ❤️ by the community

*Privacy-first • Open-source • Easy-to-use*

</div>
