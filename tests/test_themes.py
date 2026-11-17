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

class TestThemes(unittest.TestCase):
    """themes.py must provide complete, consistent theme definitions."""

    def test_both_themes_present(self):
        self.assertIn("dark", _themes.THEMES)
        self.assertIn("light", _themes.THEMES)

    def test_each_theme_has_stylesheet_and_vars(self):
        for name, theme in _themes.THEMES.items():
            with self.subTest(theme=name):
                self.assertIn("stylesheet", theme, f"{name} missing 'stylesheet'")
                self.assertIn("vars", theme, f"{name} missing 'vars'")

    def test_stylesheet_is_non_empty_string(self):
        for name, theme in _themes.THEMES.items():
            with self.subTest(theme=name):
                self.assertIsInstance(theme["stylesheet"], str)
                self.assertGreater(len(theme["stylesheet"]), 0)

    def test_vars_contain_required_keys(self):
        required = {
            "accent",
            "tag_selected_bg", "tag_selected_fg", "tag_selected_hover",
            "tag_avail_bg", "tag_avail_fg", "tag_avail_border",
            "tag_avail_hover_bg", "tag_avail_hover_bd",
            "frame_bg", "frame_border", "preview_fg",
            "notice_fg", "notice_bg", "notice_border",
            "scroll_bg",
        }
        for name, theme in _themes.THEMES.items():
            with self.subTest(theme=name):
                missing = required - theme["vars"].keys()
                self.assertEqual(missing, set(), f"{name} vars missing keys: {missing}")

    def test_auth_instructions_rule_in_both_stylesheets(self):
        """Both themes must contain a QSS rule for the auth_instructions notice box."""
        for name, theme in _themes.THEMES.items():
            with self.subTest(theme=name):
                self.assertIn(
                    "auth_instructions",
                    theme["stylesheet"],
                    f"{name} stylesheet missing QLabel#auth_instructions rule",
                )

    def test_default_theme_is_valid(self):
        self.assertIn(_themes.DEFAULT_THEME, {*_themes.THEMES, "uq"})


class TestUqTheme(unittest.TestCase):
    """The uQ theme is generated from tokens.json and must fail safe."""

    TOKENS = {
        "variant": "dark",
        "colors": {
            "bg": "#282828", "surface": "#343330", "surface_alt": "#3d3c37",
            "overlay": "#4f4c44", "text": "#ebdbb2", "text_muted": "#b0a589",
            "accent": "#d79921", "accent_text": "#282828", "border": "#625e51",
            "success": "#98971a", "warning": "#d79921", "error": "#cc241d",
        },
    }

    def test_default_is_uq(self):
        self.assertEqual(_themes.DEFAULT_THEME, "uq")

    def test_build_theme_fills_every_placeholder(self):
        from themes.uq import build_theme
        theme = build_theme(self.TOKENS)
        self.assertNotIn("@", theme["stylesheet"])
        self.assertIn("#d79921", theme["stylesheet"])
        self.assertEqual(theme["vars"].keys(), _themes.DARK["vars"].keys())

    def test_invalid_tokens_rejected(self):
        from themes.uq import build_theme
        self.assertIsNone(build_theme({}))
        bad = {"colors": dict(self.TOKENS["colors"], bg="red")}
        self.assertIsNone(build_theme(bad))

    def test_resolve_falls_back_to_dark_without_uq(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            old = os.environ.get("XDG_STATE_HOME")
            os.environ["XDG_STATE_HOME"] = d
            try:
                self.assertIs(_themes.resolve_theme("uq"), _themes.DARK)
            finally:
                if old is None:
                    del os.environ["XDG_STATE_HOME"]
                else:
                    os.environ["XDG_STATE_HOME"] = old
