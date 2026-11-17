"""
Theme definitions for AV Morning Star.

Each theme is a dict with two keys:
  "stylesheet" — full QSS string applied to QApplication
  "vars"       — colour/value tokens used by code that must set widget
                 stylesheets programmatically (e.g. tag buttons, frames)
"""

from .dark import DARK
from .light import LIGHT
from .uq import uq_theme, tokens_path

THEMES = {"dark": DARK, "light": LIGHT}
DEFAULT_THEME = "uq"


def resolve_theme(name):
    """Theme dict for *name*. "uq" follows uQ and falls back to dark without it."""
    if name == "uq":
        return uq_theme() or DARK
    return THEMES.get(name, DARK)

__all__ = ["DARK", "LIGHT", "THEMES", "DEFAULT_THEME", "resolve_theme", "tokens_path"]
