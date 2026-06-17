"""Filename template tag button styling helpers."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton

from themes import THEMES


def create_tag_button(app, tag, *, is_selected=False):
    """Create a visual tag button (pill/chip) for filename templates."""
    display_text = app.all_tags.get(tag, tag)
    v = THEMES[app.current_theme]["vars"]

    btn = QPushButton(display_text)
    btn.setFixedHeight(26)
    btn.setMinimumWidth(80)
    btn.setCursor(Qt.PointingHandCursor)
    btn.tag = tag

    if is_selected:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {v['tag_selected_bg']};
                color: {v['tag_selected_fg']};
                border: none;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {v['tag_selected_hover']};
            }}
        """)
        btn.clicked.connect(lambda checked, t=tag: app.remove_tag_visual(t))
        btn.setToolTip("Click to remove")
    else:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {v['tag_avail_bg']};
                color: {v['tag_avail_fg']};
                border: 2px solid {v['tag_avail_border']};
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {v['tag_avail_hover_bg']};
                border-color: {v['tag_avail_hover_bd']};
            }}
        """)
        btn.clicked.connect(lambda checked, t=tag: app.add_tag_visual(t))

    return btn
