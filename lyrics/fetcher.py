"""Fetch lyrics from LRCLIB (lrclib.net).

LRCLIB is a completely free, crowdsourced lyrics database with no API key,
no rate limiting, and CORS support.  It returns both time-synced LRC text
and a plain-text fallback in a single JSON response.

See https://lrclib.net/docs for the full API reference.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

_BASE = 'https://lrclib.net/api'
_USER_AGENT = 'AV-Morning-Star/1.0 (https://github.com/asafelobotomy/AV-Morning-Star)'
_TIMEOUT = 10


def _get(path: str, params: dict) -> dict | None:
    url = f'{_BASE}{path}?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError):
        pass
    return None


def fetch_lyrics(
    track_name: str,
    artist_name: str,
    album_name: str = '',
    duration: float | None = None,
) -> tuple[str | None, str | None]:
    """Return ``(synced_lrc, plain_text)`` for the given track.

    Either element may be ``None`` if that format is unavailable.
    Both are ``None`` when the track is not found or on network error.

    Strategy
    --------
    1. Exact-signature lookup via ``/api/get`` (requires all four fields;
       LRCLIB uses duration ±2 s to disambiguate live vs. studio versions).
    2. Keyword search via ``/api/search`` as a graceful fallback when the
       album or duration are missing or when the exact lookup returns 404.
    """
    if not track_name or not artist_name:
        return None, None

    result = None
    if album_name and duration is not None:
        result = _get('/get', {
            'track_name': track_name,
            'artist_name': artist_name,
            'album_name': album_name,
            'duration': int(duration),
        })

    if not result:
        results = _get('/search', {
            'track_name': track_name,
            'artist_name': artist_name,
        })
        if results and isinstance(results, list):
            result = results[0]

    if not result:
        return None, None

    if result.get('instrumental'):
        return None, None

    synced = result.get('syncedLyrics') or None
    plain = result.get('plainLyrics') or None
    return synced, plain
