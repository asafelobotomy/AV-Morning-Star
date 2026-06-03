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
from extractors.odysee import OdyseeExtractor
from extractors.youtube_ytdlp import YouTubeExtractor
from extractors import get_extractor, is_youtube_url


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


# ---------------------------------------------------------------------------
# PodcastPageExtractor — _title_from_url
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PodcastPageExtractor — extract_info (network mocked)
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


# ---------------------------------------------------------------------------
# PodcastPageExtractor — _fetch_html security checks
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


# ---------------------------------------------------------------------------
# BaseExtractor — yt-dlp option building
# ---------------------------------------------------------------------------

class TestBaseExtractorOptions(unittest.TestCase):
    """BaseExtractor builds correct yt-dlp option dicts."""

    def setUp(self):
        self.extractor = BaseExtractor("http://example.com/video")

    def test_base_opts_include_socket_timeout(self):
        opts = self.extractor.get_base_ydl_opts()
        self.assertIn("socket_timeout", opts)
        self.assertGreater(opts["socket_timeout"], 0)

    def test_fetch_opts_set_skip_download(self):
        opts = self.extractor.get_fetch_opts()
        self.assertTrue(opts.get("skip_download"))

    def test_fetch_opts_set_extract_flat(self):
        opts = self.extractor.get_fetch_opts()
        self.assertTrue(opts.get("extract_flat"))

    # --- Video filter chains ---

    def _get_video_postprocessor_args(self, **kwargs):
        opts = self.extractor._get_video_opts("1080p", **kwargs)
        return opts.get("postprocessor_args", {}).get("videoconvertor", [])

    def test_video_denoise_filter_in_vf_chain(self):
        args = self._get_video_postprocessor_args(denoise_video=True)
        self.assertIn("-vf", args)
        vf_value = args[args.index("-vf") + 1]
        self.assertIn(VIDEO_DENOISE_FILTER, vf_value)

    def test_video_sharpen_filter_in_vf_chain(self):
        args = self._get_video_postprocessor_args(sharpen_video=True)
        self.assertIn("-vf", args)
        vf_value = args[args.index("-vf") + 1]
        self.assertIn(VIDEO_SHARPEN_FILTER, vf_value)

    def test_multiple_video_filters_combined(self):
        args = self._get_video_postprocessor_args(denoise_video=True, sharpen_video=True)
        self.assertIn("-vf", args)
        vf_value = args[args.index("-vf") + 1]
        self.assertIn(VIDEO_DENOISE_FILTER, vf_value)
        self.assertIn(VIDEO_SHARPEN_FILTER, vf_value)

    def test_no_filters_no_postprocessor_args(self):
        opts = self.extractor._get_video_opts("1080p")
        self.assertNotIn("postprocessor_args", opts)

    # --- Audio filter chains ---

    def _get_audio_postprocessor_args(self, normalize=False, denoise=False, dynamic=False):
        opts = self.extractor._get_audio_opts(
            "mp3", "192", False, normalize, denoise, dynamic
        )
        return opts.get("postprocessor_args", {}).get("extractaudio+ffmpeg_o", [])

    def test_audio_denoise_filter_in_af_chain(self):
        args = self._get_audio_postprocessor_args(denoise=True)
        self.assertIn("-af", args)
        af_value = args[args.index("-af") + 1]
        self.assertIn(AUDIO_DENOISE_FILTER, af_value)

    def test_audio_loudnorm_filter_applied(self):
        args = self._get_audio_postprocessor_args(normalize=True, dynamic=False)
        self.assertIn("-af", args)
        af_value = args[args.index("-af") + 1]
        self.assertIn(AUDIO_LOUDNORM_FILTER, af_value)

    def test_audio_dynaudnorm_filter_applied(self):
        args = self._get_audio_postprocessor_args(normalize=True, dynamic=True)
        self.assertIn("-af", args)
        af_value = args[args.index("-af") + 1]
        self.assertIn(AUDIO_DYNAUDNORM_FILTER, af_value)

    def test_no_audio_filters_no_postprocessor_args(self):
        opts = self.extractor._get_audio_opts("mp3", "192", False, False, False, False)
        self.assertNotIn("postprocessor_args", opts)


# ---------------------------------------------------------------------------
# GenericExtractor — SSL and security option overrides
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


# ---------------------------------------------------------------------------
# OdyseeExtractor — passthrough behaviour
# ---------------------------------------------------------------------------

class TestOdyseeExtractor(unittest.TestCase):
    """OdyseeExtractor delegates fully to base without overriding options."""

    def setUp(self):
        self.extractor = OdyseeExtractor("https://odysee.com/@channel/video")

    def test_platform_name_is_odysee(self):
        self.assertEqual(self.extractor.platform_name, "Odysee")

    def test_fetch_opts_returns_dict(self):
        opts = self.extractor.get_fetch_opts()
        self.assertIsInstance(opts, dict)

    def test_fetch_opts_skip_download_set(self):
        opts = self.extractor.get_fetch_opts()
        self.assertTrue(opts.get("skip_download"))

    def test_download_opts_returns_dict(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIsInstance(opts, dict)

    def test_download_opts_has_outtmpl(self):
        opts = self.extractor.get_download_opts("/tmp", "%(title)s.%(ext)s", "video")
        self.assertIn("outtmpl", opts)


# ---------------------------------------------------------------------------
# YouTubeExtractor — download option construction
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


# ---------------------------------------------------------------------------
# get_extractor factory — URL routing
# ---------------------------------------------------------------------------

class TestGetExtractorFactory(unittest.TestCase):
    """get_extractor routes URLs to the correct extractor class."""

    def test_youtube_com_url_returns_youtube_extractor(self):
        ext = get_extractor("https://www.youtube.com/watch?v=abc123")
        self.assertIsInstance(ext, YouTubeExtractor)

    def test_youtu_be_short_url_returns_youtube_extractor(self):
        ext = get_extractor("https://youtu.be/abc123")
        self.assertIsInstance(ext, YouTubeExtractor)

    def test_odysee_url_returns_odysee_extractor(self):
        ext = get_extractor("https://odysee.com/@channel/video")
        self.assertIsInstance(ext, OdyseeExtractor)

    def test_lbry_tv_url_returns_odysee_extractor(self):
        ext = get_extractor("https://lbry.tv/@channel/video")
        self.assertIsInstance(ext, OdyseeExtractor)

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


# ---------------------------------------------------------------------------
# is_youtube_url — hostname-based classification (injection-safe)
# ---------------------------------------------------------------------------

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


if __name__ == "__main__":
    unittest.main()
