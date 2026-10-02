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
        return opts.get("postprocessor_args", {}).get("copystream", [])

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

    def test_filters_use_copystream_not_videoconvertor(self):
        """FFmpegVideoConvertor skips same-container files, so filters would never run."""
        opts = build_video_opts("1080p", denoise_video=True)
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertIn("FFmpegCopyStream", keys)
        self.assertNotIn("FFmpegVideoConvertor", keys)

    def test_subtitle_embed_survives_video_filters(self):
        """Subtitle embedding and filter postprocessors must both be present."""
        opts = self.extractor.get_download_opts(
            "/tmp", "%(title)s.%(ext)s", "video", download_subs=True, denoise_video=True,
        )
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertEqual(keys, ["FFmpegEmbedSubtitle", "FFmpegCopyStream"])

    # --- Codec stream copy when only one stream has a filter ---

    def _get_video_convertor_args(self, **kwargs):
        opts = build_video_opts("1080p", **kwargs)
        return opts.get("postprocessor_args", {}).get("copystream", [])

    def test_video_only_filter_copies_audio_stream(self):
        """When only a video filter is active the audio stream must be copied."""
        args = self._get_video_convertor_args(denoise_video=True)
        self.assertIn("-c:a", args)
        self.assertEqual(args[args.index("-c:a") + 1], "copy")

    def test_audio_only_filter_copies_video_stream(self):
        """When only an audio filter is active the video stream must be copied."""
        args = self._get_video_convertor_args(normalize_video_audio=True)
        self.assertIn("-c:v", args)
        self.assertEqual(args[args.index("-c:v") + 1], "copy")

    def test_both_filters_encode_both_streams(self):
        """When both stream types have filters, both are re-encoded (not copied)."""
        args = self._get_video_convertor_args(denoise_video=True, normalize_video_audio=True)
        self.assertIn("-c:v", args)
        self.assertNotEqual(args[args.index("-c:v") + 1], "copy")
        self.assertIn("-c:a", args)
        self.assertNotEqual(args[args.index("-c:a") + 1], "copy")

    def test_webm_video_filter_uses_vp9(self):
        args = self._get_video_convertor_args(video_container="webm", denoise_video=True)
        self.assertIn("-c:v", args)
        self.assertEqual(args[args.index("-c:v") + 1], "libvpx-vp9")

    def test_webm_audio_filter_copies_video(self):
        args = self._get_video_convertor_args(video_container="webm", normalize_video_audio=True)
        self.assertIn("-c:v", args)
        self.assertEqual(args[args.index("-c:v") + 1], "copy")
        self.assertIn("-c:a", args)
        self.assertEqual(args[args.index("-c:a") + 1], "libopus")

    # --- Audio postprocessor ordering ---

    def test_audio_metadata_before_thumbnail(self):
        """FFmpegMetadata must appear before EmbedThumbnail in the pipeline."""
        opts = build_audio_opts("mp3", "192", embed_thumbnail=True,
                                normalize_audio=False, denoise_audio=False,
                                dynamic_normalization=False)
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertIn("FFmpegMetadata", keys)
        self.assertIn("EmbedThumbnail", keys)
        self.assertLess(keys.index("FFmpegMetadata"), keys.index("EmbedThumbnail"))

    def test_audio_metadata_present_without_thumbnail(self):
        opts = build_audio_opts("mp3", "192", embed_thumbnail=False,
                                normalize_audio=False, denoise_audio=False,
                                dynamic_normalization=False)
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertIn("FFmpegMetadata", keys)
        self.assertNotIn("EmbedThumbnail", keys)

    # --- Audio filter chains ---

    def _get_audio_postprocessor_args(self, normalize=False, denoise=False, dynamic=False):
        opts = build_audio_opts("mp3", "192", False, normalize, denoise, dynamic)
        return opts.get("postprocessor_args", {}).get("copystream", [])

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

    def test_dynamic_normalization_works_without_ebu_checkbox(self):
        """The UI exposes Dynamic Normalization as its own checkbox."""
        args = self._get_audio_postprocessor_args(normalize=False, dynamic=True)
        self.assertIn("-af", args)
        af_value = args[args.index("-af") + 1]
        self.assertIn(AUDIO_DYNAUDNORM_FILTER, af_value)
        self.assertNotIn(AUDIO_LOUDNORM_FILTER, af_value)

    def test_audio_filters_run_after_extract_before_metadata(self):
        """Filters need their own pass: ExtractAudio stream-copies same-codec sources."""
        opts = build_audio_opts("opus", "192", True, True, False, False)
        keys = [pp["key"] for pp in opts["postprocessors"]]
        self.assertEqual(
            keys, ["FFmpegExtractAudio", "FFmpegCopyStream", "FFmpegMetadata", "EmbedThumbnail"],
        )
        args = opts["postprocessor_args"]["copystream"]
        self.assertEqual(args[args.index("-c:a") + 1], "libopus")
        self.assertEqual(args[args.index("-b:a") + 1], "192k")

    def test_lossless_audio_filter_pass_has_no_bitrate(self):
        opts = build_audio_opts("flac", "0", False, True, False, False)
        args = opts["postprocessor_args"]["copystream"]
        self.assertEqual(args[args.index("-c:a") + 1], "flac")
        self.assertNotIn("-b:a", args)

    def test_no_audio_filters_no_postprocessor_args(self):
        opts = build_audio_opts("mp3", "192", False, False, False, False)
        self.assertNotIn("postprocessor_args", opts)
