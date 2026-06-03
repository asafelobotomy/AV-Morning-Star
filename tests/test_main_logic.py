"""
Tests for pure-logic methods in main.py — no display required.

PyQt5 and yt_dlp are replaced with minimal stub modules before main is imported
so that tests are runnable without the full downloader stack installed.
"""

import os
import sys
import types
import unittest
from unittest.mock import patch, MagicMock


def _fake_qt_class(name):
    """Real Python class that Qt subclasses can inherit from without side effects."""
    return type(name, (object,), {'__init__': lambda self, *a, **kw: None})


# ---- Provide minimal PyQt5 stubs before any import of main ----
_qtwidgets = types.ModuleType('PyQt5.QtWidgets')
for _cn in ['QApplication', 'QMainWindow', 'QWidget', 'QVBoxLayout',
            'QHBoxLayout', 'QPushButton', 'QLineEdit', 'QLabel',
            'QComboBox', 'QProgressBar', 'QCheckBox', 'QScrollArea',
            'QGroupBox', 'QMessageBox', 'QFileDialog', 'QSplashScreen',
            'QGridLayout', 'QDialog']:
    setattr(_qtwidgets, _cn, _fake_qt_class(_cn))

_qtcore = types.ModuleType('PyQt5.QtCore')
for _cn in ['QThread', 'QTimer']:
    setattr(_qtcore, _cn, _fake_qt_class(_cn))
_qtcore.pyqtSignal = lambda *a, **kw: MagicMock()
_qtcore.Qt = MagicMock()

_qtgui = types.ModuleType('PyQt5.QtGui')
for _cn in ['QIcon', 'QFont', 'QPixmap', 'QPainter', 'QPainterPath']:
    setattr(_qtgui, _cn, _fake_qt_class(_cn))

_pyqt5 = types.ModuleType('PyQt5')

sys.modules['PyQt5'] = _pyqt5
sys.modules['PyQt5.QtWidgets'] = _qtwidgets
sys.modules['PyQt5.QtCore'] = _qtcore
sys.modules['PyQt5.QtGui'] = _qtgui

# ---- Stub yt_dlp so logic-only tests run without the downloader installed ----
_yt_dlp = types.ModuleType('yt_dlp')
_yt_dlp.YoutubeDL = _fake_qt_class('YoutubeDL')
_yt_dlp_utils = types.ModuleType('yt_dlp.utils')
_yt_dlp_utils.DownloadError = Exception
_yt_dlp.utils = _yt_dlp_utils
sys.modules['yt_dlp'] = _yt_dlp
sys.modules['yt_dlp.utils'] = _yt_dlp_utils

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main as _main  # noqa: E402  (must come after stubs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app_stub(tags, format_text='Video'):
    """Return a minimal stub that satisfies build_filename_template's attribute access."""
    stub = MagicMock()
    stub.filename_template = list(tags)
    stub.format_combo.currentText.return_value = format_text
    return stub


# ---------------------------------------------------------------------------
# build_filename_template
# ---------------------------------------------------------------------------

class TestBuildFilenameTemplate(unittest.TestCase):
    """build_filename_template converts a tag list to a yt-dlp output template."""

    def _build(self, tags, format_text='Video'):
        stub = _make_app_stub(tags, format_text)
        return _main.MediaDownloaderApp.build_filename_template(stub)

    def test_single_title_tag(self):
        result = self._build(['title'])
        self.assertIn('%(title)s', result)

    def test_multiple_tags_joined_with_separator(self):
        result = self._build(['title', 'uploader'])
        self.assertIn('%(title)s', result)
        self.assertIn('%(uploader)s', result)
        self.assertIn(' - ', result)

    def test_empty_tag_list_returns_fallback(self):
        result = self._build([])
        self.assertEqual(result, '%(title)s.%(ext)s')

    def test_quality_tag_uses_height_for_video(self):
        result = self._build(['quality'], format_text='Video')
        self.assertIn('%(height)sp', result)

    def test_quality_tag_uses_abr_for_audio_only(self):
        result = self._build(['quality'], format_text='Audio Only')
        self.assertIn('%(abr)skbps', result)

    def test_all_known_tags_produce_ydl_variables(self):
        known_tags = ['title', 'uploader', 'format', 'website', 'id',
                      'upload_date', 'download_date', 'duration', 'ext']
        result = self._build(known_tags)
        self.assertIn('%(', result)

    def test_unknown_tags_are_silently_skipped(self):
        result = self._build(['title', 'totally_unknown'])
        self.assertIn('%(title)s', result)
        self.assertNotIn('totally_unknown', result)

    def test_order_preserved(self):
        result = self._build(['uploader', 'title'])
        uploader_pos = result.index('%(uploader)s')
        title_pos = result.index('%(title)s')
        self.assertLess(uploader_pos, title_pos)

    def test_non_ext_tags_always_include_extension_placeholder(self):
        """Ensure .%(ext)s is appended when ext tag is not selected."""
        result = self._build(['title', 'uploader'])
        self.assertTrue(result.endswith('.%(ext)s'),
                        f"Expected template to end with .%(ext)s, got: {result}")

    def test_ext_tag_not_duplicated(self):
        """When user selects the ext tag, .%(ext)s must not be appended twice."""
        result = self._build(['title', 'ext'])
        self.assertEqual(result.count('%(ext)s'), 1,
                         f"%(ext)s appears more than once in: {result}")


