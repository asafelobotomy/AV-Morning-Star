"""
Platform-specific video extractors for AV Morning Star
"""

from .base import BaseExtractor
from .youtube_ytdlp import YouTubeExtractor  # Using yt-dlp backend for PO token support
from .odysee import OdyseeExtractor
from .generic import GenericExtractor

__all__ = ['BaseExtractor', 'YouTubeExtractor', 'OdyseeExtractor', 'GenericExtractor', 'get_extractor']


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
    url_lower = url.lower()
    
    # YouTube detection
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return YouTubeExtractor(url, cookies_from_browser=cookies_from_browser)
    
    # Odysee detection
    elif 'odysee.com' in url_lower or 'lbry.tv' in url_lower:
        return OdyseeExtractor(url)
    
    # Generic fallback for all other sites
    else:
        return GenericExtractor(url)
