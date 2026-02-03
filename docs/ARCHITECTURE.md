# AV Morning Star - Architecture Documentation

## Overview

AV Morning Star uses a **modular extractor architecture** that separates platform-specific download logic from the main application. This makes it easy to add custom handling for different video platforms.

## Architecture Components

### 1. Main Application (`main.py`)
- **URLScraperThread**: Fetches video metadata using platform extractors
- **DownloadThread**: Downloads videos/audio using platform extractors  
- **MediaDownloaderApp**: PyQt5 GUI with all UI components

### 2. Extractor System (`extractors/`)

#### Base Extractor (`extractors/base.py`)
The foundation class that all platform extractors inherit from:

```python
class BaseExtractor:
    def extract_info(self) -> list
    def get_download_opts(...) -> dict
    def get_fetch_opts() -> dict
```

**Key Methods:**
- `extract_info()` - Fetches video metadata without downloading
- `get_download_opts()` - Returns yt-dlp options for downloading
- `get_fetch_opts()` - Returns yt-dlp options for metadata extraction
- `_get_video_opts()` - Configures video quality settings
- `_get_audio_opts()` - Configures audio extraction with filters

#### Platform-Specific Extractors

**YouTube Extractor** (`extractors/youtube.py`)
- Cookie-based authentication from browsers (Firefox by default)
- Age-gate bypassing
- DASH/HLS manifest support
- Parallel fragment downloads

**Odysee Extractor** (`extractors/odysee.py`)
- Basic Odysee/LBRY support
- No special authentication needed
- Inherits standard options from BaseExtractor

**Generic Extractor** (`extractors/generic.py`)
- Fallback for all other platforms
- Works with any yt-dlp-supported site
- Standard security settings

#### Extractor Factory (`extractors/__init__.py`)

The `get_extractor(url)` function automatically selects the right extractor:

```python
from extractors import get_extractor

extractor = get_extractor("https://youtube.com/watch?v=...")
# Returns YouTubeExtractor instance

extractor = get_extractor("https://odysee.com/@channel/video")
# Returns OdyseeExtractor instance

extractor = get_extractor("https://vimeo.com/12345")
# Returns GenericExtractor instance
```

## How It Works

### Fetching Videos

```
User enters URL
    ↓
URLScraperThread created
    ↓
get_extractor(url) → Returns appropriate extractor
    ↓
extractor.extract_info() → Fetches metadata
    ↓
Returns list of videos with: url, title, duration, uploader
```

### Downloading Videos

```
User clicks Download
    ↓
DownloadThread created with URLs
    ↓
For each URL:
    get_extractor(url) → Returns appropriate extractor
    ↓
    extractor.get_download_opts() → Platform-specific yt-dlp options
    ↓
    yt_dlp.YoutubeDL(opts).download([url])
```

## Adding a New Platform

To add support for a new platform (e.g., Twitch):

### 1. Create Platform Extractor

Create `extractors/twitch.py`:

```python
from .base import BaseExtractor

class TwitchExtractor(BaseExtractor):
    def __init__(self, url):
        super().__init__(url)
        self.platform_name = "Twitch"
    
    def get_fetch_opts(self):
        opts = super().get_fetch_opts()
        # Add Twitch-specific options
        opts['twitch_api_key'] = 'your_key_here'
        return opts
    
    def get_download_opts(self, output_path, filename_template, ...):
        opts = super().get_download_opts(...)
        # Add Twitch-specific download options
        opts['twitch_api_key'] = 'your_key_here'
        return opts
```

### 2. Register in Factory

Edit `extractors/__init__.py`:

```python
from .twitch import TwitchExtractor

def get_extractor(url):
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return YouTubeExtractor(url)
    elif 'odysee.com' in url_lower or 'lbry.tv' in url_lower:
        return OdyseeExtractor(url)
    elif 'twitch.tv' in url_lower:  # Add this
        return TwitchExtractor(url)
    else:
        return GenericExtractor(url)
```

### 3. Test

No changes needed to `main.py` - the extractor system handles everything!

## Platform-Specific Features

### YouTube
- **Cookie Authentication**: Bypasses bot detection by using browser cookies
- **Browser Selection**: Defaults to Firefox, can be changed:
  ```python
  extractor = YouTubeExtractor(url, browser='chrome')
  ```
- **DASH/HLS**: Full support for adaptive streaming formats
- **Parallel Downloads**: 4 concurrent fragment downloads

### Odysee
- **Direct Access**: No authentication needed
- **LBRY Protocol**: Supports both odysee.com and lbry.tv URLs