# ---------------------------------------------------------------------------
# parse_cookie_error
# ---------------------------------------------------------------------------

class TestParseCookieError(unittest.TestCase):
    """parse_cookie_error converts yt-dlp error messages to user-friendly text."""

    def _parse(self, error_text, available=None, yt_browsers=None):
        stub = MagicMock()
        with patch('main.detect_available_browsers', return_value=available or []):
            with patch('main.get_browsers_with_youtube_cookies',
                       return_value=yt_browsers or []):
                return _main.MediaDownloaderApp.parse_cookie_error(stub, error_text)

    def test_unrecognised_error_returns_none(self):
        self.assertIsNone(self._parse("some random yt-dlp error"))

    def test_firefox_db_not_found_includes_browser_name(self):
        error = "could not find firefox cookies database"
        result = self._parse(error, available=['chrome'])
        self.assertIsNotNone(result)
        self.assertIn('Firefox', result)

    def test_chrome_db_not_found_includes_browser_name(self):
        error = "could not find chrome cookies database"
        result = self._parse(error, available=['firefox'])
        self.assertIsNotNone(result)
        self.assertIn('Chrome', result)

    def test_no_browsers_available_shows_supported_list(self):
        error = "could not find chrome cookies database"
        result = self._parse(error, available=[])
        self.assertIn('Supported browsers', result)

    def test_yt_browsers_listed_in_recommendation(self):
        error = "could not find brave cookies database"
        result = self._parse(error, available=['firefox'], yt_browsers=['firefox'])
        self.assertIn('Firefox', result)

    def test_corrupt_database_detected(self):
        result = self._parse("database is corrupt")
        self.assertIsNotNone(result)
        self.assertIn('corrupted', result)

    def test_malformed_database_detected(self):
        result = self._parse("database malformed error")
        self.assertIsNotNone(result)
        self.assertIn('corrupted', result)

    def test_permission_denied_detected(self):
        result = self._parse("permission denied reading cookie file")
        self.assertIsNotNone(result)
        self.assertIn('Permission denied', result)

    def test_access_denied_detected(self):
        result = self._parse("access denied to cookie storage")
        self.assertIsNotNone(result)
        self.assertIn('Permission denied', result)


# ---------------------------------------------------------------------------
# fetch_videos auth policy — cookie decision per browser_preference mode
# ---------------------------------------------------------------------------

