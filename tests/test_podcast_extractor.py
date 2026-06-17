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

class TestPodcastPageExtractorExtractInfo(unittest.TestCase):
    """extract_info scrapes audio links from HTML with network mocked out."""

    SAMPLE_HTML = b"""
    <html><body>
      <a href="/eps/ep1.mp3">Episode 1</a>
      <a href="/eps/ep2.mp3">Episode 2</a>
      <a href="/about.html">About</a>
      <a href="http://cdn.other.com/ep3.mp3">External Audio</a>
    </body></html>
    """

    def _mock_response(self, body_bytes, charset="utf-8"):
        resp = MagicMock()
        resp.read.return_value = body_bytes
        resp.headers.get_content_charset.return_value = charset
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    @patch("extractors.podcast_page.urlopen")
    def test_returns_only_audio_items(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(self.SAMPLE_HTML)
        extractor = PodcastPageExtractor("http://example.com/")
        results = extractor.extract_info()
        urls = [r["url"] for r in results]
        self.assertIn("http://example.com/eps/ep1.mp3", urls)
        self.assertIn("http://example.com/eps/ep2.mp3", urls)
        self.assertIn("http://cdn.other.com/ep3.mp3", urls)
        self.assertNotIn("http://example.com/about.html", urls)

    @patch("extractors.podcast_page.urlopen")
    def test_deduplicates_repeated_links(self, mock_urlopen):
        html = b"""
        <html><body>
          <a href="/ep.mp3">Ep</a>
          <a href="/ep.mp3">Ep duplicate</a>
        </body></html>
        """
        mock_urlopen.return_value = self._mock_response(html)
        results = PodcastPageExtractor("http://example.com/").extract_info()
        self.assertEqual(len(results), 1)

    @patch("extractors.podcast_page.urlopen")
    def test_each_item_has_required_keys(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response(self.SAMPLE_HTML)
        results = PodcastPageExtractor("http://example.com/").extract_info()
        for item in results:
            with self.subTest(url=item.get("url")):
                self.assertIn("url", item)
                self.assertIn("title", item)
                self.assertIn("duration", item)
                self.assertIn("uploader", item)

    def test_direct_audio_url_skips_network(self):
        """A URL that is itself an audio file returns immediately without fetching."""
        extractor = PodcastPageExtractor("http://example.com/ep.mp3")
        # No mock needed — extract_info returns early for direct audio URLs
        results = extractor.extract_info()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "http://example.com/ep.mp3")

    @patch("extractors.podcast_page.urlopen")
    def test_hostile_scheme_links_excluded(self, mock_urlopen):
        """Extracted links with non-http(s) schemes must be silently dropped."""
        html = b"""
        <html><body>
          <a href="file:///etc/passwd.mp3">Hostile file</a>
          <a href="ftp://evil.example/ep.mp3">Hostile ftp</a>
          <a href="/safe/ep.mp3">Safe</a>
        </body></html>
        """
        resp = MagicMock()
        resp.headers.get_content_type.return_value = "text/html"
        resp.headers.get.return_value = None
        resp.headers.get_content_charset.return_value = "utf-8"
        resp.read.return_value = html
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp
        results = PodcastPageExtractor("http://example.com/").extract_info()
        urls = [r["url"] for r in results]
        self.assertNotIn("file:///etc/passwd.mp3", urls)
        self.assertNotIn("ftp://evil.example/ep.mp3", urls)
        self.assertIn("http://example.com/safe/ep.mp3", urls)
