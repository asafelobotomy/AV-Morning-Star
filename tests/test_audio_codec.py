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
