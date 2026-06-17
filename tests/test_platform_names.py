"""Tests for extractors/platform_names.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.platform_names import platform_name_for_url


class TestPlatformNameForUrl(unittest.TestCase):
    """platform_name_for_url maps hostnames to human-readable names."""

    def _name(self, url):
        return platform_name_for_url(url)

    # Known platforms
    def test_youtube_com(self):
        self.assertEqual(self._name("https://www.youtube.com/watch?v=abc"), "YouTube")

    def test_youtu_be(self):
        self.assertEqual(self._name("https://youtu.be/abc"), "YouTube")

    def test_vimeo(self):
        self.assertEqual(self._name("https://vimeo.com/12345"), "Vimeo")

    def test_www_vimeo(self):
        self.assertEqual(self._name("https://www.vimeo.com/12345"), "Vimeo")

    def test_twitch(self):
        self.assertEqual(self._name("https://twitch.tv/channel"), "Twitch")

    def test_tiktok(self):
        self.assertEqual(self._name("https://www.tiktok.com/@user/video/123"), "TikTok")

    def test_rumble(self):
        self.assertEqual(self._name("https://rumble.com/v-video.html"), "Rumble")

    def test_odysee(self):
        self.assertEqual(self._name("https://odysee.com/@channel/video"), "Odysee")

    def test_soundcloud(self):
        self.assertEqual(self._name("https://soundcloud.com/artist/track"), "SoundCloud")

    def test_twitter_x(self):
        self.assertEqual(self._name("https://twitter.com/user/status/123"), "Twitter/X")

    def test_x_com(self):
        self.assertEqual(self._name("https://x.com/user/status/123"), "Twitter/X")

    def test_instagram(self):
        self.assertEqual(self._name("https://www.instagram.com/p/abc"), "Instagram")

    def test_archive_org(self):
        self.assertEqual(self._name("https://archive.org/details/video"), "Internet Archive")

    def test_bbc(self):
        self.assertEqual(self._name("https://www.bbc.co.uk/iplayer/episode/abc"), "BBC")

    # Unknown hostnames fall back to the hostname
    def test_unknown_host_returns_hostname(self):
        result = self._name("https://example.com/video")
        self.assertEqual(result, "example.com")

    def test_subdomain_unknown_returns_full_hostname(self):
        result = self._name("https://video.example.com/path")
        # example.com is not in the map; falls back to the full hostname
        self.assertEqual(result, "video.example.com")

    # Edge cases
    def test_empty_string_returns_unknown(self):
        self.assertEqual(self._name(""), "Unknown")

    def test_malformed_url_returns_unknown(self):
        self.assertEqual(self._name("not a url"), "Unknown")

    def test_subdomain_of_known_host(self):
        # player.vimeo.com → Vimeo
        self.assertEqual(self._name("https://player.vimeo.com/video/123"), "Vimeo")
