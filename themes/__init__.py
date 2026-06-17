"""
Theme definitions for AV Morning Star.

Each theme is a dict with two keys:
  "stylesheet" — full QSS string applied to QApplication
  "vars"       — colour/value tokens used by code that must set widget
                 stylesheets programmatically (e.g. tag buttons, frames)
"""

from .dark import DARK
from .light import LIGHT

THEMES = {"dark": DARK, "light": LIGHT}
DEFAULT_THEME = "dark"

__all__ = ["DARK", "LIGHT", "THEMES", "DEFAULT_THEME"]
