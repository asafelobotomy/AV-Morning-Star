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
import themes as _themes  # noqa: E402


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

class TestParseCookieError(unittest.TestCase):
    """parse_cookie_error converts yt-dlp error messages to user-friendly text."""

    def _parse(self, error_text, available=None, yt_browsers=None):
        stub = MagicMock()
        with patch('app_mixins.cookie_errors.detect_available_browsers', return_value=available or []):
            with patch('app_mixins.fetch_auth.get_browsers_with_youtube_cookies',
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
