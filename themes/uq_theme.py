"""uq-theme 1.1.0

uQ's theme tokens ($XDG_STATE_HOME/uq/theme/tokens.json, written by uqd) for a Python app. Vendor
this file unchanged (see uQ's native/uq-theme/README.md); it needs only the standard library.

load() gives the tokens as one dict, the same shape uq_theme.rs and uqtheme.h give:

    {present, name, variant, colors{bg, surface, ...}, radius, gapIn, gapOut, borderWidth,
     fontUi, fontMono, fontSize, iconTheme, motion{fast, base, slow, reduce}}

or {"present": False} when uQ isn't there, the file doesn't parse, or a colour is missing or not
#rrggbb / #rrggbbaa. To follow changes live, watch theme_dirs(path) (the theme/ folder and its
parent: uqd renames a filled staging folder over theme/) with QFileSystemWatcher or inotify, wait
about 150 ms after a change, and load() again.
"""

import json
import os
import re
from pathlib import Path

VERSION = "1.1.0"

COLORS = ("bg", "surface", "surface_alt", "overlay", "text", "text_muted",
          "accent", "accent_text", "border", "success", "warning", "error")

MAX_BYTES = 256 * 1024
_COLOR = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")


def tokens_path(override_var=None, env=None):
    """$<override_var> when set, else $XDG_STATE_HOME/uq/theme/tokens.json (absolute only), else
    ~/.local/state/uq/theme/tokens.json; None without HOME."""
    env = os.environ if env is None else env
    if override_var and env.get(override_var):
        return Path(env[override_var])
    state = env.get("XDG_STATE_HOME", "")
    if not os.path.isabs(state):
        home = env.get("HOME", "")
        if not home:
            return None
        state = os.path.join(home, ".local/state")
    return Path(state) / "uq/theme/tokens.json"


def theme_dirs(path):
    """The folders to watch for `path`: its folder and that folder's parent, or the nearest
    folder that exists when uQ hasn't written a theme yet."""
    d = Path(path).parent
    while not d.is_dir() and d != d.parent:
        d = d.parent
    return [str(d), str(d.parent)] if d != d.parent else [str(d)]


def _absent():
    return {"present": False}


def _num(obj, key, default, maximum):
    v = obj.get(key) if isinstance(obj, dict) else None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
        return default
    return min(int(v), maximum)


def _text(obj, key):
    v = obj.get(key) if isinstance(obj, dict) else None
    return v if isinstance(v, str) else ""


def parse(text):
    """The tokens in `text` (the contents of tokens.json)."""
    try:
        t = json.loads(text)
    except (ValueError, TypeError):
        return _absent()
    if not isinstance(t, dict):
        return _absent()
    src = t.get("colors") if isinstance(t.get("colors"), dict) else {}
    colors = {}
    for key in COLORS:
        c = src.get(key)
        if not isinstance(c, str) or not _COLOR.fullmatch(c):
            return _absent()
        colors[key] = c
    ui, fonts, icons = (t.get(k) if isinstance(t.get(k), dict) else {} for k in ("ui", "fonts", "icons"))
    motion = t.get("motion") if isinstance(t.get("motion"), dict) else {}
    reduce = motion.get("reduce") is True

    def ms(key, default):
        return 0 if reduce else _num(motion, key, default, 1000)

    name = t.get("name")
    return {
        "present": True,
        "name": name if isinstance(name, str) else "uQ",
        "variant": "light" if t.get("variant") == "light" else "dark",
        "colors": colors,
        "radius": _num(ui, "radius", 8, 32),
        "gapIn": _num(ui, "gap_in", 5, 64),
        "gapOut": _num(ui, "gap_out", 12, 64),
        "borderWidth": _num(ui, "border_width", 1, 8),
        "fontUi": _text(fonts, "ui"),
        "fontMono": _text(fonts, "mono"),
        "fontSize": _num(fonts, "size", 0, 32),
        "iconTheme": _text(icons, "theme"),
        "motion": {"fast": ms("fast", 100), "base": ms("base", 140), "slow": ms("slow", 220), "reduce": reduce},
    }


def load(path):
    """The tokens at `path`; {"present": False} without them."""
    try:
        p = Path(path)
        if p.stat().st_size > MAX_BYTES:
            return _absent()
        return parse(p.read_text(encoding="utf-8"))
    except (OSError, TypeError, UnicodeDecodeError):
        return _absent()
