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
        with patch('app_mixins.window_lifecycle.QMessageBox') as mock_mb:
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
        with patch('app_mixins.window_lifecycle.QMessageBox') as mock_mb:
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
        with patch('app_mixins.window_lifecycle.QMessageBox') as mock_mb:
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
