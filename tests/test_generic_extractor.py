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

class TestGenericExtractor(unittest.TestCase):
    """GenericExtractor enforces safe SSL defaults on top of base options."""

    def setUp(self):
        self.extractor = GenericExtractor("http://example.com/video")

    def test_platform_name_is_generic(self):
        self.assertEqual(self.extractor.platform_name, "Generic")

    def test_fetch_opts_nocheckcertificate_is_false(self):
        opts = self.extractor.get_fetch_opts()
        self.assertFalse(opts.get("nocheckcertificate"))

    def test_fetch_opts_prefer_insecure_is_false(self):
        opts = self.extractor.get_fetch_opts()
        self.assertFalse(opts.get("prefer_insecure"))

    def test_download_opts_nocheckcertificate_is_false(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertFalse(opts.get("nocheckcertificate"))

    def test_download_opts_prefer_insecure_is_false(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertFalse(opts.get("prefer_insecure"))

    def test_download_opts_has_outtmpl(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIn("outtmpl", opts)
