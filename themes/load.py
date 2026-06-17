"""Load theme QSS files from the themes package directory."""

from pathlib import Path

_THEME_DIR = Path(__file__).parent


def load_qss(filename: str) -> str:
    return (_THEME_DIR / filename).read_text(encoding="utf-8")