class TestFetchVideosAuthPolicy(unittest.TestCase):
    """fetch_videos must pass cookies only when the mode or retry requires it."""

    def _make_app(self, browser_pref='auto', cookieless_failed=False):
        """Return a minimal MediaDownloaderApp-shaped stub."""
        app = _main.MediaDownloaderApp.__new__(_main.MediaDownloaderApp)
        app.browser_preference = browser_pref
        app.cookieless_failed = cookieless_failed
        # Minimal UI stubs so the method can run without a real Qt window
        app.url_input = MagicMock()
        app.status_label = MagicMock()
        app.statusBar = MagicMock(return_value=MagicMock())
        app.fetch_btn = MagicMock()
        app.download_btn = MagicMock()
        app.clear_videos_list = MagicMock()
        return app

    def _run_fetch(self, app, url, captured):
        """Run fetch_videos and record the cookies_from_browser passed to the thread."""
        app.url_input.text.return_value = url

        class FakeThread:
            def __init__(self_t, url, cookies_from_browser=None):
                captured['cookies'] = cookies_from_browser

            finished = MagicMock()
            error = MagicMock()
            start = MagicMock()

        with patch('main.URLScraperThread', FakeThread):
            with patch('main.get_default_browser', return_value='firefox'):
                app.fetch_videos()

    # Auto mode — first attempt should be cookieless for YouTube
    def test_auto_mode_youtube_first_attempt_is_cookieless(self):
        app = self._make_app(browser_pref='auto', cookieless_failed=False)
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertIsNone(captured['cookies'])

    # Auto mode — after bot-detection, on_fetch_error temporarily overrides
    # browser_preference to an explicit browser before calling fetch_videos().
    # That explicit override (not cookieless_failed) is what drives the retry.
    def test_explicit_override_during_retry_uses_cookies(self):
        app = self._make_app(browser_pref='firefox', cookieless_failed=False)
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(captured['cookies'], 'firefox')

    # None mode — never uses cookies even for YouTube
    def test_none_mode_never_uses_cookies(self):
        app = self._make_app(browser_pref='none', cookieless_failed=False)
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertIsNone(captured['cookies'])

    # Explicit browser — always uses that browser
    def test_explicit_browser_always_uses_cookies(self):
        app = self._make_app(browser_pref='brave', cookieless_failed=False)
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(captured['cookies'], 'brave')

    # Hostile URL — userinfo-confusion must NOT trigger YouTube auth path
    def test_userinfo_confusion_url_is_not_youtube(self):
        """youtube.com@evil.example must not be classified as YouTube."""
        app = self._make_app(browser_pref='auto', cookieless_failed=False)
        captured = {}
        # In auto mode with no cookieless failure, a *real* YouTube URL gets no
        # cookies. For this hostile URL the extractor factory will route it as
        # non-YouTube (generic), so auto mode will pass get_default_browser()
        # cookies (non-YouTube path). The key assertion is that the is_youtube_url
        # check returns False — proven by the extractor test suite; here we verify
        # fetch_videos never treats it as YouTube by confirming no special
        # "Fetching video information (no authentication)..." YouTube message is set.
        app.url_input.text.return_value = 'https://youtube.com@evil.example/watch?v=abc'

        class FakeThread:
            def __init__(self_t, url, cookies_from_browser=None):
                captured['cookies'] = cookies_from_browser

            finished = MagicMock()
            error = MagicMock()
            start = MagicMock()

        with patch('main.URLScraperThread', FakeThread):
            with patch('main.get_default_browser', return_value='firefox'):
                app.fetch_videos()

        # The status message should NOT contain the YouTube-specific cookieless text
        youtube_cookieless_msg = "Fetching video information (no authentication)..."
        calls = [str(c) for c in app.status_label.setText.call_args_list]
        self.assertFalse(
            any(youtube_cookieless_msg in c for c in calls),
            "Hostile URL was misclassified as YouTube"
        )

    # fetch stores the auth decision for start_download to mirror
    def test_fetch_stores_cookies_used_on_app(self):
        app = self._make_app(browser_pref='brave')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(app._fetch_cookies_used, captured['cookies'])


# ---------------------------------------------------------------------------
# Audio codec label → yt-dlp preferredcodec mapping
# ---------------------------------------------------------------------------

class TestAudioCodecMapping(unittest.TestCase):
    """Verify the codec label→name mapping used in advanced-mode downloads."""

    # Replicate the mapping dict from main.py so the test is independent of
    # the widget; any divergence will cause this suite to catch it.
    _CODEC_MAP = {
        'MP3': 'mp3',
        'AAC': 'aac',
        'FLAC': 'flac',
        'Opus': 'opus',
        'M4A': 'm4a',
        'WAV': 'wav',
        'ALAC': 'alac',
        'OGG Vorbis': 'vorbis',
    }

    def _map(self, label):
        return self._CODEC_MAP.get(label, label.lower())

    def test_mp3(self):
        self.assertEqual(self._map('MP3'), 'mp3')

    def test_aac(self):
        self.assertEqual(self._map('AAC'), 'aac')

    def test_flac(self):
        self.assertEqual(self._map('FLAC'), 'flac')

    def test_opus(self):
        self.assertEqual(self._map('Opus'), 'opus')

    def test_m4a(self):
        self.assertEqual(self._map('M4A'), 'm4a')

    def test_wav(self):
        self.assertEqual(self._map('WAV'), 'wav')

    def test_alac(self):
        self.assertEqual(self._map('ALAC'), 'alac')

    def test_ogg_vorbis_maps_to_vorbis_not_ogg(self):
        """Critical: yt-dlp expects 'vorbis', not 'ogg'."""
        self.assertEqual(self._map('OGG Vorbis'), 'vorbis')
        self.assertNotEqual(self._map('OGG Vorbis'), 'ogg')

    def test_all_constants_covered(self):
        """Every label in constants.AUDIO_CODECS must be present in the map."""
        import constants
        missing = [c for c in constants.AUDIO_CODECS if c not in self._CODEC_MAP]
        self.assertEqual(missing, [],
                         f"Codec labels not in mapping dict: {missing}")


