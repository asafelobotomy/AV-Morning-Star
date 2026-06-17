"""Tests for RSSExtractor and is_rss_url detection."""

import os
import sys
import types
import unittest

# Stub yt_dlp before importing extractors
if 'yt_dlp' not in sys.modules:
    _yt_dlp = types.ModuleType('yt_dlp')
    _yt_dlp.YoutubeDL = type('YoutubeDL', (object,), {'__init__': lambda self, *a, **kw: None})
    _yt_dlp_utils = types.ModuleType('yt_dlp.utils')
    _yt_dlp_utils.DownloadError = Exception
    _yt_dlp.utils = _yt_dlp_utils
    sys.modules['yt_dlp'] = _yt_dlp
    sys.modules['yt_dlp.utils'] = _yt_dlp_utils

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors import is_rss_url
from extractors.generic import GenericExtractor
from extractors.rss import RSSExtractor


class TestIsRssUrl(unittest.TestCase):
    """is_rss_url detects RSS/Atom feed URLs by path/query heuristics."""

    def test_rss_extension(self):
        self.assertTrue(is_rss_url("https://example.com/podcast.rss"))

    def test_xml_extension(self):
        self.assertTrue(is_rss_url("https://example.com/feed.xml"))

    def test_atom_extension(self):
        self.assertTrue(is_rss_url("https://example.com/feed.atom"))

    def test_feed_path_fragment(self):
        self.assertTrue(is_rss_url("https://example.com/feed/podcast"))

    def test_rss_path_fragment(self):
        self.assertTrue(is_rss_url("https://example.com/rss/episodes"))

    def test_atom_path_fragment(self):
        self.assertTrue(is_rss_url("https://example.com/atom/episodes"))

    def test_podcast_feed_path(self):
        self.assertTrue(is_rss_url("https://example.com/podcast/feed"))

    def test_format_rss_query(self):
        self.assertTrue(is_rss_url("https://example.com/channel?format=rss"))

    def test_format_atom_query(self):
        self.assertTrue(is_rss_url("https://example.com/channel?format=atom"))

    def test_youtube_url_is_not_rss(self):
        self.assertFalse(is_rss_url("https://www.youtube.com/watch?v=abc"))

    def test_vimeo_url_is_not_rss(self):
        self.assertFalse(is_rss_url("https://vimeo.com/123456"))

    def test_plain_html_url_is_not_rss(self):
        self.assertFalse(is_rss_url("https://example.com/about"))

    def test_mp3_direct_url_is_not_rss(self):
        self.assertFalse(is_rss_url("https://example.com/episode.mp3"))

    def test_malformed_url_is_not_rss(self):
        self.assertFalse(is_rss_url("not a url"))

    def test_userinfo_url_is_not_rss(self):
        self.assertFalse(is_rss_url("https://user:pass@example.com/feed.rss"))

    # --- New patterns added after audit ---

    def test_anchor_fm_podcast_rss(self):
        """Anchor/Spotify-style /podcast/rss path ending."""
        self.assertTrue(is_rss_url("https://anchor.fm/my-show/podcast/rss"))

    def test_libsyn_path_ending_rss(self):
        """Libsyn-style path ending with /rss (no extension)."""
        self.assertTrue(is_rss_url("https://traffic.libsyn.com/show/rss"))

    def test_rss_subdomain_art19(self):
        """Dedicated rss. subdomain (e.g. art19)."""
        self.assertTrue(is_rss_url("https://rss.art19.com/my-show"))

    def test_feeds_subdomain(self):
        """Dedicated feeds. subdomain (e.g. feedburner)."""
        self.assertTrue(is_rss_url("https://feeds.feedburner.com/my-podcast"))

    def test_feed_subdomain(self):
        """Dedicated feed. subdomain."""
        self.assertTrue(is_rss_url("https://feed.podbean.com/showname/feed.xml"))

    def test_rss_in_path_without_slash_suffix_is_not_false_positive(self):
        """/rss-tips does NOT contain the /rss/ fragment so should return False."""
        self.assertFalse(is_rss_url("https://example.com/rss-tips"))

    def test_path_ending_feed_without_slash(self):
        """WordPress /feed path without trailing slash."""
        self.assertTrue(is_rss_url("https://example.com/feed"))


class TestRSSExtractor(unittest.TestCase):
    """RSSExtractor is a GenericExtractor subclass with RSS-specific defaults."""

    def setUp(self):
        self.extractor = RSSExtractor("https://example.com/podcast.rss")

    def test_is_generic_extractor_subclass(self):
        self.assertIsInstance(self.extractor, GenericExtractor)

    def test_platform_name_is_podcast_rss(self):
        self.assertEqual(self.extractor.platform_name, "Podcast RSS")

    def test_fetch_opts_extract_flat_is_false(self):
        # RSS extractor needs full info, not flat playlist entries
        opts = self.extractor.get_fetch_opts()
        self.assertFalse(opts.get("extract_flat"))

    def test_cookies_passed_through(self):
        ext = RSSExtractor("https://example.com/feed.rss", cookies_from_browser="firefox")
        opts = ext.get_fetch_opts()
        self.assertIn("cookiesfrombrowser", opts)
        self.assertEqual(opts["cookiesfrombrowser"], ("firefox",))

    def test_no_cookies_by_default(self):
        opts = self.extractor.get_fetch_opts()
        self.assertNotIn("cookiesfrombrowser", opts)

    def test_parse_playlist_builds_episode_list(self):
        entries = [
            {
                'url': 'https://cdn.example.com/ep1.mp3',
                'title': 'Episode 1',
                'duration': 3600,
                'uploader': 'My Podcast',
            },
            {
                'url': 'https://cdn.example.com/ep2.mp3',
                'title': 'Episode 2',
                'duration': 1800,
                'uploader': 'My Podcast',
            },
        ]
        result = self.extractor._parse_playlist(entries)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Episode 1')
        self.assertEqual(result[0]['url'], 'https://cdn.example.com/ep1.mp3')
        self.assertEqual(result[1]['title'], 'Episode 2')

    def test_parse_playlist_skips_none_entries(self):
        entries = [None, {'url': 'https://cdn.example.com/ep.mp3', 'title': 'Ep'}]
        result = self.extractor._parse_playlist(entries)
        self.assertEqual(len(result), 1)

    def test_parse_playlist_skips_entries_without_url(self):
        entries = [{'title': 'No URL entry', 'url': '', 'id': ''}]
        result = self.extractor._parse_playlist(entries)
        self.assertEqual(len(result), 0)

    def test_parse_playlist_falls_back_to_webpage_url(self):
        entries = [{'webpage_url': 'https://example.com/ep', 'title': 'Ep via webpage_url'}]
        result = self.extractor._parse_playlist(entries)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], 'https://example.com/ep')
