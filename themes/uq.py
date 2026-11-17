"""uQ theme: colours come from uQ's rendered tokens.json and follow it live.

uqd writes ``tokens.json`` under ``$XDG_STATE_HOME/uq/theme/`` whenever the
theme changes. ``uq_theme()`` turns it into the same ``{"vars", "stylesheet"}``
shape as the built-in themes, or returns None when uQ is not installed.
"""

import json
import os
import re
from pathlib import Path

from .load import load_qss


def tokens_path() -> Path:
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state) / "uq" / "theme" / "tokens.json"


_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_REQUIRED = ("bg", "surface", "surface_alt", "overlay", "text", "text_muted",
             "accent", "accent_text", "border", "warning", "error", "success")


def _mix(a: str, b: str, t: float) -> str:
    """Blend hex colour *a* towards *b* by *t* (0..1)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def build_theme(tokens: dict):
    """Build a theme dict from parsed tokens.json, or None if it is unusable."""
    try:
        c = dict(tokens["colors"])
    except (KeyError, TypeError):
        return None
    if any(not isinstance(c.get(k), str) or not _HEX.match(c[k]) for k in _REQUIRED):
        return None
    c["accent_hover"] = _mix(c["accent"], c["bg"], 0.25)
    qss = load_qss("uq.qss")
    for key, value in c.items():
        qss = qss.replace(f"@{key}@", value)
    variant = tokens.get("variant", "dark")
    v = {
        "accent": c["accent"],
        "tag_selected_bg": c["accent"],
        "tag_selected_fg": c["accent_text"],
        "tag_selected_hover": c["error"],
        "tag_avail_bg": c["surface_alt"],
        "tag_avail_fg": c["text"],
        "tag_avail_border": c["border"],
        "tag_avail_hover_bg": c["overlay"],
        "tag_avail_hover_bd": c["accent"],
        "frame_bg": c["surface"],
        "frame_border": c["border"],
        "preview_fg": c["success"],
        "notice_fg": c["warning"],
        "notice_bg": c["surface"],
        "notice_border": c["warning"],
        "scroll_bg": c["bg"],
    }
    fonts = tokens.get("fonts") or {}
    return {"vars": v, "stylesheet": qss, "variant": variant,
            "font_family": fonts.get("ui"), "font_size": fonts.get("size")}


def uq_theme():
    """Current uQ theme, or None when tokens.json is missing or invalid."""
    try:
        return build_theme(json.loads(tokens_path().read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return None
