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

from extractors.base import (
    AUDIO_DENOISE_FILTER,
    AUDIO_DYNAUDNORM_FILTER,
    AUDIO_LOUDNORM_FILTER,
    VIDEO_DENOISE_FILTER,
    VIDEO_SHARPEN_FILTER,
    BaseExtractor,
)
from extractors.ytdlp_format_opts import build_audio_opts, build_video_opts

# ---------------------------------------------------------------------------
# PodcastPageExtractor — _is_audio_url
# ---------------------------------------------------------------------------

class TestBaseExtractorOptions(unittest.TestCase):
    """BaseExtractor builds correct yt-dlp option dicts."""

    def setUp(self):
        self.extractor = BaseExtractor("http://example.com/video")

    def test_cookies_absent_by_default(self):
        opts = self.extractor.get_base_ydl_opts()
        self.assertNotIn("cookiesfrombrowser", opts)

    def test_cookies_injected_when_provided(self):
        ext = BaseExtractor("http://example.com/video", cookies_from_browser="firefox")
        opts = ext.get_base_ydl_opts()
        self.assertIn("cookiesfrombrowser", opts)
        self.assertEqual(opts["cookiesfrombrowser"], ("firefox",))

    def test_cookies_none_does_not_inject(self):
        ext = BaseExtractor("http://example.com/video", cookies_from_browser=None)
        opts = ext.get_base_ydl_opts()
        self.assertNotIn("cookiesfrombrowser", opts)

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
        opts = build_video_opts("1080p", **kwargs)
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
        opts = build_video_opts("1080p")
        self.assertNotIn("postprocessor_args", opts)

    # --- Audio filter chains ---

    def _get_audio_postprocessor_args(self, normalize=False, denoise=False, dynamic=False):
        opts = build_audio_opts("mp3", "192", False, normalize, denoise, dynamic)
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
        opts = build_audio_opts("mp3", "192", False, False, False, False)
        self.assertNotIn("postprocessor_args", opts)
