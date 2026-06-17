"""
Tests for pure-logic methods in main.py — no display required.

PyQt5 and yt_dlp are replaced with minimal stub modules before main is imported
so that tests are runnable without the full downloader stack installed.
"""

import os
import sys
import types
import unittest
from unittest.mock import MagicMock


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
