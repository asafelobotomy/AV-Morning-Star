"""Light theme colour tokens and QSS."""

from .load import load_qss

LIGHT_VARS = {
    "accent":             "#2979ff",
    "tag_selected_bg":    "#2979ff",
    "tag_selected_fg":    "#ffffff",
    "tag_selected_hover": "#d32f2f",
    "tag_avail_bg":       "#e0e0e0",
    "tag_avail_fg":       "#212121",
    "tag_avail_border":   "#bdbdbd",
    "tag_avail_hover_bg": "#bbdefb",
    "tag_avail_hover_bd": "#2979ff",
    "frame_bg":           "#f5f5f5",
    "frame_border":       "#bdbdbd",
    "preview_fg":         "#1b5e20",
    "notice_fg":          "#e65100",
    "notice_bg":          "#fff3e0",
    "notice_border":      "#ffcc80",
    "scroll_bg":          "#f0f0f0",
}

LIGHT = {"vars": LIGHT_VARS, "stylesheet": load_qss("light.qss")}
