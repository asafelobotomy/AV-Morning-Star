"""
Tests for pure-logic methods in main.py — no display required.

PyQt5 is replaced with minimal stub classes before main is imported so that
class bodies execute normally and methods are accessible as unbound functions.
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main as _main  # noqa: E402  (must come after PyQt5 stubs)


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


if __name__ == '__main__':
    unittest.main()



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app_stub(tags, format_text='Video'):
    """Return a MagicMock that satisfies build_filename_template's attribute access."""
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

    def test_all_known_tags_map_to_ydl_variables(self):
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


if __name__ == '__main__':
    unittest.main()
