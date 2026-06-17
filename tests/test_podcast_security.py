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
from unittest.mock import MagicMock, patch

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

# ---------------------------------------------------------------------------
# PodcastPageExtractor — _is_audio_url
# ---------------------------------------------------------------------------

class TestPodcastFetchHtmlSecurity(unittest.TestCase):
    """_fetch_html must reject unsafe schemes, wrong content types, and large bodies."""

    def setUp(self):
        self.extractor = PodcastPageExtractor("http://example.com/feed")

    def test_non_http_scheme_raises(self):
        with self.assertRaises(ValueError, msg="ftp:// should be rejected"):
            self.extractor._fetch_html("ftp://example.com/feed.html")

    def test_file_scheme_raises(self):
        with self.assertRaises(ValueError, msg="file:// should be rejected"):
            self.extractor._fetch_html("file:///etc/passwd")

    @patch("extractors.podcast_page.urlopen")
    def test_non_html_content_type_raises(self, mock_urlopen):
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "application/octet-stream"
        resp.headers.get.return_value = None
        resp.read.return_value = b""
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        with self.assertRaises(ValueError, msg="non-HTML content type should be rejected"):
            self.extractor._fetch_html("http://example.com/feed")

    @patch("extractors.podcast_page.urlopen")
    def test_oversized_content_length_header_raises(self, mock_urlopen):
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "text/html"
        resp.headers.get.return_value = str(6 * 1024 * 1024)  # 6 MiB > 5 MiB cap
        resp.read.return_value = b"<html></html>"
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        with self.assertRaises(ValueError, msg="Content-Length exceeding cap should be rejected"):
            self.extractor._fetch_html("http://example.com/feed")

    @patch("extractors.podcast_page.urlopen")
    def test_oversized_body_raises(self, mock_urlopen):
        big_body = b"x" * (5 * 1024 * 1024 + 1)
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "text/html"
        resp.headers.get.return_value = None
        resp.headers.get_content_charset.return_value = "utf-8"
        resp.read.return_value = big_body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        with self.assertRaises(ValueError, msg="Body exceeding cap should be rejected"):
            self.extractor._fetch_html("http://example.com/feed")

    @patch("extractors.podcast_page.urlopen")
    def test_valid_html_response_returns_string(self, mock_urlopen):
        body = b"<html><body><a href='/ep.mp3'>Ep</a></body></html>"
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "text/html; charset=utf-8"
        resp.headers.get.return_value = None
        resp.headers.get_content_charset.return_value = "utf-8"
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        result = self.extractor._fetch_html("http://example.com/feed")
        self.assertIn("<html>", result)

    @patch("extractors.podcast_page.urlopen")
    def test_malformed_content_length_header_does_not_raise(self, mock_urlopen):
        """A non-numeric Content-Length must be silently ignored, not crash."""
        body = b"<html><body></body></html>"
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "text/html"
        resp.headers.get.return_value = "not-a-number"
        resp.headers.get_content_charset.return_value = "utf-8"
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        result = self.extractor._fetch_html("http://example.com/feed")
        self.assertIn("<html>", result)
