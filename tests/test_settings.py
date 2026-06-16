"""Tests for persistent application settings."""

import os
import sys
import types
import unittest
from unittest.mock import patch, MagicMock


def _fake_qt_class(name):
    return type(name, (object,), {'__init__': lambda self, *a, **kw: None})


_qtcore = types.ModuleType('PyQt5.QtCore')
_qtcore.QSettings = _fake_qt_class('QSettings')
_pyqt5 = types.ModuleType('PyQt5')
sys.modules['PyQt5'] = _pyqt5
sys.modules['PyQt5.QtCore'] = _qtcore

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import (
    load_browser_preference,
    save_browser_preference,
    load_theme,
    save_theme,
    load_output_path,
    save_output_path,
)


class TestSettings(unittest.TestCase):
    """QSettings helpers store and load user preferences."""

    def setUp(self):
        self.mock_settings = MagicMock()
        self.patcher = patch('settings._settings', return_value=self.mock_settings)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_load_browser_preference_default(self):
        self.mock_settings.value.return_value = None
        self.assertEqual(load_browser_preference(), 'auto')

    def test_load_browser_preference_invalid_falls_back(self):
        self.mock_settings.value.return_value = 'invalid-browser'
        self.assertEqual(load_browser_preference(), 'auto')

    def test_save_browser_preference_valid(self):
        save_browser_preference('firefox')
        self.mock_settings.setValue.assert_called_with('browser_preference', 'firefox')

    def test_save_browser_preference_invalid_ignored(self):
        save_browser_preference('not-a-browser')
        self.mock_settings.setValue.assert_not_called()

    def test_load_theme_default(self):
        self.mock_settings.value.return_value = None
        self.assertEqual(load_theme(), 'dark')

    def test_save_theme(self):
        save_theme('light')
        self.mock_settings.setValue.assert_called_with('theme', 'light')

    def test_load_output_path_default(self):
        self.mock_settings.value.return_value = ''
        self.assertEqual(load_output_path(), '~/Downloads')

    def test_save_output_path(self):
        save_output_path('/tmp/downloads')
        self.mock_settings.setValue.assert_called_with('output_path', '/tmp/downloads')


if __name__ == '__main__':
    unittest.main()
