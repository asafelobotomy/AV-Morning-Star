"""Detect whether a downloaded track is a music song."""

from urllib.parse import urlparse

_MUSIC_HOSTNAMES: frozenset[str] = frozenset({
    'music.youtube.com',
    'soundcloud.com',
    'bandcamp.com',
    'tidal.com',
    'deezer.com',
    'open.spotify.com',
    'music.amazon.com',
    'music.apple.com',
})


def is_music_track(info: dict) -> bool:
    """Return True when the yt-dlp info dict represents a music track.

    Primary signal: both ``track`` and ``artist`` fields are populated
    (yt-dlp sets these for dedicated music extractors such as YouTube Music,
    Deezer, SoundCloud, and Bandcamp).

    Secondary signal: the source URL belongs to a known music platform.
    """
    if info.get('track') and info.get('artist'):
        return True
    url = info.get('webpage_url') or info.get('url') or ''
    return _hostname_is_music(url)


def is_youtube_music_url(url: str) -> bool:
    """Return True when *url* points to YouTube Music."""
    return 'music.youtube.com' in (urlparse(url).hostname or '')


def _hostname_is_music(url: str) -> bool:
    hostname = urlparse(url).hostname or ''
    hostname = hostname.removeprefix('www.')
    if hostname in _MUSIC_HOSTNAMES:
        return True
    # Handle artist subdomains, e.g. artist.bandcamp.com → bandcamp.com
    for music_host in _MUSIC_HOSTNAMES:
        if hostname.endswith(f'.{music_host}'):
            return True
    return False