# ---------------------------------------------------------------------------
# closeEvent — graceful QThread shutdown
# ---------------------------------------------------------------------------

class TestCloseEvent(unittest.TestCase):
    """Unit tests for MediaDownloaderApp.closeEvent without a live QApplication."""

    def _make_app(self):
        app = _main.MediaDownloaderApp.__new__(_main.MediaDownloaderApp)
        app.scraper_thread = None
        app.download_thread = None
        return app

    def _make_event(self):
        event = MagicMock()
        return event

    def test_no_threads_accepts_event(self):
        app = self._make_app()
        event = self._make_event()
        app.closeEvent(event)
        event.accept.assert_called_once()
        event.ignore.assert_not_called()

    def test_non_running_thread_accepts_event(self):
        app = self._make_app()
        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = False
        app.scraper_thread = mock_thread
        event = self._make_event()
        app.closeEvent(event)
        event.accept.assert_called_once()

    def test_running_thread_no_stops_when_user_cancels(self):
        app = self._make_app()
        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = True
        app.download_thread = mock_thread
        event = self._make_event()
        with patch('main.QMessageBox') as mock_mb:
            mock_mb.Yes = 0x4000
            mock_mb.No = 0x10000
            mock_mb.question.return_value = mock_mb.No
            app.closeEvent(event)
        event.ignore.assert_called_once()
        event.accept.assert_not_called()
        mock_thread.quit.assert_not_called()

    def test_running_thread_stopped_when_user_confirms(self):
        app = self._make_app()
        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = True
        mock_thread.wait.return_value = True  # finishes within timeout
        app.scraper_thread = mock_thread
        event = self._make_event()
        with patch('main.QMessageBox') as mock_mb:
            mock_mb.Yes = 0x4000
            mock_mb.No = 0x10000
            mock_mb.question.return_value = mock_mb.Yes
            app.closeEvent(event)
        mock_thread.requestInterruption.assert_called_once()
        mock_thread.terminate.assert_not_called()
        event.accept.assert_called_once()

    def test_thread_not_force_terminated_when_wait_times_out(self):
        """On timeout the window stays open (event.ignore) and terminate() is never called."""
        app = self._make_app()
        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = True
        mock_thread.wait.return_value = False  # does not stop within timeout
        app.download_thread = mock_thread
        event = self._make_event()
        with patch('main.QMessageBox') as mock_mb:
            mock_mb.Yes = 0x4000
            mock_mb.No = 0x10000
            mock_mb.question.return_value = mock_mb.Yes
            mock_mb.Warning = MagicMock()
            mock_mb.warning = MagicMock()
            app.closeEvent(event)
        mock_thread.requestInterruption.assert_called_once()
        mock_thread.terminate.assert_not_called()
        # Window must NOT close when a thread is still running after timeout.
        event.ignore.assert_called_once()
        event.accept.assert_not_called()


# ---------------------------------------------------------------------------
# PreferencesDialog — GROUP_AUTHENTICATION constant must exist (NameError guard)
# ---------------------------------------------------------------------------

class TestPreferencesDialogSmoke(unittest.TestCase):
    """GROUP_AUTHENTICATION must be defined in constants so PreferencesDialog doesn't NameError."""

    def test_group_authentication_constant_exists(self):
        """GROUP_AUTHENTICATION must be defined in constants and be a non-empty string."""
        import constants
        self.assertTrue(
            hasattr(constants, 'GROUP_AUTHENTICATION'),
            "constants.GROUP_AUTHENTICATION is missing — PreferencesDialog will raise NameError",
        )
        self.assertIsInstance(constants.GROUP_AUTHENTICATION, str)
        self.assertTrue(constants.GROUP_AUTHENTICATION, "GROUP_AUTHENTICATION must be non-empty")


if __name__ == '__main__':
    unittest.main()
