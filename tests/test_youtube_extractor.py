"""
Tests for platform-specific extractors.

Covers:
- PodcastPageExtractor: URL classification, title derivation, HTML parsing
- BaseExtractor: option building, FFmpeg filter chain construction
"""

import os
import sys
import types
import unittest
from unittest.mock import patch, MagicMock

# ---- Stub yt_dlp so extractor tests run without the downloader installed ----
if 'yt_dlp' not in sys.modules:
    _yt_dlp = types.ModuleType('yt_dlp')
    _yt_dlp.YoutubeDL = type('YoutubeDL', (object,), {'__init__': lambda self, *a, **kw: None})
    _yt_dlp_utils = types.ModuleType('yt_dlp.utils')
    _yt_dlp_utils.DownloadError = Exception
    _yt_dlp.utils = _yt_dlp_utils
    sys.modules['yt_dlp'] = _yt_dlp
    sys.modules['yt_dlp.utils'] = _yt_dlp_utils

# Ensure the workspace root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.podcast_page import PodcastPageExtractor
from extractors.base import (
    BaseExtractor,
    VIDEO_DENOISE_FILTER,
    VIDEO_SHARPEN_FILTER,
    AUDIO_DENOISE_FILTER,
    AUDIO_LOUDNORM_FILTER,
    AUDIO_DYNAUDNORM_FILTER,
)
from extractors.generic import GenericExtractor
from extractors.youtube_ytdlp import YouTubeExtractor
from extractors import get_extractor, is_youtube_url


# ---------------------------------------------------------------------------
# PodcastPageExtractor — _is_audio_url
# ---------------------------------------------------------------------------

class TestYouTubeExtractor(unittest.TestCase):
    """YouTubeExtractor builds correct yt-dlp opts (no network calls made)."""

    def setUp(self):
        self.extractor = YouTubeExtractor("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_platform_name_is_youtube(self):
        self.assertEqual(self.extractor.platform_name, "YouTube")

    def test_default_cookies_from_browser_is_none(self):
        self.assertIsNone(self.extractor.cookies_from_browser)

    def test_cookies_stored_when_provided(self):
        ext = YouTubeExtractor("https://www.youtube.com/watch?v=x", cookies_from_browser="firefox")
        self.assertEqual(ext.cookies_from_browser, "firefox")

    def test_download_opts_has_outtmpl(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIn("outtmpl", opts)

    def test_download_opts_audio_sets_format_bestaudio(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "audio")
        self.assertIn("bestaudio", opts.get("format", ""))

    def test_download_opts_no_cookies_key_when_browser_is_none(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertNotIn("cookiesfrombrowser", opts)

    def test_download_opts_cookies_key_present_when_browser_set(self):
        ext = YouTubeExtractor("https://www.youtube.com/watch?v=x", cookies_from_browser="brave")
        opts = ext.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIn("cookiesfrombrowser", opts)
        self.assertEqual(opts["cookiesfrombrowser"][0], "brave")

    # --- Subtitle embedding parity with BaseExtractor ---

    def test_video_download_with_subs_sets_embedsubtitles(self):
        opts = self.extractor.get_download_opts(
            "/tmp", "%(title)s.%(ext)s", "video", download_subs=True
        )
        self.assertTrue(opts.get("embedsubtitles"), "embedsubtitles must be True for video+subs")

    def test_audio_download_with_subs_does_not_set_embedsubtitles(self):
        opts = self.extractor.get_download_opts(
            "/tmp", "%(title)s.%(ext)s", "audio", download_subs=True
        )
        self.assertFalse(opts.get("embedsubtitles", False))

    def test_video_download_without_subs_does_not_set_embedsubtitles(self):
        opts = self.extractor.get_download_opts(
            "/tmp", "%(title)s.%(ext)s", "video", download_subs=False
        )
        self.assertFalse(opts.get("embedsubtitles", False))

    def test_subtitle_parity_with_base_extractor(self):
        """YouTubeExtractor subtitle options must match BaseExtractor for video+subs."""
        base = BaseExtractor("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        base_opts = base.get_download_opts("/tmp", "%(title)s.%(ext)s", "video", download_subs=True)
        yt_opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video", download_subs=True)
        for key in ("writesubtitles", "writeautomaticsub", "embedsubtitles"):
            with self.subTest(key=key):
                self.assertEqual(
                    yt_opts.get(key),
                    base_opts.get(key),
                    f"YouTube and BaseExtractor disagree on '{key}'",
                )
