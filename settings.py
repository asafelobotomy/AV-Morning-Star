"""Persistent application settings via QSettings (no cookies or secrets stored)."""

from PyQt5.QtCore import QSettings

from constants import DEFAULT_BROWSER_PREFERENCE, DEFAULT_OUTPUT_DIR
from themes import DEFAULT_THEME

ORGANIZATION = "AVMorningStar"
APPLICATION = "AV-Morning-Star"

_VALID_BROWSERS = {
    'auto', 'none', 'firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera', 'vivaldi',
}
_VALID_THEMES = {'dark', 'light'}


def _settings():
    return QSettings(ORGANIZATION, APPLICATION)


def load_browser_preference():
    value = _settings().value('browser_preference', DEFAULT_BROWSER_PREFERENCE)
    return value if value in _VALID_BROWSERS else DEFAULT_BROWSER_PREFERENCE


def save_browser_preference(preference):
    if preference in _VALID_BROWSERS:
        _settings().setValue('browser_preference', preference)


def load_theme():
    value = _settings().value('theme', DEFAULT_THEME)
    return value if value in _VALID_THEMES else DEFAULT_THEME


def save_theme(theme):
    if theme in _VALID_THEMES:
        _settings().setValue('theme', theme)


def load_output_path():
    value = _settings().value('output_path', '')
    if value and isinstance(value, str):
        return value
    return DEFAULT_OUTPUT_DIR


def save_output_path(path):
    if path:
        _settings().setValue('output_path', path)
