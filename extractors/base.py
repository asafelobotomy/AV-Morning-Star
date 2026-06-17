"""
Base extractor class defining the common interface for all platform extractors
"""

import os

import yt_dlp

from lyrics.detector import is_youtube_music_url

from .extract_errors import format_extract_error
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

    def __init__(self, url, cookies_from_browser=None):
        self.url = url
        self.platform_name = "Generic"
        self.cookies_from_browser = cookies_from_browser

    def get_base_ydl_opts(self):
        opts = {
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
        }
        if self.cookies_from_browser:
            opts['cookiesfrombrowser'] = (self.cookies_from_browser,)
        return opts

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
        fetch_lyrics=False,
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
            # SRT embeds cleanly into MP4/MKV; fall back through VTT to
            # whatever the site offers if SRT is unavailable.
            opts['subtitlesformat'] = 'srt/vtt/best'
            if format_type == 'video':
                opts['embedsubtitles'] = True

        # YouTube Music subtitle tracks are the song lyrics in LRC/ELRC format.
        # Requesting them here lets yt-dlp write the .lrc file alongside the
        # audio as a first-class native extraction — no external API needed.
        if fetch_lyrics and format_type == 'audio' and is_youtube_music_url(self.url):
            opts['writesubtitles'] = True
            opts['subtitlesformat'] = 'lrc/elrc/txt'
            opts['subtitleslangs'] = ['orig', 'en']

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
            raise format_extract_error(error_msg) from e

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
