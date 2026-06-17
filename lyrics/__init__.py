"""Lyrics fetch, detect, and embed utilities for AV Morning Star."""

from .detector import is_music_track, is_youtube_music_url
from .embedder import embed_lyrics, is_lrc_format, parse_lrc_timestamps, save_lrc_file, strip_lrc_tags
from .fetcher import fetch_lyrics

__all__ = [
    'is_music_track',
    'is_youtube_music_url',
    'fetch_lyrics',
    'embed_lyrics',
    'save_lrc_file',
    'parse_lrc_timestamps',
    'strip_lrc_tags',
    'is_lrc_format',
]
