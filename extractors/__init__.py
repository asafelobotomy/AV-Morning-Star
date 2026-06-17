"""
Platform-specific video extractors for AV Morning Star
"""

from urllib.parse import urlparse

from .base import BaseExtractor
from .generic import GenericExtractor
from .platform_names import platform_name_for_url
from .podcast_page import PodcastPageExtractor
from .rss import RSSExtractor
from .youtube_ytdlp import YouTubeExtractor  # Using yt-dlp backend for PO token support

__all__ = [
    'BaseExtractor',
    'YouTubeExtractor',
    'GenericExtractor',
    'PodcastPageExtractor',
    'RSSExtractor',
    'get_extractor',
    'is_youtube_url',
    'is_rss_url',
    'platform_name_for_url',
]

# Allowed hostnames per extractor.  Matching is done against the parsed hostname
# only (never the full URL string) to prevent userinfo-confusion attacks such as
# https://evil.com@youtube.com/ routing to the wrong extractor.
_YOUTUBE_HOSTS = {'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com'}
_PODCAST_HOSTS = {'fat-pie.com', 'www.fat-pie.com'}

# Path suffixes and path fragments that indicate an RSS / Atom feed URL.
_RSS_EXTENSIONS = ('.rss', '.xml', '.atom')
_RSS_PATH_FRAGMENTS = ('/feed/', '/rss/', '/atom/', '/podcast/feed', '/podcasts/feed')
_RSS_QUERY_FRAGMENTS = ('format=rss', 'format=atom', 'format=feed', 'feed=rss')


def is_youtube_url(url: str) -> bool:
    """Return True if *url* is a YouTube URL.

    Uses the same hardened parsed-hostname check as the extractor factory, so
    it is immune to userinfo-confusion attacks such as
    https://youtube.com@evil.example/ returning a false positive.
    """
    return _hostname(url) in _YOUTUBE_HOSTS


def is_rss_url(url: str) -> bool:
    """Return True if *url* looks like an RSS / Atom / podcast feed.

    Detection is heuristic and purely URL-based — no network request is made.
    Checked in order:
      1. URL path ends with a known feed extension (.rss, .xml, .atom)
      2. URL path contains a known feed path fragment (/feed/, /rss/, etc.)
      3. URL query string contains a known feed format indicator
    """
    try:
        parsed = urlparse(url)
        if parsed.username or parsed.password:
            return False
        path = (parsed.path or '').lower()
        query = (parsed.query or '').lower()
    except Exception:
        return False

    if any(path.endswith(ext) for ext in _RSS_EXTENSIONS):
        return True
    if any(frag in path for frag in _RSS_PATH_FRAGMENTS):
        return True
    if any(frag in query for frag in _RSS_QUERY_FRAGMENTS):
        return True
    return False


def _hostname(url: str) -> str:
    """Return the lowercased hostname of *url*, or an empty string on parse failure."""
    try:
        parsed = urlparse(url)
        # Reject URLs that embed userinfo (e.g. user@host) as a safety measure.
        if parsed.username or parsed.password:
            return ''
        return (parsed.hostname or '').lower()
    except Exception:
        return ''


def get_extractor(url, cookies_from_browser=None):
    """
    Factory function to get the appropriate extractor for a URL

    Args:
        url: Video URL to extract from
        cookies_from_browser: Browser name to extract cookies from (e.g., 'firefox', 'chrome', 'brave')
                             Passed to all yt-dlp-backed extractors.  If None, uses unauthenticated access.

    Returns:
        An instance of the appropriate extractor class
    """
    host = _hostname(url)

    if host in _YOUTUBE_HOSTS:
        return YouTubeExtractor(url, cookies_from_browser=cookies_from_browser)

    if host in _PODCAST_HOSTS:
        return PodcastPageExtractor(url)

    if is_rss_url(url):
        return RSSExtractor(url, cookies_from_browser=cookies_from_browser)

    # Odysee/LBRY and all other yt-dlp-supported sites use the generic backend.
    return GenericExtractor(url, cookies_from_browser=cookies_from_browser)
