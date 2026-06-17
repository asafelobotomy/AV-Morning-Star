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

from extractors.generic import GenericExtractor

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

    # --- Cookie passthrough ---

    def test_no_cookies_by_default(self):
        self.assertIsNone(self.extractor.cookies_from_browser)

    def test_cookies_stored_when_provided(self):
        ext = GenericExtractor("http://example.com/video", cookies_from_browser="firefox")
        self.assertEqual(ext.cookies_from_browser, "firefox")

    def test_cookies_in_fetch_opts_when_set(self):
        ext = GenericExtractor("http://example.com/video", cookies_from_browser="brave")
        opts = ext.get_fetch_opts()
        self.assertIn("cookiesfrombrowser", opts)
        self.assertEqual(opts["cookiesfrombrowser"], ("brave",))

    def test_no_cookies_in_fetch_opts_when_not_set(self):
        opts = self.extractor.get_fetch_opts()
        self.assertNotIn("cookiesfrombrowser", opts)

    def test_cookies_in_download_opts_when_set(self):
        ext = GenericExtractor("http://example.com/video", cookies_from_browser="chrome")
        opts = ext.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIn("cookiesfrombrowser", opts)
        self.assertEqual(opts["cookiesfrombrowser"], ("chrome",))

    def test_no_cookies_in_download_opts_when_not_set(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertNotIn("cookiesfrombrowser", opts)
