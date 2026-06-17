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

class TestGetExtractorFactory(unittest.TestCase):
    """get_extractor routes URLs to the correct extractor class."""

    def test_youtube_com_url_returns_youtube_extractor(self):
        ext = get_extractor("https://www.youtube.com/watch?v=abc123")
        self.assertIsInstance(ext, YouTubeExtractor)

    def test_youtu_be_short_url_returns_youtube_extractor(self):
        ext = get_extractor("https://youtu.be/abc123")
        self.assertIsInstance(ext, YouTubeExtractor)

    def test_odysee_url_returns_generic_extractor(self):
        ext = get_extractor("https://odysee.com/@channel/video")
        self.assertIsInstance(ext, GenericExtractor)

    def test_lbry_tv_url_returns_generic_extractor(self):
        ext = get_extractor("https://lbry.tv/@channel/video")
        self.assertIsInstance(ext, GenericExtractor)

    def test_generic_url_returns_generic_extractor(self):
        ext = get_extractor("https://vimeo.com/123456789")
        self.assertIsInstance(ext, GenericExtractor)

    def test_youtube_with_cookies_passed_through(self):
        ext = get_extractor("https://www.youtube.com/watch?v=abc", cookies_from_browser="firefox")
        self.assertIsInstance(ext, YouTubeExtractor)
        self.assertEqual(ext.cookies_from_browser, "firefox")

    def test_generic_extractor_has_no_cookies_attribute(self):
        ext = get_extractor("https://vimeo.com/123456789")
        self.assertIsInstance(ext, GenericExtractor)

class TestIsYoutubeUrl(unittest.TestCase):
    """is_youtube_url must use parsed hostname, not substring matching."""

    def test_standard_youtube_url(self):
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=abc"))

    def test_short_youtu_be_url(self):
        self.assertTrue(is_youtube_url("https://youtu.be/abc"))

    def test_mobile_youtube_url(self):
        self.assertTrue(is_youtube_url("https://m.youtube.com/watch?v=abc"))

    def test_non_youtube_url(self):
        self.assertFalse(is_youtube_url("https://vimeo.com/123456789"))

    def test_odysee_url(self):
        self.assertFalse(is_youtube_url("https://odysee.com/@channel/video"))

    # Hostile URL cases — must NOT match despite containing 'youtube.com'
    def test_userinfo_confusion_youtube_in_username(self):
        # https://youtube.com@evil.example/ — parsed hostname is evil.example
        self.assertFalse(is_youtube_url("https://youtube.com@evil.example/watch?v=abc"))

    def test_youtube_in_path_only(self):
        self.assertFalse(is_youtube_url("https://evil.example/youtube.com/watch?v=abc"))

    def test_youtube_in_query_only(self):
        self.assertFalse(is_youtube_url("https://evil.example/?ref=youtube.com"))

    def test_malformed_url_returns_false(self):
        self.assertFalse(is_youtube_url("not a url at all"))

    def test_empty_string_returns_false(self):
        self.assertFalse(is_youtube_url(""))
