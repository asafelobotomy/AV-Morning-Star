# AV Morning Star - Media Downloader

A powerful PyQt5-based application for downloading videos and audio from various websites. Supports both single video downloads and batch downloads from playlists/channels.

## Features

✨ **Key Features:**
- 🎥 Download videos in multiple quality options (Best, 1080p, 720p, 480p)
- 🎵 Extract audio-only in MP3 format
- 📋 Support for playlists and channel URLs
- ☑️ Select multiple videos via checkboxes
- 📊 Real-time download progress tracking
- 🎯 User-friendly GUI interface
- 📦 Packaged as AppImage for easy distribution

## Supported Sites

Thanks to `yt-dlp`, this application supports downloading from:
- YouTube (videos, playlists, channels)
- Vimeo
- Twitter/X
- Facebook
- Instagram
- TikTok
- And 1000+ other sites!

## Requirements

- Python 3.7+
- PyQt5
- yt-dlp
- requests
- beautifulsoup4
- FFmpeg (for audio extraction and video merging)

## Installation

### Method 1: Run from Source

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure FFmpeg is installed:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

4. Run the application:
```bash
python3 main.py
```

### Method 2: Build AppImage

1. Make the build script executable:
```bash
chmod +x build-appimage.sh
```

2. Run the build script:
```bash
./build-appimage.sh
```

3. Run the generated AppImage:
```bash
./AV-Morning-Star-1.0.0-x86_64.AppImage
```

## Usage

1. **Enter URL**: Paste a video URL or playlist/channel URL in the input field
2. **Fetch Videos**: Click "Fetch" to retrieve available videos
3. **Select Videos**: Use checkboxes to select which videos to download
4. **Choose Format**: 
   - Select "Video" or "Audio Only"
   - For videos, choose quality (Best, 1080p, 720p, 480p)
5. **Set Output Path**: Click "Browse" to choose where to save downloads
6. **Download**: Click "Download Selected" to start the process

## How It Works

### Single Video Download
When you paste a URL containing a single video, the app will:
1. Detect it as a single video
2. Display its title, uploader, and duration
3. Allow you to download it in your chosen format/quality

### Multiple Videos (Playlist/Channel)
When you paste a playlist or channel URL, the app will:
1. Scrape all video URLs from the page
2. Display each video with its metadata
3. Show checkboxes for each video
4. Allow you to select which videos to download
5. Download all selected videos sequentially

## Architecture

The application uses:
- **PyQt5**: For the graphical user interface
- **yt-dlp**: For video/audio downloading and metadata extraction
- **Threading**: For non-blocking UI during downloads and scraping
- **BeautifulSoup**: For additional web scraping capabilities

### Components

- `URLScraperThread`: Handles URL fetching and metadata extraction
- `DownloadThread`: Manages the download process with progress tracking
- `MediaDownloaderApp`: Main GUI application class

## Building the AppImage

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
