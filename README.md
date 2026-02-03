# 🌟 AV Morning Star - Video & Audio Downloader

> A powerful, privacy-first desktop application for downloading videos and audio from 1000+ websites.

**Version 0.3.0** | Built with PyQt5 & yt-dlp | [📖 Full Documentation](docs/README.md)

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
- **📝 Filename Customization** – Drag-and-drop template tags (title, uploader, date, duration, etc.)
- **📑 Subtitle Handling** – Download and embed subtitles automatically
- **⚡ Real-time Progress** – Live download tracking with filename and percentage
- **🔒 Privacy-First** – Cookieless by default, authenticated only when needed

### 🧠 Smart Browser Detection (New in v0.3.0!)
- **🤖 Auto Mode** – Intelligently finds the best browser with YouTube authentication
- **🔍 Browser Support** – Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi
- **🛡️ Secure by Design** – Read-only access, in-memory storage, OS keyring encryption
- **💬 User-Friendly** – Plain-English errors with actionable solutions

## 🌐 Supported Platforms

Powered by **yt-dlp (2026.1.31+)** with support for:

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
| **Python 3.7+** | Application runtime | Required |
| **FFmpeg** | Audio/video processing | Required |
| **Deno** or **Node.js 25+** | YouTube PO token generation | Recommended (YouTube downloads) |

### 🐍 Python Packages
All automatically installed via `requirements.txt`:
- `PyQt5 >= 5.15.0` – GUI framework
- `yt-dlp >= 2026.1.31` – Video downloading
- `requests >= 2.28.0` – HTTP client
- `beautifulsoup4 >= 4.11.0` – HTML parsing
- `Pillow >= 10.0.0` – Image handling

## 🚀 Installation

### ⚡ Quick Start (Recommended)

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
- ✅ Deno installation (optional, for YouTube)
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

```bash
# Install Deno
curl -fsSL https://deno.land/install.sh | sh

# Add to PATH
echo 'export DENO_INSTALL="$HOME/.deno"' >> ~/.bashrc
echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
deno --version
```

**Alternatives to Deno:**
- Node.js 25+ – See [nodejs.org](https://nodejs.org/)
- Bun – See [bun.sh](https://bun.sh/)
- QuickJS – `sudo apt install quickjs`

#### 4️⃣ Launch Application

```bash
python3 main.py
```

### 📦 Build AppImage (Optional)

Create a portable, standalone executable:

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

Output: `AV-Morning-Star-0.3.0-x86_64.AppImage`

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
- Video enhancements (for MP4/MKV/WebM):
  - 🎬 Video denoising
  - 🤳 Stabilization (reduce camera shake)
  - ✨ Sharpening
  - 🔊 Audio processing (normalization/denoising)

### 📝 Filename Templates

Customize output filenames with drag-and-drop tags:

| Tag | Example | Use Case |
|-----|---------|----------|
| **Title** | "Amazing Video" | Video name |
| **Uploader** | "Channel Name" | Creator/channel |
| **Quality** | "1080p" | Video resolution |
| **Format** | "mp4" | File format |
| **Website** | "YouTube" | Platform name |
| **ID** | "dQw4w9WgXcQ" | Unique video ID |
| **Upload Date** | "20260203" | Original upload date |
| **Download Date** | "20260203" | When downloaded |
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
✅ Safari (macOS)

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
- **[Security Audit](docs/SECURITY_AUDIT.md)**: Comprehensive technical security review
- **[Reorganization](docs/REORGANIZATION.md)**: v0.3.0 reorganization details

### Quick Links
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
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
**✓ Solution:** Install Deno
```bash
curl -fsSL https://deno.land/install.sh | sh
source ~/.bashrc
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
- **[Code Review](CODE_REVIEW_REPORT.md)** – Code quality analysis

### 📋 Project Resources
- **[CHANGELOG.md](CHANGELOG.md)** – Version history and updates
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
