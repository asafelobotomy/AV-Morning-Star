Production-ready PyQt5 media downloader with cross-distribution Linux support.

## 🎉 First Official Release!

AV Morning Star v0.3.0 introduces professional-grade AppImage packaging, making it easy to run on any Linux distribution without installation.

## ✨ Key Features

### Platform Support
- **YouTube** - Full support with PO token authentication & browser cookies
- **Odysee/LBRY** - Dedicated extractor for decentralized platforms
- **1000+ Sites** - Universal support via yt-dlp backend (Vimeo, Twitch, TikTok, etc.)

### Download Options
- **Dual Mode Interface** - Basic (auto-config) or Advanced (manual settings)
- **Video Quality** - 360p to 4K, multiple container formats (MP4, MKV, WebM, MOV, AVI, FLV)
- **Audio Extraction** - MP3, AAC, FLAC, WAV, ALAC, Opus, OGG Vorbis
- **Subtitle Support** - Automatic download and embedding

### Professional Audio Processing
- **EBU R128 Normalization** - Broadcast-standard loudness (-16 LUFS)
- **Dynamic Normalization** - Adaptive volume leveling for varying content
- **Noise Reduction** - FFT-based denoising with adaptive tracking
- **Thumbnail Embedding** - Album art support for audio files

### Video Enhancement
- **Denoise** - 3D temporal denoising (hqdn3d) for grainy footage
- **Stabilize** - Camera shake reduction (deshake filter)
- **Sharpen** - Unsharp mask with edge-aware settings
- **Audio Processing** - Normalization & denoising for video audio tracks

### Smart Features
- **Browser Cookie Auto-Detection** - Automatic authentication via Firefox/Chrome/Brave/Edge
- **Filename Templating** - Customizable output naming with drag-and-drop tags
- **Batch Downloads** - Multi-video selection from playlists/channels
- **Live Progress Tracking** - Real-time download status

## 📦 Installation

### AppImage (Recommended)
```bash
# Download the AppImage
wget https://github.com/asafelobotomy/AV-Morning-Star/releases/download/v0.3.0/AV-Morning-Star-0.3.0-x86_64.AppImage

# Make executable
chmod +x AV-Morning-Star-0.3.0-x86_64.AppImage

# Run!
./AV-Morning-Star-0.3.0-x86_64.AppImage
```

**No installation required!** Works on any Linux distribution with glibc 2.6.32+ (Ubuntu 20.04+, Fedora 32+, Arch, etc.)

### From Source
```bash
git clone https://github.com/asafelobotomy/AV-Morning-Star.git
cd AV-Morning-Star
./start.sh
```

## 📋 System Requirements

### Minimum
- **OS:** Any Linux with glibc 2.6.32+
- **RAM:** 512 MB
- **Disk:** 200 MB free space
- **Architecture:** x86-64

### Optional Dependencies
- **FFmpeg** - Audio extraction & video processing (highly recommended)
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # Fedora
  sudo dnf install ffmpeg
  
  # Arch
  sudo pacman -S ffmpeg
  ```

- **Deno/Node.js 25+** - YouTube Proof of Origin tokens (recommended for YouTube)
  ```bash
  # Deno (recommended)
  curl -fsSL https://deno.land/install.sh | sh
  ```

## 📊 Build Information

- **Size:** 69 MB (self-contained, includes all dependencies)
- **Compression:** Squashfs 4.0 with gzip (98.94% efficiency)
- **Python:** 3.14.2
- **PyQt5:** 5.15.11
- **yt-dlp:** 2026.2.4 (latest)
- **Build Tool:** PyInstaller 6.18.0 + appimagetool

## 🔐 Checksums

**SHA256:** `9122d034a1c16c71cc4df40ce0f013c4a28d65ef7b0e86a7ec5c7338406b3f2c`  
**MD5:** `b81254a708eeb3ecd05c0aaf5c1f3bd7`

Download checksum files below to verify integrity.

## 📚 Documentation

- [README.md](https://github.com/asafelobotomy/AV-Morning-Star/blob/main/README.md) - Quick start guide
- [AUTHENTICATION_GUIDE.md](https://github.com/asafelobotomy/AV-Morning-Star/blob/main/docs/AUTHENTICATION_GUIDE.md) - YouTube login setup
- [BUILD_SUMMARY.md](https://github.com/asafelobotomy/AV-Morning-Star/blob/main/BUILD_SUMMARY.md) - Complete build manifest
- [ARCHITECTURE.md](https://github.com/asafelobotomy/AV-Morning-Star/blob/main/docs/ARCHITECTURE.md) - Code structure

## 🐛 Known Issues

- **YouTube:** Requires browser login for some videos (bot detection) - See authentication guide
- **File Manager Icon:** May need cache clearing after first download - `rm -rf ~/.cache/thumbnails/large/*`

## 🙏 Credits

Built with:
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) - GUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download engine
- [PyInstaller](https://pyinstaller.org/) - Executable packaging
- [AppImageKit](https://github.com/AppImage/AppImageKit) - Linux distribution

## 📄 License

MIT License - See [LICENSE](https://github.com/asafelobotomy/AV-Morning-Star/blob/main/LICENSE) for details

---

**Full Changelog:** https://github.com/asafelobotomy/AV-Morning-Star/blob/main/CHANGELOG.md
