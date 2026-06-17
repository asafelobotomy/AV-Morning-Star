"""Main window shell layout for MediaDownloaderApp."""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from constants import (
    APP_NAME,
    APP_SUBTITLE,
    BTN_FETCH,
    BTN_SELECT_ALL,
    BTN_SELECT_NONE,
    GROUP_AVAILABLE_VIDEOS,
    GROUP_ENTER_URL,
    GROUP_FILENAME_TEMPLATE,
    ICON_FILENAME,
    MAIN_WINDOW_MIN_HEIGHT,
    MAIN_WINDOW_MIN_WIDTH,
    MAIN_WINDOW_TITLE,
    MENU_ABOUT,
    MENU_HELP,
    MENU_PREFERENCES,
    MENU_TOOLS,
    PLACEHOLDER_URL,
    SHORTCUT_HELP,
    SHORTCUT_PREFERENCES,
    STATUS_READY,
)
from ui_widgets import FlowLayout, make_circular_pixmap


class UILayoutMixin:
    """Builds the main window layout."""

    def init_ui(self):
        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ICON_FILENAME)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        menubar = self.menuBar()

        view_menu = menubar.addMenu("View")
        self.dark_mode_action = view_menu.addAction("Dark Mode")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.current_theme == "dark")
        self.dark_mode_action.triggered.connect(self._on_theme_toggle)

        tools_menu = menubar.addMenu(MENU_TOOLS)

        preferences_action = tools_menu.addAction(MENU_PREFERENCES)
        preferences_action.setShortcut(SHORTCUT_PREFERENCES)
        preferences_action.triggered.connect(self.show_preferences)

        tools_menu.addSeparator()

        about_action = tools_menu.addAction(MENU_ABOUT)
        about_action.triggered.connect(self.show_about)

        help_action = tools_menu.addAction(MENU_HELP)
        help_action.setShortcut(SHORTCUT_HELP)
        help_action.triggered.connect(self.show_help)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        banner_layout = QHBoxLayout()
        banner_layout.addStretch()

        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(make_circular_pixmap(scaled_pixmap))
            banner_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title = QLabel(APP_NAME)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)

        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)

        banner_layout.addLayout(title_layout)
        banner_layout.addStretch()
        main_layout.addLayout(banner_layout)

        url_group = QGroupBox(GROUP_ENTER_URL)
        url_layout = QVBoxLayout()
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(PLACEHOLDER_URL)
        self.url_input.returnPressed.connect(self.fetch_videos)
        url_input_layout.addWidget(self.url_input)

        self.fetch_btn = QPushButton(BTN_FETCH)
        self.fetch_btn.clicked.connect(self.fetch_videos)
        url_input_layout.addWidget(self.fetch_btn)
        url_layout.addLayout(url_input_layout)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)

        content_row = QHBoxLayout()

        videos_group = QGroupBox(GROUP_AVAILABLE_VIDEOS)
        videos_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(120)
        scroll.setMaximumHeight(180)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.videos_container = QWidget()
        self.videos_container_layout = QVBoxLayout(self.videos_container)
        scroll.setWidget(self.videos_container)
        videos_layout.addWidget(scroll)

        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton(BTN_SELECT_ALL)
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setEnabled(False)
        select_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton(BTN_SELECT_NONE)
        self.select_none_btn.clicked.connect(self.select_none)
        self.select_none_btn.setEnabled(False)
        select_layout.addWidget(self.select_none_btn)

        videos_layout.addLayout(select_layout)
        videos_group.setLayout(videos_layout)
        content_row.addWidget(videos_group, 2)

        filename_group = QGroupBox(GROUP_FILENAME_TEMPLATE)
        filename_layout = QVBoxLayout()

        filename_layout.addWidget(QLabel("Selected Tags (click to remove):"))

        selected_frame = QWidget()
        selected_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.selected_tags_layout = FlowLayout(selected_frame)
        self.selected_tags_layout.setSpacing(10)
        filename_layout.addWidget(selected_frame)
        self._selected_frame = selected_frame

        filename_layout.addSpacing(10)
        filename_layout.addWidget(QLabel("Available Tags (click to add):"))

        available_frame = QWidget()
        available_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.available_tags_layout = FlowLayout(available_frame)
        self.available_tags_layout.setSpacing(10)
        filename_layout.addWidget(available_frame)
        self._available_frame = available_frame

        filename_layout.addSpacing(10)

        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.filename_preview = QLabel("")
        self.filename_preview.setStyleSheet("QLabel { font-family: monospace; font-weight: bold; }")
        self.filename_preview.setWordWrap(True)
        self.filename_preview.setMaximumHeight(60)
        preview_layout.addWidget(self.filename_preview)
        filename_layout.addLayout(preview_layout)

        filename_group.setLayout(filename_layout)
        filename_group.setMaximumWidth(450)
        content_row.addWidget(filename_group)

        main_layout.addLayout(content_row)
        self.init_filename_tags()

        self._setup_download_options(main_layout)
        self._setup_progress_footer(main_layout)
        self.statusBar().showMessage(STATUS_READY)
