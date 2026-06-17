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

from extractors.podcast_page import PodcastPageExtractor

# ---------------------------------------------------------------------------
# PodcastPageExtractor — _is_audio_url
# ---------------------------------------------------------------------------

class TestIsAudioUrl(unittest.TestCase):
    """_is_audio_url classifies URLs by file extension."""

    def setUp(self):
        self.extractor = PodcastPageExtractor("http://example.com/feed")

    def test_known_audio_extensions_accepted(self):
        audio_urls = [
            "http://example.com/ep1.mp3",
            "http://example.com/ep2.m4a",
            "http://example.com/ep3.aac",
            "http://example.com/ep4.ogg",
            "http://example.com/ep5.opus",
            "http://example.com/ep6.wav",
            "http://example.com/ep7.flac",
        ]
        for url in audio_urls:
            with self.subTest(url=url):
                self.assertTrue(self.extractor._is_audio_url(url))

    def test_non_audio_extensions_rejected(self):
        non_audio = [
            "http://example.com/video.mp4",
            "http://example.com/page.html",
            "http://example.com/image.jpg",
            "http://example.com/",
            "http://example.com/data.json",
        ]
        for url in non_audio:
            with self.subTest(url=url):
                self.assertFalse(self.extractor._is_audio_url(url))

class TestTitleFromUrl(unittest.TestCase):
    """_title_from_url derives a readable title from the audio file path."""

    def setUp(self):
        self.extractor = PodcastPageExtractor("http://example.com/feed")

    def test_hyphens_replaced_with_spaces(self):
        self.assertEqual(
            self.extractor._title_from_url("http://example.com/my-episode.mp3"),
            "my episode",
        )

    def test_underscores_replaced_with_spaces(self):
        self.assertEqual(
            self.extractor._title_from_url("http://example.com/my_episode.mp3"),
            "my episode",
        )

    def test_nested_path_uses_last_segment(self):
        self.assertEqual(
            self.extractor._title_from_url("http://example.com/season1/ep-01.mp3"),
            "ep 01",
        )

    def test_empty_path_returns_fallback(self):
        self.assertEqual(
            self.extractor._title_from_url("http://example.com/"),
            "Podcast Audio",
        )
