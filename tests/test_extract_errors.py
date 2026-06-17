"""Tests for extractors/extract_errors.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.extract_errors import format_extract_error


def _msg(error_text):
    """Return the message string from format_extract_error."""
    return str(format_extract_error(error_text))


class TestDRMError(unittest.TestCase):
    def test_known_to_use_drm_protection(self):
        msg = _msg("The requested site is known to use DRM protection. It will NOT be supported.")
        self.assertIn("DRM", msg)
        self.assertIn("platform restriction", msg)

    def test_drm_not_be_supported_pattern(self):
        msg = _msg("drm content will not be supported here")
        self.assertIn("DRM", msg)


class TestGeoError(unittest.TestCase):
    def test_not_available_in_your_country(self):
        msg = _msg("This video is not available in your country.")
        self.assertIn("region", msg.lower())
        self.assertIn("VPN", msg)

    def test_geo_restriction(self):
        msg = _msg("geo restriction detected for this content")
        self.assertIn("region", msg.lower())

    def test_georestrict_keyword(self):
        msg = _msg("ERROR: georestricted content")
        self.assertIn("region", msg.lower())


class TestLoginRequired(unittest.TestCase):
    def test_login_required(self):
        msg = _msg("This video is available for members only. login required")
        self.assertIn("Preferences", msg)

    def test_members_only(self):
        msg = _msg("members only content")
        self.assertIn("logged in", msg.lower())

    def test_subscriber_only(self):
        msg = _msg("subscriber only episode")
        self.assertIn("logged in", msg.lower())


class TestRateLimit(unittest.TestCase):
    def test_rate_limit_message(self):
        msg = _msg("rate-limit exceeded for this IP")
        self.assertIn("wait", msg.lower())

    def test_too_many_requests(self):
        msg = _msg("too many requests, try again later")
        self.assertIn("wait", msg.lower())

    def test_http_429(self):
        msg = _msg("HTTP Error 429: Too Many Requests")
        self.assertIn("wait", msg.lower())


class TestContentRemoved(unittest.TestCase):
    def test_video_removed(self):
        msg = _msg("This video has been removed by the uploader.")
        self.assertIn("private or unavailable", msg.lower())

    def test_video_unavailable(self):
        msg = _msg("Video unavailable")
        self.assertIn("private or unavailable", msg.lower())

    def test_private_video(self):
        msg = _msg("This is a private video.")
        self.assertIn("private", msg.lower())


class TestYouTubeSpecific(unittest.TestCase):
    def test_n_challenge_solving_failed(self):
        msg = _msg("n challenge solving failed for xyz")
        self.assertIn("YouTube", msg)
        self.assertIn("anti-bot", msg.lower())

    def test_sign_in_required(self):
        msg = _msg("Sign in to confirm you're not a bot")
        self.assertIn("YouTube", msg)
        self.assertIn("login", msg.lower())

    def test_format_not_available(self):
        msg = _msg("Requested format is not available")
        self.assertIn("downloaded", msg.lower())

    def test_only_images_available(self):
        msg = _msg("Only images are available for this URL")
        self.assertIn("not available for download", msg.lower())


class TestFallthrough(unittest.TestCase):
    def test_unrecognised_error_includes_original(self):
        original = "some bizarre yt-dlp error XYZ-999"
        msg = _msg(original)
        self.assertIn("XYZ-999", msg)

    def test_fallthrough_includes_preferences_hint(self):
        msg = _msg("completely unknown error")
        self.assertIn("Preferences", msg)
