"""Light theme QSS and colour tokens."""

LIGHT = {
    "vars": {
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
    },
    "stylesheet": """
/* ── Global ── */
QWidget {
    background-color: #f0f0f0;
    color: #212121;
    font-size: 10pt;
}

/* ── Main / Central widget ── */
QMainWindow, QDialog {
    background-color: #f0f0f0;
}

/* ── Menu bar ── */
QMenuBar {
    background-color: #e0e0e0;
    color: #212121;
    border-bottom: 1px solid #bdbdbd;
}
QMenuBar::item:selected {
    background-color: #bbdefb;
}
QMenu {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
}
QMenu::item:selected {
    background-color: #2979ff;
    color: #ffffff;
}

/* ── Group boxes ── */
QGroupBox {
    border: 1px solid #bdbdbd;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 6px;
    color: #212121;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: #555555;
}

/* ── Buttons ── */
QPushButton {
    background-color: #e0e0e0;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 5px 14px;
}
QPushButton:hover {
    background-color: #2979ff;
    color: #ffffff;
    border-color: #2979ff;
}
QPushButton:pressed {
    background-color: #1565c0;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: #eeeeee;
    color: #9e9e9e;
    border-color: #e0e0e0;
}

/* ── Line edits ── */
QLineEdit {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 4px 6px;
    selection-background-color: #2979ff;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border-color: #2979ff;
}

/* ── Combo boxes ── */
QComboBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 4px 6px;
    selection-background-color: #2979ff;
    selection-color: #ffffff;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212121;
    selection-background-color: #2979ff;
    selection-color: #ffffff;
    border: 1px solid #bdbdbd;
}

/* ── Checkboxes ── */
QCheckBox {
    color: #212121;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #9e9e9e;
    border-radius: 3px;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #2979ff;
    border-color: #2979ff;
}

/* ── Progress bar ── */
QProgressBar {
    background-color: #e0e0e0;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    text-align: center;
    color: #212121;
}
QProgressBar::chunk {
    background-color: #2979ff;
    border-radius: 3px;
}

/* ── Scroll areas / scroll bars ── */
QScrollArea {
    background-color: #f0f0f0;
    border: 1px solid #bdbdbd;
}
QScrollBar:vertical {
    background: #e0e0e0;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #9e9e9e;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #e0e0e0;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #9e9e9e;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Labels ── */
QLabel {
    color: #212121;
    background-color: transparent;
}

/* ── Status bar ── */
QStatusBar {
    background-color: #e0e0e0;
    color: #555555;
    border-top: 1px solid #bdbdbd;
}

/* ── Tool tips ── */
QToolTip {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    padding: 4px;
}

/* ── Scroll area viewport ── */
QAbstractScrollArea {
    background-color: #f0f0f0;
}
QAbstractScrollArea > QWidget {
    background-color: #f0f0f0;
}

/* ── Menu separator ── */
QMenu::separator {
    height: 1px;
    background-color: #bdbdbd;
    margin: 3px 6px;
}

/* ── Status bar items — suppress Fusion border ── */
QStatusBar::item {
    border: none;
}

/* ── Notice / callout label (PreferencesDialog auth_instructions) ── */
QLabel#auth_instructions {
    color: #e65100;
    background-color: #fff3e0;
    border: 1px solid #ffcc80;
    border-radius: 4px;
    padding: 8px;
    font-size: 9pt;
}
""",
}
