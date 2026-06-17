"""
Tests for pure-logic methods in main.py — no display required.

PyQt5 and yt_dlp are replaced with minimal stub modules before main is imported
so that tests are runnable without the full downloader stack installed.
"""

import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


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
for _cn in ['QThread', 'QTimer', 'QSettings']:
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

class TestFetchVideosAuthPolicy(unittest.TestCase):
    """fetch_videos must pass cookies only when the mode or retry requires it."""

    def _make_app(self, browser_pref='auto'):
        """Return a minimal MediaDownloaderApp-shaped stub."""
        app = _main.MediaDownloaderApp.__new__(_main.MediaDownloaderApp)
        app.browser_preference = browser_pref
        app._youtube_auth_handled = False
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

        with patch('app_mixins.fetch_auth.URLScraperThread', FakeThread):
            app.fetch_videos()

    # Auto mode — first attempt should be cookieless for YouTube
    def test_auto_mode_youtube_first_attempt_is_cookieless(self):
        app = self._make_app(browser_pref='auto')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertIsNone(captured['cookies'])

    # Auto mode — after bot-detection, on_fetch_error temporarily overrides
    # browser_preference to an explicit browser before calling fetch_videos().
    # That explicit override (not cookieless_failed) is what drives the retry.
    def test_explicit_override_during_retry_uses_cookies(self):
        app = self._make_app(browser_pref='firefox')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(captured['cookies'], 'firefox')

    # None mode — never uses cookies even for YouTube
    def test_none_mode_never_uses_cookies(self):
        app = self._make_app(browser_pref='none')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertIsNone(captured['cookies'])

    # Explicit browser — always uses that browser
    def test_explicit_browser_always_uses_cookies(self):
        app = self._make_app(browser_pref='brave')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(captured['cookies'], 'brave')

    # Hostile URL — userinfo-confusion must NOT trigger YouTube auth path
    def test_userinfo_confusion_url_is_not_youtube(self):
        """youtube.com@evil.example must not be classified as YouTube."""
        app = self._make_app(browser_pref='auto')
        captured = {}
        app.url_input.text.return_value = 'https://youtube.com@evil.example/watch?v=abc'

        class FakeThread:
            def __init__(self_t, url, cookies_from_browser=None):
                captured['cookies'] = cookies_from_browser

            finished = MagicMock()
            error = MagicMock()
            start = MagicMock()

        with patch('app_mixins.fetch_auth.URLScraperThread', FakeThread):
            app.fetch_videos()

        self.assertIsNone(captured['cookies'])
        youtube_cookieless_msg = "Fetching video information (no authentication)..."
        calls = [str(c) for c in app.status_label.setText.call_args_list]
        self.assertFalse(
            any(youtube_cookieless_msg in c for c in calls),
            "Hostile URL was misclassified as YouTube",
        )

    def test_auto_mode_does_not_probe_cookie_stores(self):
        """Auto mode first fetch must not read browser cookie databases."""
        app = self._make_app(browser_pref='auto')
        captured = {}

        with patch('app_mixins.fetch_auth.get_browsers_with_youtube_cookies') as mock_yt_cookies:
            self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
            mock_yt_cookies.assert_not_called()

    # fetch stores the auth decision for start_download to mirror
    def test_fetch_stores_cookies_used_on_app(self):
        app = self._make_app(browser_pref='brave')
        captured = {}
        self._run_fetch(app, 'https://www.youtube.com/watch?v=abc', captured)
        self.assertEqual(app._fetch_cookies_used, captured['cookies'])
