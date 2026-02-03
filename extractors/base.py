"""
Base extractor class defining the common interface for all platform extractors
"""

import os
import subprocess
import re
import yt_dlp


def strip_ansi_codes(text):
    """
    Remove ANSI color/formatting codes from text
    
    Args:
        text: Text potentially containing ANSI codes
        
    Returns:
        str: Clean text without ANSI codes
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', str(text))


def detect_available_browsers():
    """
    Detect which browsers are installed and have cookies available
    
    Returns:
        list: List of browser names that have cookies (e.g., ['brave', 'chrome', 'firefox'])
    """
    browsers = ['brave', 'chrome', 'chromium', 'firefox', 'edge', 'opera', 'safari']
    available = []
    
    for browser in browsers:
        if check_browser_cookies(browser):
            available.append(browser)
    
    return available


def extract_cookies_to_file(browser_name):
    """
    Extract browser cookies to a Netscape format cookies.txt file
    (needed for Flatpak browsers where yt-dlp can't access cookies directly)
    
    Args:
        browser_name: Name of the browser
        
    Returns:
        str: Path to cookies file, or None if extraction failed
    """
    import tempfile
    import subprocess
    import os
    
    try:
        # Create temporary cookies file
        fd, cookie_file = tempfile.mkstemp(suffix='.txt', prefix='yt-dlp-cookies-')
        os.close(fd)
        
        # Try to extract cookies using yt-dlp's built-in cookie extraction
        # This creates a cookies file we can reuse
        cmd = [
            'yt-dlp',
            '--cookies-from-browser', browser_name,
            '--cookies', cookie_file,
            '--skip-download',
            '--no-warnings',
            '--quiet',
            'https://www.youtube.com',  # Dummy URL to trigger cookie extraction
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        
        # Check if cookies file was created and has content
        if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 0:
            return cookie_file
        else:
            # Clean up empty file
            try:
                os.remove(cookie_file)
            except:
                pass
            return None
            
    except Exception as e:
        return None


def get_browser_profile_path(browser_name):
    """
    Get the browser profile path (needed for Flatpak installations)
    
    Args:
        browser_name: Name of the browser
        
    Returns:
        str: Profile path if found, None otherwise
    """
    import pathlib
    
    home = pathlib.Path.home()
    
    # Map browser names to their Flatpak and standard profile paths
    profile_paths = {
        'brave': [
            home / '.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser',
            home / '.config/BraveSoftware/Brave-Browser',
        ],
        'chrome': [
            home / '.var/app/com.google.Chrome/config/google-chrome',
            home / '.config/google-chrome',
        ],
        'chromium': [
            home / '.var/app/org.chromium.Chromium/config/chromium',
            home / '.config/chromium',
        ],
        'firefox': [
            home / '.var/app/org.mozilla.firefox/.mozilla/firefox',
            home / '.mozilla/firefox',
        ],
        'edge': [
            home / '.var/app/com.microsoft.Edge/config/microsoft-edge',
            home / '.config/microsoft-edge',
        ],
        'opera': [
            home / '.var/app/com.opera.Opera/config/opera',
            home / '.config/opera',
        ],
    }
    
    paths = profile_paths.get(browser_name.lower(), [])
    
    for path in paths:
        if path.exists():
            return str(path)
    
    return None


def check_browser_cookies(browser_name):
    """
    Check if a browser has cookies available by checking common cookie file locations
    
    Args:
        browser_name: Name of the browser to check
        
    Returns:
        bool: True if browser has accessible cookies
    """
    import pathlib
    
    # Common cookie database locations for each browser
    home = pathlib.Path.home()
    
    cookie_paths = {
        'brave': [
            # Flatpak installation
            home / '.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser/Default/Cookies',
            # Standard installation
            home / '.config/BraveSoftware/Brave-Browser/Default/Cookies',
            home / '.config/BraveSoftware/Brave-Browser/Default/Network/Cookies',
        ],
        'chrome': [
            # Flatpak
            home / '.var/app/com.google.Chrome/config/google-chrome/Default/Cookies',
            # Standard
            home / '.config/google-chrome/Default/Cookies',
            home / '.config/google-chrome/Default/Network/Cookies',
        ],
        'chromium': [
            # Flatpak
            home / '.var/app/org.chromium.Chromium/config/chromium/Default/Cookies',
            # Standard
            home / '.config/chromium/Default/Cookies',
            home / '.config/chromium/Default/Network/Cookies',
        ],
        'firefox': [
            # Flatpak
            home / '.var/app/org.mozilla.firefox/.mozilla/firefox',
            # Standard
            home / '.mozilla/firefox',
        ],
        'edge': [
            # Flatpak
            home / '.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Cookies',
            # Standard
            home / '.config/microsoft-edge/Default/Cookies',
            home / '.config/microsoft-edge/Default/Network/Cookies',
        ],
        'opera': [
            # Flatpak
            home / '.var/app/com.opera.Opera/config/opera/Cookies',
            # Standard
            home / '.config/opera/Cookies',
            home / '.config/opera/Network/Cookies',
        ],
        'safari': [
            home / 'Library/Cookies/Cookies.binarycookies',  # macOS only
        ],
    }
    
    paths = cookie_paths.get(browser_name.lower(), [])
    
    for path in paths:
        if path.exists():
            # For Firefox, check if there's at least one profile
            if browser_name.lower() == 'firefox' and path.is_dir():
                profiles = list(path.glob('*.default*'))
                if profiles:
                    return True
            elif path.is_file():
                return True
    
    return False


def get_default_browser():
    """
    Try to detect the system's default browser
    
    Returns:
        str: Browser name or None if can't detect
    """
    try:
        # Try xdg-settings on Linux
        result = subprocess.run(
            ['xdg-settings', 'get', 'default-web-browser'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            browser_desktop = result.stdout.strip().lower()
            
            # Map .desktop file names to browser names
            browser_map = {
                'brave': 'brave',
                'google-chrome': 'chrome',
                'chromium': 'chromium',
                'firefox': 'firefox',
                'microsoft-edge': 'edge',
                'opera': 'opera',
            }
            
            for key, value in browser_map.items():
                if key in browser_desktop:
                    return value
    except Exception:
        pass
    
    return None


class BaseExtractor:
    """Base class for platform-specific video extractors"""
    
    def __init__(self, url):
        """
        Initialize the extractor
        
        Args:
            url: Video/playlist/channel URL
        """
        self.url = url
        self.platform_name = "Generic"
    
    def get_base_ydl_opts(self):
        """
        Get base yt-dlp options that apply to all platforms
        
        Returns:
            dict: Base yt-dlp options
        """
        return {
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
        }
    
    def get_fetch_opts(self):
        """
        Get yt-dlp options for fetching video metadata (not downloading)
        
        Returns:
            dict: yt-dlp options for metadata extraction
        """
        opts = self.get_base_ydl_opts()
        opts['extract_flat'] = True
        # Don't specify format when extracting metadata - prevents "format not available" errors
        # Format selection only matters during actual downloads
        opts['ignoreerrors'] = False  # We want to catch real errors
        opts['skip_download'] = True  # Ensure we never download during metadata fetch
        return opts
    
    def get_download_opts(self, output_path, filename_template, format_type, 
                         video_quality=None, audio_codec='mp3', audio_quality='192',
                         download_subs=False, embed_thumbnail=False, 
                         normalize_audio=False, denoise_audio=False,
                         dynamic_normalization=False, video_container='mp4'):
        """
        Get yt-dlp options for downloading videos/audio
        
        Args:
            output_path: Directory to save files
            filename_template: Template for output filename
            format_type: 'video' or 'audio'
            video_quality: Video quality string (e.g., 'Best', '1080p')
            audio_codec: Audio codec (mp3, aac, flac, wav, alac, ogg, etc.)
            audio_quality: Audio bitrate (e.g., '192') or '0' for lossless
            download_subs: Whether to download subtitles
            embed_thumbnail: Whether to embed thumbnail in audio
            normalize_audio: Whether to normalize audio volume
            denoise_audio: Whether to denoise audio
            dynamic_normalization: Use dynamic normalization vs EBU R128
            video_container: Video container format (mp4, mkv, webm, avi, mov, flv)
            
        Returns:
            dict: Complete yt-dlp options for downloading
        """
        opts = self.get_base_ydl_opts()
        opts.update({
            'outtmpl': os.path.join(output_path, filename_template),
            'noprogress': False,
            'quiet': False,
            'no_warnings': False,
            'ignore_no_formats_error': False,  # Fail gracefully if no formats available
            'ignoreerrors': False,  # Don't ignore errors - we want to catch them
        })
        
        # Subtitle options
        if download_subs:
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = ['en', 'en-US']
            if format_type == 'video':
                opts['embedsubtitles'] = True
        
        # Format selection
        if format_type == 'audio':
            opts.update(self._get_audio_opts(audio_codec, audio_quality, 
                                             embed_thumbnail, normalize_audio, 
                                             denoise_audio, dynamic_normalization))
        else:
            opts.update(self._get_video_opts(video_quality, video_container))
        
        return opts
    
    def _get_video_opts(self, video_quality, video_container='mp4'):
        """
        Get video-specific download options
        
        Args:
            video_quality: Quality string from UI
            video_container: Container format (mp4, mkv, webm, avi, mov, flv)
            
        Returns:
            dict: Video-specific yt-dlp options
        """
        quality_text = video_quality.lower() if video_quality else 'best'
        
        # Use more flexible format selectors with multiple fallbacks
        if 'best' in quality_text:
            format_str = 'bestvideo*+bestaudio/best'
        elif '2160' in quality_text or '4k' in quality_text:
            format_str = 'bestvideo[height<=2160]+bestaudio/bestvideo*+bestaudio/best'
        elif '1440' in quality_text:
            format_str = 'bestvideo[height<=1440]+bestaudio/bestvideo*+bestaudio/best'
        elif '1080' in quality_text:
            format_str = 'bestvideo[height<=1080]+bestaudio/bestvideo*+bestaudio/best'
        elif '720' in quality_text:
            format_str = 'bestvideo[height<=720]+bestaudio/bestvideo*+bestaudio/best'
        elif '480' in quality_text:
            format_str = 'bestvideo[height<=480]+bestaudio/bestvideo*+bestaudio/best'
        elif '360' in quality_text:
            format_str = 'bestvideo[height<=360]+bestaudio/bestvideo*+bestaudio/best'
        else:
            format_str = 'best'
        
        return {
            'format': format_str,
            'merge_output_format': video_container
        }
    
    def _get_audio_opts(self, audio_codec, audio_quality, embed_thumbnail,
                       normalize_audio, denoise_audio, dynamic_normalization):
        """
        Get audio-specific download options
        
        Args:
            audio_codec: Codec name (mp3, aac, etc.)
            audio_quality: Bitrate string
            embed_thumbnail: Whether to embed thumbnail
            normalize_audio: Whether to normalize volume
            denoise_audio: Whether to denoise
            dynamic_normalization: Use dynamic vs EBU R128
            
        Returns:
            dict: Audio-specific yt-dlp options
        """
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': []
        }
        
        # Audio extraction
        opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_codec.lower(),
            'preferredquality': audio_quality,
        })
        
        # Build audio filter chain
        audio_filters = []
        
        if denoise_audio:
            audio_filters.append('afftdn=nf=-20')
        
        if normalize_audio:
            if dynamic_normalization:
                audio_filters.append('dynaudnorm=p=0.95:m=10:s=12:g=5')
            else:
                audio_filters.append('loudnorm=I=-16:LRA=11:TP=-1.5')
        
        if audio_filters:
            opts['postprocessor_args'] = {
                'ffmpeg': ['-af', ','.join(audio_filters)]
            }
        
        # Thumbnail embedding
        if embed_thumbnail:
            opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            opts['writethumbnail'] = True
        
        # Metadata
        opts['postprocessors'].append({'key': 'FFmpegMetadata'})
        
        return opts
    
    def extract_info(self):
        """
        Extract video information without downloading
        
        Returns:
            list: List of video info dicts with keys: url, title, duration, uploader
        """
        try:
            ydl_opts = self.get_fetch_opts()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info and 'entries' in info:
                    # Playlist/channel
                    return self._parse_playlist(info['entries'])
                else:
                    # Single video
                    return self._parse_single_video(info)
                    
        except Exception as e:
            error_msg = strip_ansi_codes(str(e))
            
            # Check for YouTube anti-bot / n-challenge issues
            if 'n challenge solving failed' in error_msg.lower() or 'no video formats found' in error_msg.lower():
                raise Exception(f"YouTube video extraction failed due to anti-bot measures.\n\nThis is a known YouTube issue. Try:\n\n1. Wait a few minutes and try again\n2. Use a different video URL\n3. Make sure you're logged into YouTube in Brave browser\n\nTechnical: yt-dlp's n-parameter challenge solver needs updating.\nThis affects many YouTube videos currently.")
            
            # Check for common YouTube errors
            elif 'Only images are available' in error_msg or 'only images are available' in error_msg.lower():
                raise Exception(f"This video is not available for download.\n\nPossible reasons:\n• Video has been deleted or made private\n• Video is a premiere that hasn't started\n• Content is restricted in your region\n\nPlease try a different video URL.")
            elif 'Requested format is not available' in error_msg or 'format is not available' in error_msg.lower():
                raise Exception(f"This video cannot be downloaded.\n\nThis usually means:\n• Video has been deleted or made private\n• Video is currently being processed\n• Content is age-restricted or region-locked\n• YouTube anti-bot protection is active\n\nPlease verify the video works in your browser, or try a different URL.")
            elif 'Sign in' in error_msg or 'not a bot' in error_msg.lower():
                raise Exception(f"YouTube authentication required.\n\nPlease:\n1. Open YouTube in your browser (Brave)\n2. Sign in to your account\n3. Try fetching the video again\n\nThe app uses your browser's login cookies.")
            elif 'private video' in error_msg.lower() or 'video unavailable' in error_msg.lower():
                raise Exception(f"Video is private or unavailable.\n\nThis video cannot be accessed. It may be:\n• Set to private by the uploader\n• Removed by YouTube\n• Not available in your region\n\nPlease try a different video URL.")
            else:
                # Generic error with cleaned message
                raise Exception(f"Unable to fetch video information.\n\n{error_msg[:300]}\n\nPlease verify:\n• The URL is correct\n• The video is publicly accessible\n• You're logged into YouTube in your browser")
    
    def _parse_playlist(self, entries):
        """Parse playlist entries into standardized format"""
        videos = []
        for entry in entries:
            if entry:
                uploader = self._get_uploader(entry)
                videos.append({
                    'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'title': entry.get('title', 'Unknown Title'),
                    'duration': entry.get('duration', 0),
                    'uploader': uploader
                })
        return videos
    
    def _parse_single_video(self, info):
        """Parse single video info into standardized format"""
        uploader = self._get_uploader(info)
        return [{
            'url': self.url,
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'uploader': uploader
        }]
    
    def _get_uploader(self, info):
        """
        Extract uploader name with fallbacks
        
        Args:
            info: Video info dict from yt-dlp
            
        Returns:
            str: Uploader name or 'Unknown'
        """
        return (info.get('uploader') or 
                info.get('channel') or 
                info.get('uploader_id') or 
                info.get('creator') or 
                'Unknown')
