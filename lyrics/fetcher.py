"""Fetch lyrics from LRCLIB with syncedlyrics multi-provider fallback.

Primary source: LRCLIB (lrclib.net) — free, no API key, returns both synced
LRC and plain text in one response.

Fallback: syncedlyrics aggregates Musixmatch, NetEase, Megalobiz, and Genius
when LRCLIB has no match (common for CJK tracks on NetEase).
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from .embedder import is_lrc_format, strip_lrc_tags

_BASE = 'https://lrclib.net/api'
_USER_AGENT = 'AV-Morning-Star/1.0 (https://github.com/asafelobotomy/AV-Morning-Star)'
_TIMEOUT = 10

# Exclude Lrclib — already queried directly above.
_SYNCEDLYRICS_PROVIDERS = ['Musixmatch', 'NetEase', 'Megalobiz', 'Genius']


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


def _fetch_lrclib(
    track_name: str,
    artist_name: str,
    album_name: str,
    duration: float | None,
) -> tuple[str | None, str | None]:
    """Query LRCLIB; return ``(synced_lrc, plain_text)`` or ``(None, None)``."""
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

    if not result or result.get('instrumental'):
        return None, None

    synced = result.get('syncedLyrics') or None
    plain = result.get('plainLyrics') or None
    return synced, plain


def _fetch_syncedlyrics(track_name: str, artist_name: str) -> tuple[str | None, str | None]:
    """Query syncedlyrics providers; return ``(synced_lrc, plain_text)`` or ``(None, None)``."""
    try:
        import syncedlyrics
    except ImportError:
        return None, None

    search_term = f'{track_name} - {artist_name}'
    try:
        result = syncedlyrics.search(search_term, providers=_SYNCEDLYRICS_PROVIDERS)
    except Exception:  # noqa: BLE001 — provider/network errors are non-fatal
        return None, None

    if not result:
        return None, None

    if is_lrc_format(result):
        return result, strip_lrc_tags(result)
    return None, result


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
    1. LRCLIB exact-signature lookup via ``/api/get``, then ``/api/search``.
    2. syncedlyrics fallback (Musixmatch, NetEase, Megalobiz, Genius) when
       LRCLIB returns no match.
    """
    if not track_name or not artist_name:
        return None, None

    synced, plain = _fetch_lrclib(track_name, artist_name, album_name, duration)
    if synced or plain:
        return synced, plain

    return _fetch_syncedlyrics(track_name, artist_name)
