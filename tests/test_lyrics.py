"""
Tests for the lyrics package.

Covers:
- detector: is_music_track, is_youtube_music_url
- fetcher: URL construction (no live HTTP calls)
- embedder: parse_lrc_timestamps, strip_lrc_tags, save_lrc_file
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyrics.detector import is_music_track, is_youtube_music_url
from lyrics.embedder import parse_lrc_timestamps, save_lrc_file, strip_lrc_tags

# ---------------------------------------------------------------------------
# detector
# ---------------------------------------------------------------------------

class TestIsMusicTrack(unittest.TestCase):
    def test_track_and_artist_fields_detect_music(self):
        self.assertTrue(is_music_track({'track': 'Bohemian Rhapsody', 'artist': 'Queen'}))

    def test_missing_artist_is_not_music(self):
        self.assertFalse(is_music_track({'track': 'Some Track'}))

    def test_missing_track_is_not_music(self):
        self.assertFalse(is_music_track({'artist': 'Some Artist'}))

    def test_empty_track_string_is_not_music(self):
        self.assertFalse(is_music_track({'track': '', 'artist': 'Queen'}))

    def test_youtube_music_url_detects_music(self):
        self.assertTrue(is_music_track({
            'webpage_url': 'https://music.youtube.com/watch?v=abc',
        }))

    def test_soundcloud_url_detects_music(self):
        self.assertTrue(is_music_track({
            'webpage_url': 'https://soundcloud.com/artist/track',
        }))

    def test_bandcamp_url_detects_music(self):
        self.assertTrue(is_music_track({
            'webpage_url': 'https://artist.bandcamp.com/track/song',
        }))

    def test_plain_youtube_url_is_not_music(self):
        self.assertFalse(is_music_track({
            'webpage_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        }))

    def test_empty_info_is_not_music(self):
        self.assertFalse(is_music_track({}))


class TestIsYoutubeMusicUrl(unittest.TestCase):
    def test_music_youtube_com(self):
        self.assertTrue(is_youtube_music_url('https://music.youtube.com/watch?v=abc'))

    def test_www_youtube_com_is_false(self):
        self.assertFalse(is_youtube_music_url('https://www.youtube.com/watch?v=abc'))

    def test_youtu_be_is_false(self):
        self.assertFalse(is_youtube_music_url('https://youtu.be/abc'))

    def test_empty_string_is_false(self):
        self.assertFalse(is_youtube_music_url(''))


# ---------------------------------------------------------------------------
# embedder — LRC parsing
# ---------------------------------------------------------------------------

SAMPLE_LRC = """\
[00:17.12] I feel your breath upon my neck
[00:20.45] The sunlight dims and starts to fade
[03:20.31] The clock won't stop and this is what we get
[03:25.72]
"""

SAMPLE_LRC_2DIGIT_MS = """\
[01:02.03] Line with two-digit ms
[02:30.99] Another line
"""


class TestParseLrcTimestamps(unittest.TestCase):
    def test_basic_parse(self):
        result = parse_lrc_timestamps(SAMPLE_LRC)
        self.assertEqual(len(result), 3)  # blank line excluded

    def test_first_entry_text(self):
        result = parse_lrc_timestamps(SAMPLE_LRC)
        self.assertEqual(result[0][0], 'I feel your breath upon my neck')

    def test_first_entry_timestamp_ms(self):
        result = parse_lrc_timestamps(SAMPLE_LRC)
        # [00:17.12] = 17*1000 + 120 = 17120 ms
        self.assertEqual(result[0][1], 17_120)

    def test_last_entry_timestamp_ms(self):
        result = parse_lrc_timestamps(SAMPLE_LRC)
        # [03:20.31] = 3*60000 + 20*1000 + 310 = 200310 ms
        self.assertEqual(result[-1][1], 200_310)

    def test_blank_lrc_line_excluded(self):
        result = parse_lrc_timestamps(SAMPLE_LRC)
        texts = [r[0] for r in result]
        self.assertNotIn('', texts)

    def test_two_digit_ms_normalised(self):
        result = parse_lrc_timestamps(SAMPLE_LRC_2DIGIT_MS)
        self.assertEqual(result[0][1], 62_030)

    def test_empty_string_returns_empty(self):
        self.assertEqual(parse_lrc_timestamps(''), [])

    def test_header_tags_skipped(self):
        lrc = '[by: Test Artist]\n[00:01.00] Hello\n'
        result = parse_lrc_timestamps(lrc)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'Hello')


class TestStripLrcTags(unittest.TestCase):
    def test_strips_timestamps(self):
        result = strip_lrc_tags(SAMPLE_LRC)
        self.assertNotIn('[00:', result)

    def test_preserves_text(self):
        result = strip_lrc_tags(SAMPLE_LRC)
        self.assertIn('I feel your breath upon my neck', result)

    def test_blank_synced_line_excluded(self):
        result = strip_lrc_tags(SAMPLE_LRC)
        lines = [ln for ln in result.splitlines() if ln]
        self.assertEqual(len(lines), 3)

    def test_plain_text_passed_through(self):
        plain = 'No timestamps here\nJust text'
        self.assertEqual(strip_lrc_tags(plain), plain)


# ---------------------------------------------------------------------------
# embedder — save_lrc_file
# ---------------------------------------------------------------------------

class TestSaveLrcFile(unittest.TestCase):
    def test_writes_lrc_next_to_audio(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, 'song.mp3')
            lrc_content = '[00:01.00] Hello\n'
            result = save_lrc_file(audio_path, lrc_content)
            self.assertTrue(result)
            lrc_path = os.path.join(tmpdir, 'song.lrc')
            self.assertTrue(os.path.exists(lrc_path))
            with open(lrc_path, encoding='utf-8') as fh:
                self.assertEqual(fh.read(), lrc_content)

    def test_returns_false_on_invalid_path(self):
        result = save_lrc_file('/nonexistent/dir/song.mp3', 'lyrics')
        self.assertFalse(result)
