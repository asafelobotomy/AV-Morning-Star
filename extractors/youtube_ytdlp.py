"""
YouTube-specific extractor using yt-dlp backend

This replaces the InnerTube API approach with yt-dlp, which properly handles:
- Proof of Origin (PO) Tokens
- JavaScript challenge solving
- Bot detection bypasses
- Browser cookie authentication

As of February 2026, YouTube requires external JS runtime (Deno/Node.js) for PO token
generation. yt-dlp handles this automatically.
"""

import yt_dlp


class YouTubeExtractor:
    """YouTube video extractor using yt-dlp backend"""
    
    def __init__(self, url, cookies_from_browser=None):
        """
        Initialize YouTube extractor with yt-dlp backend
        
        Args:
            url: YouTube video/playlist/channel URL
            cookies_from_browser: Browser name to extract cookies from (e.g., 'firefox', 'chrome', 'brave')
        """
        self.url = url
        self.platform_name = "YouTube"
        self.cookies_from_browser = cookies_from_browser
        
    def extract_info(self):
        """
        Extract video information from YouTube URL
        
        Returns:
            List of dicts with video info: [{'title': ..., 'url': ..., 'uploader': ..., 'duration': ...}, ...]
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # Don't download, just get info
            'skip_download': True,
            'allow_unplayable_formats': False,
        }
        
        # Enable remote components for YouTube challenge solving (PO tokens)
        # This requires Deno/Node.js to be installed
        ydl_opts['remote_components'] = ['ejs:github']
        
        # Add browser cookies if specified
        if self.cookies_from_browser:
            ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                return self._convert_to_standard_format(info)
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
                raise Exception(
                    f"YouTube bot detection active. To fix this:\n\n"
                    f"1. Make sure you're logged into YouTube in {self.cookies_from_browser or 'your browser'}\n"
                    f"2. Go to Tools > Preferences and verify browser selection\n"
                    f"3. Try signing out and back in to YouTube\n"
                    f"4. Clear YouTube cookies and login again\n"
                    f"5. Wait a few minutes if rate-limited\n\n"
                    f"Technical details: {error_msg[:200]}"
                )
            else:
                raise Exception(f"YouTube extraction failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Failed to extract YouTube info: {str(e)}\n\n"
                          f"Troubleshooting:\n"
                          f"1. Verify you're logged into YouTube in {self.cookies_from_browser or 'your browser'}\n"
                          f"2. Update yt-dlp: pip install --upgrade yt-dlp\n"
                          f"3. Ensure Deno is installed: deno --version\n"
                          f"4. Try a different browser in Preferences")
    
    def _convert_to_standard_format(self, info):
        """
        Convert yt-dlp info dict to our standard format
        
        Args:
            info: yt-dlp info dict
            
        Returns:
            List of video dicts in our standard format
        """
        videos = []
        
        # Handle playlist/channel (multiple videos)
        if 'entries' in info:
            for entry in info['entries']:
                if entry:  # Some entries might be None
                    videos.append(self._format_single_video(entry))
        # Handle single video
        else:
            videos.append(self._format_single_video(info))
        
        return videos
    
    def _format_single_video(self, entry):
        """
        Format a single video entry to our standard format
        
        Args:
            entry: Single video info dict from yt-dlp
            
        Returns:
            Dict with standardized video info
        """
        return {
            'title': entry.get('title', 'Unknown Title'),
            'url': entry.get('webpage_url') or entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
            'uploader': entry.get('uploader') or entry.get('channel') or 'Unknown',
            'duration': entry.get('duration', 0),  # Duration in seconds
            'thumbnail': entry.get('thumbnail'),
            'description': entry.get('description'),
            'view_count': entry.get('view_count'),
            'upload_date': entry.get('upload_date'),
            'id': entry.get('id'),
        }
    
    def get_download_opts(self, output_path, filename_template, format_type, 
                         video_quality=None, audio_codec='mp3', audio_quality='192',
                         download_subs=False, embed_thumbnail=False, 
                         normalize_audio=False, denoise_audio=False,
                         dynamic_normalization=False):
        """
        Get yt-dlp download options
        
        Returns:
            Dict of yt-dlp options for downloading
        """
        ydl_opts = {
            'outtmpl': f'{output_path}/{filename_template}',
            'quiet': False,
            'no_warnings': False,
            'allow_unplayable_formats': False,
        }
        
        # Enable remote components for YouTube challenge solving (PO tokens)
        ydl_opts['remote_components'] = ['ejs:github']
        
        # Add browser cookies if specified
        if self.cookies_from_browser:
            ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)
        
        # Format selection
        if format_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_codec.lower(),
                'preferredquality': audio_quality,
            }]
            
            # Add thumbnail embedding for audio
            if embed_thumbnail:
                ydl_opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                })
                ydl_opts['writethumbnail'] = True
            
            # Audio normalization
            if normalize_audio:
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegNormalize',
                    'normalization': 'ebu' if not dynamic_normalization else 'dynaudnorm',
                })
            
            # Audio denoising
            if denoise_audio:
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegAudioFilter',
                    'filter': 'afftdn=nf=-25',
                })
        else:
            # Video download
            if video_quality and video_quality != 'Best':
                # Extract resolution (e.g., "1080p" -> "1080")
                quality_map = {
                    '4K (2160p)': '2160',
                    '1440p': '1440',
                    '1080p': '1080',
                    '720p': '720',
                    '480p': '480',
                    '360p': '360',
                }
                height = quality_map.get(video_quality, '1080')
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
        
        # Subtitle download
        if download_subs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en', 'en-US']
        
        return ydl_opts
