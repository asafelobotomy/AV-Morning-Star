"""Tests for constants/drm_hosts.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants.drm_hosts import DRM_HOSTS, drm_display_name, is_drm_host


class TestIsDrmHost(unittest.TestCase):
    """is_drm_host correctly identifies known DRM domains."""

    def test_netflix_is_drm(self):
        self.assertTrue(is_drm_host("www.netflix.com"))

    def test_spotify_is_drm(self):
        self.assertTrue(is_drm_host("open.spotify.com"))

    def test_disney_plus_is_drm(self):
        self.assertTrue(is_drm_host("www.disneyplus.com"))

    def test_prime_video_is_drm(self):
        self.assertTrue(is_drm_host("www.primevideo.com"))

    def test_hulu_is_drm(self):
        self.assertTrue(is_drm_host("www.hulu.com"))

    def test_apple_tv_is_drm(self):
        self.assertTrue(is_drm_host("tv.apple.com"))

    def test_rakuten_tv_eu_is_drm(self):
        self.assertTrue(is_drm_host("www.rakuten.tv"))

    def test_rakuten_tv_jp_is_drm(self):
        self.assertTrue(is_drm_host("tv.rakuten.co.jp"))

    def test_crunchyroll_is_drm(self):
        self.assertTrue(is_drm_host("www.crunchyroll.com"))

    def test_youtube_is_not_drm(self):
        self.assertFalse(is_drm_host("www.youtube.com"))

    def test_vimeo_is_not_drm(self):
        self.assertFalse(is_drm_host("vimeo.com"))

    def test_odysee_is_not_drm(self):
        self.assertFalse(is_drm_host("odysee.com"))

    def test_unknown_host_is_not_drm(self):
        self.assertFalse(is_drm_host("example.com"))

    def test_empty_string_is_not_drm(self):
        self.assertFalse(is_drm_host(""))

    def test_case_insensitive(self):
        self.assertTrue(is_drm_host("WWW.NETFLIX.COM"))
        self.assertTrue(is_drm_host("Open.Spotify.Com"))

    # --- New entries added after yt-dlp supported-sites review ---

    def test_amazon_music_us_is_drm(self):
        self.assertTrue(is_drm_host("music.amazon.com"))

    def test_amazon_music_uk_is_drm(self):
        self.assertTrue(is_drm_host("music.amazon.co.uk"))

    def test_amazon_music_de_is_drm(self):
        self.assertTrue(is_drm_host("music.amazon.de"))

    def test_apple_music_is_drm(self):
        self.assertTrue(is_drm_host("music.apple.com"))

    def test_amazon_prime_video_is_not_amazon_music(self):
        """primevideo.com is already blocked; music.amazon.* is a separate entry."""
        self.assertTrue(is_drm_host("music.amazon.com"))
        self.assertTrue(is_drm_host("www.primevideo.com"))

    def test_regular_amazon_shopping_is_not_drm(self):
        """amazon.com (shopping) is NOT in DRM_HOSTS."""
        self.assertFalse(is_drm_host("amazon.com"))
        self.assertFalse(is_drm_host("www.amazon.com"))


class TestDrmDisplayName(unittest.TestCase):
    """drm_display_name returns friendly service names."""

    def test_spotify_display_name(self):
        self.assertEqual(drm_display_name("open.spotify.com"), "Spotify")

    def test_disney_plus_display_name(self):
        self.assertEqual(drm_display_name("www.disneyplus.com"), "Disney+")

    def test_rakuten_display_name(self):
        self.assertEqual(drm_display_name("www.rakuten.tv"), "Rakuten TV")

    def test_unknown_host_returns_hostname(self):
        self.assertEqual(drm_display_name("some.unknown.host"), "some.unknown.host")

    def test_amazon_music_display_name(self):
        self.assertEqual(drm_display_name("music.amazon.com"), "Amazon Music")

    def test_amazon_music_uk_display_name(self):
        self.assertEqual(drm_display_name("music.amazon.co.uk"), "Amazon Music")

    def test_apple_music_display_name(self):
        self.assertEqual(drm_display_name("music.apple.com"), "Apple Music")


class TestDrmHostsSet(unittest.TestCase):
    """DRM_HOSTS frozenset sanity checks."""

    def test_is_frozenset(self):
        self.assertIsInstance(DRM_HOSTS, frozenset)

    def test_has_significant_count(self):
        # Should have at least 30 known DRM services
        self.assertGreater(len(DRM_HOSTS), 30)

    def test_all_entries_lowercase(self):
        for host in DRM_HOSTS:
            self.assertEqual(host, host.lower(), f"{host!r} is not lowercase")
