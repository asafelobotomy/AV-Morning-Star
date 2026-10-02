"""
Regression tests for bugs found in the 2026-10 audit.

Each test pins one defect that previously shipped:
- float durations crashed the video list (SIGABRT in the AppImage)
- non-YouTube extractors rejected the fetch_lyrics kwarg, failing every download
- LRC detection missed files with more than four header tags
- .lrc sidecar lookup matched other tracks sharing a filename prefix
- error classification on bare '429' and case-sensitive 'sign in'
"""

import inspect
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_mixins.videos_list import format_duration
from extractors import get_extractor
from extractors.base import BaseExtractor
from extractors.extract_errors import format_extract_error
from lyrics.embedder import is_lrc_format
from threads import DownloadThread


class TestFormatDuration(unittest.TestCase):
    def test_float_duration(self):
        self.assertEqual(format_duration(213.0), "00:03:33")

    def test_fractional_float_duration(self):
        self.assertEqual(format_duration(3725.7), "01:02:05")

    def test_int_duration(self):
        self.assertEqual(format_duration(59), "00:00:59")

    def test_missing_duration(self):
        for raw in (None, 0, "", "abc"):
            with self.subTest(raw=raw):
                self.assertEqual(format_duration(raw), "N/A")


class TestExtractorDownloadOptsSignature(unittest.TestCase):
    URLS = (
        "https://www.youtube.com/watch?v=x",
        "https://odysee.com/@chan/video",
        "https://example.com/podcast.rss",
        "https://fat-pie.com/episodes",
    )

    def test_every_extractor_accepts_fetch_lyrics(self):
        """DownloadThread always passes fetch_lyrics=...; every extractor must accept it."""
        for url in self.URLS:
            extractor = get_extractor(url)
            with self.subTest(extractor=type(extractor).__name__):
                opts = extractor.get_download_opts(
                    "/tmp", "%(title)s.%(ext)s", "audio", fetch_lyrics=True,
                )
                self.assertIn("outtmpl", opts)

    def test_overrides_keep_base_parameters(self):
        base_params = set(inspect.signature(BaseExtractor.get_download_opts).parameters)
        for url in self.URLS:
            extractor = get_extractor(url)
            params = set(inspect.signature(type(extractor).get_download_opts).parameters)
            with self.subTest(extractor=type(extractor).__name__):
                self.assertEqual(base_params - params, set())


class TestLrcDetection(unittest.TestCase):
    def test_lrc_with_many_header_tags(self):
        text = "[ar:Artist]\n[ti:Title]\n[al:Album]\n[by:Someone]\n[length:03:20]\n[00:12.34]First line"
        self.assertTrue(is_lrc_format(text))


class TestLrcSidecarLookup(unittest.TestCase):
    def test_ignores_other_track_with_same_prefix(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "Song 2.en.lrc").write_text("[00:01.00]x")
            audio = Path(d) / "Song.mp3"
            self.assertIsNone(DownloadThread._find_lrc_sidecar(None, str(audio)))

    def test_finds_language_suffixed_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            lrc = Path(d) / "Song.en.lrc"
            lrc.write_text("[00:01.00]x")
            audio = Path(d) / "Song.mp3"
            self.assertEqual(DownloadThread._find_lrc_sidecar(None, str(audio)), str(lrc))


class TestExtractErrorClassification(unittest.TestCase):
    def test_429_inside_id_is_not_rate_limit(self):
        msg = str(format_extract_error("ERROR: [generic] video_429abc: Unsupported URL"))
        self.assertNotIn("Rate limited", msg)

    def test_capitalised_sign_in_is_auth_error(self):
        msg = str(format_extract_error("ERROR: Sign in to confirm your age"))
        self.assertIn("authentication required", msg)


if __name__ == "__main__":
    unittest.main()
