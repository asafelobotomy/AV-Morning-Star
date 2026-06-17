"""
Tests for browser detection utilities.

Covers:
- detect_available_browsers: return type and valid browser names
- Chromium profile detection including Opera flat cookie path
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import _has_chromium_cookies, _has_firefox_cookies, detect_available_browsers


class TestDetectAvailableBrowsers(unittest.TestCase):
    """detect_available_browsers inspects the filesystem for browser cookie paths."""

    KNOWN_BROWSERS = {"brave", "firefox", "chrome", "chromium", "edge", "opera", "vivaldi"}

    def test_returns_a_list(self):
        result = detect_available_browsers()
        self.assertIsInstance(result, list)

    def test_only_known_browser_names_returned(self):
        result = detect_available_browsers()
        for browser in result:
            self.assertIn(browser, self.KNOWN_BROWSERS, f"Unexpected browser name: {browser!r}")

    def test_no_duplicates(self):
        result = detect_available_browsers()
        self.assertEqual(len(result), len(set(result)), "Duplicate browser names in result")

    def test_detects_chromium_profile_cookies(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = os.path.join(tmp, 'Profile 1')
            os.makedirs(profile)
            open(os.path.join(profile, 'Cookies'), 'w').close()
            self.assertTrue(_has_chromium_cookies(tmp))

    def test_detects_opera_flat_cookie_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            open(os.path.join(tmp, 'Cookies'), 'w').close()
            self.assertTrue(_has_chromium_cookies(tmp))

    def test_detects_firefox_profile_cookies(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = os.path.join(tmp, 'abc.default-release')
            os.makedirs(profile)
            open(os.path.join(profile, 'cookies.sqlite'), 'w').close()
            with patch('browser_utils._FIREFOX_ROOTS', [tmp]):
                self.assertTrue(_has_firefox_cookies())


if __name__ == "__main__":
    unittest.main()
