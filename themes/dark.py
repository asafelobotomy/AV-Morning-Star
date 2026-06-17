"""Dark theme colour tokens and QSS."""

from .load import load_qss

DARK_VARS = {
    "accent":             "#4a9eff",
    "tag_selected_bg":    "#4a9eff",
    "tag_selected_fg":    "#ffffff",
    "tag_selected_hover": "#ff4444",
    "tag_avail_bg":       "#555555",
    "tag_avail_fg":       "#ffffff",
    "tag_avail_border":   "#777777",
    "tag_avail_hover_bg": "#666666",
    "tag_avail_hover_bd": "#4a9eff",
    "frame_bg":           "#2d2d2d",
    "frame_border":       "#444444",
    "preview_fg":         "#00ff00",
    "notice_fg":          "#ff8800",
    "notice_bg":          "#2a2a2a",
    "notice_border":      "#664400",
    "scroll_bg":          "#1e1e1e",
}

DARK = {"vars": DARK_VARS, "stylesheet": load_qss("dark.qss")}