### Generic Fallback
- **Universal Support**: Works with 1000+ sites via yt-dlp
- **Secure**: SSL certificate verification enabled
- **HTTPS Preferred**: Uses secure connections when available

## Audio Processing Pipeline

All extractors support advanced audio processing:

1. **Extraction**: Convert to MP3/AAC/FLAC/Opus/M4A
2. **Denoising** (optional): FFT-based noise reduction
3. **Normalization** (optional):
   - EBU R128: Professional loudness normalization to -16 LUFS
   - Dynamic: Better for varying volume levels
4. **Thumbnail Embedding**: Add artwork to audio files
5. **Metadata**: Preserve title, artist, album info

## Video Quality Selection

Quality presets are handled by `BaseExtractor._get_video_opts()`:

- **Best**: Highest available quality
- **4K (2160p)**: UHD video
- **1440p**: QHD video
- **1080p**: Full HD
- **720p**: HD
- **480p**: SD
- **360p**: Low quality

Each preset selects the best video+audio combination for that resolution.

## Extension Points

### Custom Filename Templates
The extractor system passes filename templates directly to yt-dlp:
```python
extractor.get_download_opts(
    output_path='/downloads',
    filename_template='%(title)s - %(uploader)s - %(height)sp.%(ext)s',
    ...
)
```

### Progress Hooks
DownloadThread adds progress hooks after getting extractor options:
```python
ydl_opts = extractor.get_download_opts(...)
ydl_opts['progress_hooks'] = [self.progress_hook]
```

### Custom Postprocessors
Override `_get_audio_opts()` to add custom FFmpeg filters:
```python
def _get_audio_opts(self, ...):
    opts = super()._get_audio_opts(...)
    # Add custom filter
    if 'postprocessor_args' not in opts:
        opts['postprocessor_args'] = {'ffmpeg': []}
    opts['postprocessor_args']['ffmpeg'].extend(['-filter:a', 'your_filter'])
    return opts
```

## Benefits of Modular Architecture

1. **Platform Isolation**: Each platform has its own class
2. **Easy Maintenance**: Fix YouTube issues without touching Odysee code
3. **Extensibility**: Add new platforms without modifying existing code
4. **Testing**: Test each platform extractor independently
5. **Clean Code**: Main app logic separated from platform details
6. **Reusability**: Extractors can be used in other projects

## Future Enhancements

Potential improvements to the extractor system:

- **Browser Selector UI**: Let users choose which browser to extract cookies from
- **Platform Detection**: Auto-detect platform from URL and show platform-specific options
- **Credential Storage**: Secure storage for API keys and passwords
- **Rate Limiting**: Platform-specific download rate controls
- **Quality Presets**: Platform-optimized quality profiles
- **Batch Processing**: Download entire channels with platform-specific logic
- **Error Recovery**: Platform-specific retry strategies

## Troubleshooting

### YouTube "Sign in to confirm you're not a bot"
**Solution**: Install the browser extension and log into YouTube in that browser. The extractor will use your session cookies.

### Odysee videos not loading
**Solution**: Update yt-dlp: `pip install --upgrade yt-dlp`

### Generic extractor failing on specific site
**Solution**: Create a platform-specific extractor for that site with custom options.

## Dependencies

- **yt-dlp**: Core download engine (must be up-to-date)
- **FFmpeg**: Required for audio extraction and video merging
- **Browser**: Must be installed for YouTube cookie extraction

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              MediaDownloaderApp                 │
│                  (main.py)                      │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼─────────┐
│ URLScraperThread│    │  DownloadThread  │
└───────┬────────┘    └────────┬─────────┘
        │                       │
        │   get_extractor(url)  │
        └───────────┬───────────┘
                    │
        ┌───────────▼────────────┐
        │  Extractor Factory     │
        │  (extractors/__init__) │
        └───────────┬────────────┘
                    │
        ┌───────────┴───────────────┐
        │                           │
┌───────▼─────┐ ┌────────▼────────┐ ┌──────▼──────┐
│   YouTube   │ │     Odysee      │ │   Generic   │
│  Extractor  │ │    Extractor    │ │  Extractor  │
└─────┬───────┘ └────────┬────────┘ └──────┬──────┘
      │                  │                  │
      └──────────────────┴──────────────────┘
                         │
                 ┌───────▼────────┐
                 │  BaseExtractor │
                 │  (base.py)     │
                 └────────────────┘
```

---

**Version**: 1.0.0  
**Last Updated**: February 3, 2026  
**Maintainer**: AV Morning Star Team
