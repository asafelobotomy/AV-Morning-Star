"""Embed lyrics into audio files and optionally write .lrc sidecar files.

Supported containers
--------------------
- MP3  : ID3 USLT (plain text) + SYLT (time-synced) frames.
- FLAC : ``LYRICS`` / ``UNSYNCEDLYRICS`` Vorbis comment fields.
- OGG Vorbis / Opus : same Vorbis comment approach.
- M4A / ALAC / AAC  : iTunes ``©lyr`` MP4 atom.
- WAV / other       : not supported; returns False without raising.

mutagen is used for all containers.  It is a transitive dependency of yt-dlp
(required by the EmbedThumbnail postprocessor), so it is always available.
"""

import re
from pathlib import Path

_LRC_LINE_RE = re.compile(r'^\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def parse_lrc_timestamps(lrc_text: str) -> list[tuple[str, int]]:
    """Parse an LRC string into a list of ``(line_text, timestamp_ms)`` pairs.

    Handles both 2-digit and 3-digit millisecond fields.  Lines that do not
    match the ``[mm:ss.xx]`` pattern are skipped so that header tags like
    ``[by: ...]`` and ``[offset: ...]`` are silently ignored.
    """
    result = []
    for line in lrc_text.splitlines():
        m = _LRC_LINE_RE.match(line)
        if not m:
            continue
        minutes, seconds, ms_raw, text = m.groups()
        text = text.strip()
        if not text:
            # Skip blank synced lines (e.g. instrumental pauses marked as
            # ``[03:25.72]`` with no text); they produce empty subtitle
            # frames in most players without adding value.
            continue
        ms = int(ms_raw.ljust(3, '0'))  # normalise 2-digit → 3-digit ms
        timestamp_ms = int(minutes) * 60_000 + int(seconds) * 1_000 + ms
        result.append((text, timestamp_ms))
    return result


def strip_lrc_tags(lrc_text: str) -> str:
    """Return plain text with all ``[mm:ss.xx]`` timestamps removed."""
    lines = []
    for line in lrc_text.splitlines():
        m = _LRC_LINE_RE.match(line)
        if m:
            text = m.group(4).strip()
            if text:
                lines.append(text)
        elif line.strip() and not line.startswith('['):
            lines.append(line.strip())
    return '\n'.join(lines)


def save_lrc_file(audio_path: str, lrc_text: str) -> bool:
    """Write *lrc_text* to a ``.lrc`` sidecar file next to *audio_path*.

    Returns ``True`` on success, ``False`` on failure.
    """
    try:
        lrc_path = Path(audio_path).with_suffix('.lrc')
        lrc_path.write_text(lrc_text, encoding='utf-8')
        return True
    except OSError:
        return False


def embed_lyrics(
    file_path: str,
    synced_lrc: str | None = None,
    plain_text: str | None = None,
) -> bool:
    """Embed lyrics into *file_path* using mutagen.

    At least one of *synced_lrc* or *plain_text* must be provided.
    Returns ``True`` on success, ``False`` when the format is unsupported or
    an error occurs.
    """
    if not synced_lrc and not plain_text:
        return False

    ext = Path(file_path).suffix.lower()
    try:
        if ext == '.mp3':
            return _embed_mp3(file_path, synced_lrc, plain_text)
        if ext in ('.flac', '.ogg', '.opus'):
            return _embed_vorbis(file_path, synced_lrc, plain_text)
        if ext in ('.m4a', '.aac'):
            return _embed_m4a(file_path, synced_lrc, plain_text)
    except Exception:  # noqa: BLE001
        return False
    return False


# ---------------------------------------------------------------------------
# Per-format helpers
# ---------------------------------------------------------------------------

def _embed_mp3(path: str, synced_lrc: str | None, plain_text: str | None) -> bool:
    from mutagen.id3 import ID3, SYLT, USLT, Encoding, ID3NoHeaderError  # type: ignore[import]

    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        tags = ID3()

    uslt_text = plain_text or (strip_lrc_tags(synced_lrc) if synced_lrc else '')
    if uslt_text:
        tags.add(USLT(encoding=Encoding.UTF8, lang='eng', desc='', text=uslt_text))

    if synced_lrc:
        lrc_data = parse_lrc_timestamps(synced_lrc)
        if lrc_data:
            tags.add(SYLT(encoding=Encoding.UTF8, lang='eng', format=2, type=1, text=lrc_data))

    tags.save(path)
    return True


def _embed_vorbis(path: str, synced_lrc: str | None, plain_text: str | None) -> bool:
    ext = Path(path).suffix.lower()
    if ext == '.flac':
        from mutagen.flac import FLAC  # type: ignore[import]
        audio = FLAC(path)
    elif ext == '.opus':
        from mutagen.oggopus import OggOpus  # type: ignore[import]
        audio = OggOpus(path)
    else:
        from mutagen.oggvorbis import OggVorbis  # type: ignore[import]
        audio = OggVorbis(path)

    # Players that understand LRC (e.g. Foobar2000, Strawberry) read LYRICS.
    audio['LYRICS'] = [synced_lrc or plain_text]
    if plain_text and synced_lrc:
        # Also store a clean plain-text copy for players that don't grok LRC.
        audio['UNSYNCEDLYRICS'] = [plain_text]
    audio.save()
    return True


def _embed_m4a(path: str, synced_lrc: str | None, plain_text: str | None) -> bool:
    from mutagen.mp4 import MP4  # type: ignore[import]

    audio = MP4(path)
    # ©lyr is the iTunes lyrics atom; players read LRC timestamps as plain text
    # if they don't support synced display — still useful.
    audio['\xa9lyr'] = [synced_lrc or plain_text]
    audio.save()
    return True
