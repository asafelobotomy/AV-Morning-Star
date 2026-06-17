"""Mixin methods for MediaDownloaderApp."""

import os
import pathlib

from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

from browser_utils import detect_available_browsers, get_browsers_with_youtube_cookies
from constants import (
    ABOUT_TEXT,
    ABOUT_WINDOW_TITLE,
    APP_NAME,
    APP_SUBTITLE,
    AUDIO_BITRATES,
    AUDIO_CODECS,
    BTN_BROWSE,
    BTN_DOWNLOAD_SELECTED,
    BTN_FETCH,
    BTN_SELECT_ALL,
    BTN_SELECT_NONE,
    DEFAULT_FILENAME_TAGS,
    GROUP_AVAILABLE_VIDEOS,
    GROUP_DOWNLOAD_OPTIONS,
    GROUP_ENTER_URL,
    GROUP_FILENAME_TEMPLATE,
    GROUP_PROGRESS,
    HELP_GETTING_STARTED,
    HELP_MORE_INFO,
    HELP_SUPPORTED_SITES,
    HELP_WINDOW_TITLE,
    HELP_YOUTUBE_AUTH,
    ICON_FILENAME,
    MAIN_WINDOW_MIN_HEIGHT,
    MAIN_WINDOW_MIN_WIDTH,
    MAIN_WINDOW_TITLE,
    MENU_ABOUT,
    MENU_HELP,
    MENU_PREFERENCES,
    MENU_TOOLS,
    MODE_BASIC,
    PLACEHOLDER_URL,
    SHORTCUT_HELP,
    SHORTCUT_PREFERENCES,
    STATUS_READY,
    VIDEO_CONTAINERS,
    VIDEO_QUALITIES,
)
from dialogs import PreferencesDialog
from extractors import is_youtube_url
from settings import load_output_path, save_output_path, save_theme
from threads import DownloadThread, URLScraperThread
from ui_widgets import FlowLayout, VideoCheckbox, make_circular_pixmap



class VideosListMixin:
    """Behaviour mixed into MediaDownloaderApp."""

    def browse_output_path(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.output_path)
        if directory:
            self.output_path = directory
            self.path_label.setText(self.output_path)
            save_output_path(directory)

    def clear_videos_list(self):
        """Clear the videos list"""
        for checkbox in self.checkboxes:
            self.videos_container_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkboxes = []
        self.videos_list = []

    def on_videos_fetched(self, videos):
        """Handle fetched videos"""
        self._youtube_auth_handled = False
        self.videos_list = videos
        self.fetch_btn.setEnabled(True)

        if not videos:
            self.status_label.setText("No videos found")
            self.statusBar().showMessage("No videos found at the provided URL")
            return

        # Create checkboxes for each video
        for video in videos:
            duration = video.get('duration', 0)
            if duration:
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = "N/A"

            checkbox_text = f"{video['title']}\nUploader: {video.get('uploader', 'Unknown')} | Duration: {duration_str}"
            checkbox = VideoCheckbox(checkbox_text)
            checkbox.setChecked(True)
            self.videos_container_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.select_all_btn.setEnabled(True)
        self.select_none_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(videos)} video(s)")
        self.statusBar().showMessage(f"Successfully loaded {len(videos)} video(s)")

    def select_all(self):
        """Select all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def select_none(self):
        """Deselect all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
