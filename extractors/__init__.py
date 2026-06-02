"""
Platform-specific video extractors for AV Morning Star
"""

from urllib.parse import urlparse

from .base import BaseExtractor
from .youtube_ytdlp import YouTubeExtractor  # Using yt-dlp backend for PO token support
from .odysee import OdyseeExtractor
from .generic import GenericExtractor
from .podcast_page import PodcastPageExtractor

__all__ = ['BaseExtractor', 'YouTubeExtractor', 'OdyseeExtractor', 'GenericExtractor', 'PodcastPageExtractor', 'get_extractor', 'is_youtube_url']

# Allowed hostnames per extractor.  Matching is done against the parsed hostname
# only (never the full URL string) to prevent userinfo-confusion attacks such as
# https://evil.com@youtube.com/ routing to the wrong extractor.
_YOUTUBE_HOSTS = {'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com'}
_ODYSEE_HOSTS = {'odysee.com', 'www.odysee.com', 'lbry.tv', 'www.lbry.tv'}
_PODCAST_HOSTS = {'fat-pie.com', 'www.fat-pie.com'}


def is_youtube_url(url: str) -> bool:
    """Return True if *url* is a YouTube URL.

    Uses the same hardened parsed-hostname check as the extractor factory, so
    it is immune to userinfo-confusion attacks such as
    https://youtube.com@evil.example/ returning a false positive.
    """
    return _hostname(url) in _YOUTUBE_HOSTS


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
                             Only used for YouTube. If None, uses unauthenticated access.
        
    Returns:
        An instance of the appropriate extractor class
    """
    host = _hostname(url)

    # YouTube detection
    if host in _YOUTUBE_HOSTS:
        return YouTubeExtractor(url, cookies_from_browser=cookies_from_browser)

    # Odysee detection
    elif host in _ODYSEE_HOSTS:
        return OdyseeExtractor(url)

    # Direct-download podcast pages
    elif host in _PODCAST_HOSTS:
        return PodcastPageExtractor(url)

    # Generic fallback for all other sites
    else:
        return GenericExtractor(url)
