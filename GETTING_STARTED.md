# AV Morning Star - Getting Started Guide

## 📋 Quick Overview

AV Morning Star is a desktop application that allows you to:
- Download videos from YouTube, Vimeo, and 1000+ other sites
- Extract audio from videos in MP3 format
- Download entire playlists or channels with checkbox selection
- Choose video quality (Best, 1080p, 720p, 480p)
- Track download progress in real-time

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip ffmpeg
```

### Step 2: Run the Application

Simply execute:
```bash
./start.sh
```

This script will:
- Create a virtual environment
- Install all Python dependencies
- Launch the application

### Step 3: Use the App

1. Paste a video or playlist URL
2. Click "Fetch" to load videos
3. Select videos you want to download
4. Choose format (Video/Audio) and quality
5. Click "Download Selected"

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

## 📦 Building AppImage

To create a portable AppImage:

```bash
./build-appimage.sh
```

This will create `AV-Morning-Star-1.0.0-x86_64.AppImage` which you can:
- Run on any Linux distribution
- Share with others
- Run without installation

After building, run it with:
```bash
./AV-Morning-Star-1.0.0-x86_64.AppImage
```

## 🎯 Usage Examples

### Example 1: Download Single Video
```
1. Paste: https://www.youtube.com/watch?v=dQw4w9WgXcQ
2. Click "Fetch"
3. Video appears with checkbox (auto-checked)
4. Select quality: "1080p"
5. Click "Download Selected"
```

### Example 2: Download Playlist
```
1. Paste: https://www.youtube.com/playlist?list=PLxxxxxx
2. Click "Fetch"
3. All videos appear with checkboxes
4. Uncheck videos you don't want
5. Click "Download Selected"
```

### Example 3: Extract Audio from Channel
```
1. Paste: https://www.youtube.com/@channelname/videos
2. Click "Fetch"
3. Select videos you want
4. Change format to "Audio Only"
5. Click "Download Selected"
```

## 🔍 Testing Your Setup

Run the test script to verify everything is working:
```bash
./test.sh
```

This will check:
- Python version and imports
- FFmpeg installation
- yt-dlp functionality

## 📁 Project Structure

```
AV Morning Star/
├── main.py                    # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── GETTING_STARTED.md         # This file
├── start.sh                   # Quick start script
├── build-appimage.sh          # AppImage build script
├── test.sh                    # Test script
├── create_icon.py             # Icon generator
├── av-morning-star.desktop    # Desktop entry
└── .gitignore                 # Git ignore file
```

## ⚙️ Configuration

### Change Download Location
Click the "Browse" button in the app to select a different download folder.
Default: `~/Downloads`

### Video Quality Options
- **Best**: Highest quality available
- **1080p**: Full HD
- **720p**: HD
- **480p**: Standard definition

### Audio Format
Audio is extracted as MP3 at 192 kbps quality.

## 🐛 Troubleshooting

### "FFmpeg not found"
Install FFmpeg:
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
```

### "Import Error: No module named PyQt5"
Activate the virtual environment and install dependencies:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Download failed" or "HTTP Error 403"
- Check your internet connection
- The video may be restricted or private
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Application won't start
Run the test script to diagnose:
```bash
./test.sh
```

## 🌐 Supported Websites

This application supports downloading from:
- **YouTube**: Videos, playlists, channels, shorts
- **Vimeo**: Videos and channels
- **Twitter/X**: Video posts
- **Facebook**: Videos
- **Instagram**: Videos and reels
- **TikTok**: Videos
- **Twitch**: VODs and clips
- **Reddit**: Video posts
- **And 1000+ other sites!**

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 💡 Tips & Tricks

1. **Batch Downloads**: Select multiple videos and they'll download one after another
2. **Playlist Subsets**: You don't have to download entire playlists - just select what you want
3. **Audio Extraction**: Use "Audio Only" mode to get MP3 files instead of videos
4. **Quality Selection**: Choose lower quality for faster downloads or to save space
5. **Monitor Progress**: The progress bar shows real-time download status

## 🔄 Updating

To update the application:

```bash
source .venv/bin/activate
pip install --upgrade yt-dlp
```

yt-dlp is frequently updated to support site changes.

## 📝 Notes

- Downloads are performed sequentially (one at a time)
- Large playlists may take time to fetch all video information
- Some sites may have download restrictions or require authentication
- Respect copyright and terms of service of websites

## 🆘 Getting Help

If you encounter issues:
1. Run `./test.sh` to diagnose problems
2. Check FFmpeg is installed: `ffmpeg -version`
3. Try updating yt-dlp: `pip install --upgrade yt-dlp`
4. Check the video/playlist is publicly accessible

## ⚖️ Legal Disclaimer

This tool is for personal use only. Always respect:
- Copyright laws
- Website terms of service
- Content creator rights
- Local regulations

The developers are not responsible for any misuse of this software.

---

**Enjoy using AV Morning Star! 🌟**
