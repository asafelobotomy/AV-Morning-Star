"""
Base extractor class defining the common interface for all platform extractors
"""

import os

import yt_dlp

from .ffmpeg_filters import (
    AUDIO_DENOISE_FILTER,
    AUDIO_DYNAUDNORM_FILTER,
    AUDIO_LOUDNORM_FILTER,
    VIDEO_DENOISE_FILTER,
    VIDEO_SHARPEN_FILTER,
    strip_ansi_codes,
)
from .ytdlp_format_opts import build_audio_opts, build_video_opts

__all__ = [
    'BaseExtractor',
    'VIDEO_DENOISE_FILTER',
    'VIDEO_SHARPEN_FILTER',
    'AUDIO_DENOISE_FILTER',
    'AUDIO_LOUDNORM_FILTER',
    'AUDIO_DYNAUDNORM_FILTER',
    'strip_ansi_codes',
]


class BaseExtractor:
    """Base class for platform-specific video extractors"""

    def __init__(self, url):
        self.url = url
        self.platform_name = "Generic"

    def get_base_ydl_opts(self):
        return {
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
        }

    def get_fetch_opts(self):
        opts = self.get_base_ydl_opts()
        opts['extract_flat'] = True
        opts['ignoreerrors'] = False
        opts['skip_download'] = True
        return opts

    def get_download_opts(
        self,
        output_path,
        filename_template,
        format_type,
        video_quality=None,
        audio_codec='mp3',
        audio_quality='192',
        download_subs=False,
        embed_thumbnail=False,
        normalize_audio=False,
        denoise_audio=False,
        dynamic_normalization=False,
        video_container='mp4',
        denoise_video=False,
        stabilize_video=False,
        sharpen_video=False,
        normalize_video_audio=False,
        denoise_video_audio=False,
    ):
        opts = self.get_base_ydl_opts()
        opts.update({
            'outtmpl': os.path.join(output_path, filename_template),
            'noprogress': False,
            'quiet': False,
            'no_warnings': False,
            'ignore_no_formats_error': False,
            'ignoreerrors': False,
        })

        if download_subs:
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = ['en', 'en-US']
            if format_type == 'video':
                opts['embedsubtitles'] = True

        if format_type == 'audio':
            opts.update(build_audio_opts(
                audio_codec, audio_quality, embed_thumbnail,
                normalize_audio, denoise_audio, dynamic_normalization,
            ))
        else:
            opts.update(build_video_opts(
                video_quality, video_container,
                denoise_video, stabilize_video, sharpen_video,
                normalize_video_audio, denoise_video_audio,
            ))

        return opts

    def extract_info(self):
        try:
            with yt_dlp.YoutubeDL(self.get_fetch_opts()) as ydl:
                info = ydl.extract_info(self.url, download=False)

                if info and 'entries' in info:
                    return self._parse_playlist(info['entries'])
                return self._parse_single_video(info)

        except Exception as e:
            error_msg = strip_ansi_codes(str(e))
            raise self._format_extract_error(error_msg) from e

    def _format_extract_error(self, error_msg):
        lower = error_msg.lower()
        if 'n challenge solving failed' in lower or 'no video formats found' in lower:
            return Exception(
                "YouTube video extraction failed due to anti-bot measures.\n\n"
                "This is a known YouTube issue. Try:\n\n"
                "1. Wait a few minutes and try again\n"
                "2. Use a different video URL\n"
                "3. Make sure you're logged into YouTube in Brave browser\n\n"
                "Technical: yt-dlp's n-parameter challenge solver needs updating.\n"
                "This affects many YouTube videos currently."
            )
        if 'only images are available' in lower:
            return Exception(
                "This video is not available for download.\n\n"
                "Possible reasons:\n"
                "• Video has been deleted or made private\n"
                "• Video is a premiere that hasn't started\n"
                "• Content is restricted in your region\n\n"
                "Please try a different video URL."
            )
        if 'format is not available' in lower:
            return Exception(
                "This video cannot be downloaded.\n\n"
                "This usually means:\n"
                "• Video has been deleted or made private\n"
                "• Video is currently being processed\n"
                "• Content is age-restricted or region-locked\n"
                "• YouTube anti-bot protection is active\n\n"
                "Please verify the video works in your browser, or try a different URL."
            )
        if 'sign in' in error_msg or 'not a bot' in lower:
            return Exception(
                "YouTube authentication required.\n\n"
                "Please:\n"
                "1. Open YouTube in your browser (Brave)\n"
                "2. Sign in to your account\n"
                "3. Try fetching the video again\n\n"
                "The app uses your browser's login cookies."
            )
        if 'private video' in lower or 'video unavailable' in lower:
            return Exception(
                "Video is private or unavailable.\n\n"
                "This video cannot be accessed. It may be:\n"
                "• Set to private by the uploader\n"
                "• Removed by YouTube\n"
                "• Not available in your region\n\n"
                "Please try a different video URL."
            )
        return Exception(
            f"Unable to fetch video information.\n\n{error_msg[:300]}\n\n"
            "Please verify:\n"
            "• The URL is correct\n"
            "• The video is publicly accessible\n"
            "• You're logged into YouTube in your browser"
        )

    def _parse_playlist(self, entries):
        videos = []
        for entry in entries:
            if entry:
                videos.append({
                    'url': (
                        entry.get('url')
                        or entry.get('webpage_url')
                        or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    ),
                    'title': entry.get('title', 'Unknown Title'),
                    'duration': entry.get('duration', 0),
                    'uploader': self._get_uploader(entry),
                })
        return videos

    def _parse_single_video(self, info):
        return [{
            'url': self.url,
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'uploader': self._get_uploader(info),
        }]

    def _get_uploader(self, info):
        return (
            info.get('uploader')
            or info.get('channel')
            or info.get('uploader_id')
            or info.get('creator')
            or 'Unknown'
        )
