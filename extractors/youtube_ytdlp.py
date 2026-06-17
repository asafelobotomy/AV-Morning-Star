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

from .base import BaseExtractor


class YouTubeExtractor(BaseExtractor):
    """YouTube video extractor using yt-dlp backend"""

    def __init__(self, url, cookies_from_browser=None):
        """
        Initialize YouTube extractor with yt-dlp backend

        Args:
            url: YouTube video/playlist/channel URL
            cookies_from_browser: Browser name to extract cookies from (e.g., 'firefox', 'chrome', 'brave')
        """
        super().__init__(url)
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

        # PO token generation uses locally-installed Deno/Node.js; no remote
        # components are loaded so no untrusted code is fetched at runtime.

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
            'url': (
                entry.get('webpage_url')
                or entry.get('url')
                or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
            ),
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
                         dynamic_normalization=False, video_container='mp4',
                         denoise_video=False, stabilize_video=False,
                         sharpen_video=False, normalize_video_audio=False,
                         denoise_video_audio=False, fetch_lyrics=False):
        """
        Get yt-dlp download options, delegating all audio/video processing to
        BaseExtractor and adding YouTube-specific settings (cookies,
        allow_unplayable_formats).

        Returns:
            Dict of yt-dlp options for downloading
        """
        # PO token generation uses locally-installed Deno/Node.js; no remote
        # components are loaded so no untrusted code is fetched at runtime.
        ydl_opts = super().get_download_opts(
            output_path, filename_template, format_type,
            video_quality=video_quality, audio_codec=audio_codec,
            audio_quality=audio_quality, download_subs=download_subs,
            embed_thumbnail=embed_thumbnail, normalize_audio=normalize_audio,
            denoise_audio=denoise_audio, dynamic_normalization=dynamic_normalization,
            video_container=video_container, denoise_video=denoise_video,
            stabilize_video=stabilize_video, sharpen_video=sharpen_video,
            normalize_video_audio=normalize_video_audio,
            denoise_video_audio=denoise_video_audio,
            fetch_lyrics=fetch_lyrics,
        )

        # YouTube-specific additions
        ydl_opts['allow_unplayable_formats'] = False
        if self.cookies_from_browser:
            ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)

        return ydl_opts
