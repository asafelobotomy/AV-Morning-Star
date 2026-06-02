"""
Tests for browser detection utilities.

Covers:
- detect_available_browsers: return type and valid browser names
- get_default_browser: preference ordering (YouTube cookies > available > none)
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure the workspace root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import detect_available_browsers, get_default_browser


class TestDetectAvailableBrowsers(unittest.TestCase):
    """detect_available_browsers inspects the filesystem for browser cookie paths."""

    KNOWN_BROWSERS = {"brave", "firefox", "chrome", "chromium", "edge", "opera", "vivaldi", "safari"}

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


class TestGetDefaultBrowser(unittest.TestCase):
    """get_default_browser respects the preference order: YouTube cookies > available > 'none'."""

    def test_returns_a_string(self):
        result = get_default_browser()
        self.assertIsInstance(result, str)

    def test_returns_none_string_when_nothing_found(self):
        with patch("browser_utils.get_browsers_with_youtube_cookies", return_value=[]):
            with patch("browser_utils.detect_available_browsers", return_value=[]):
                result = get_default_browser()
        self.assertEqual(result, "none")

    def test_prefers_youtube_authenticated_browser(self):
        with patch("browser_utils.get_browsers_with_youtube_cookies", return_value=["firefox"]):
            result = get_default_browser()
        self.assertEqual(result, "firefox")

    def test_falls_back_to_first_available_when_no_youtube_cookies(self):
        with patch("browser_utils.get_browsers_with_youtube_cookies", return_value=[]):
            with patch("browser_utils.detect_available_browsers", return_value=["brave", "chrome"]):
                result = get_default_browser()
        self.assertEqual(result, "brave")

    def test_youtube_browser_takes_precedence_over_available(self):
        """When two different browsers are found, the YouTube-authenticated one wins."""
        with patch("browser_utils.get_browsers_with_youtube_cookies", return_value=["chrome"]):
            with patch("browser_utils.detect_available_browsers", return_value=["brave", "chrome"]):
                result = get_default_browser()
        self.assertEqual(result, "chrome")


if __name__ == "__main__":
    unittest.main()
