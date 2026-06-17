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



class FilenameTagsMixin:
    """Behaviour mixed into MediaDownloaderApp."""

    def init_filename_tags(self):
        """Initialize available and selected filename tags"""
        # All available tags with descriptions
        self.all_tags = {
            'title': 'Title',
            'uploader': 'Uploader',
            'quality': 'Quality',
            'format': 'Format',
            'website': 'Website',
            'id': 'Video ID',
            'upload_date': 'Upload Date',
            'download_date': 'Timestamp',
            'duration': 'Duration',
            'ext': 'Extension'
        }

        # Track tag buttons for drag-drop
        self.selected_tag_buttons = []
        self.available_tag_buttons = []

        # Create initial tag buttons
        self.refresh_tag_buttons()

        # Update preview
        self.update_filename_preview()

    def create_tag_button(self, tag, is_selected=False):
        """Create a visual tag button (pill/chip)"""
        display_text = self.all_tags.get(tag, tag)

        if is_selected:
            # Selected tag - blue button that can be clicked to remove
            btn = QPushButton(display_text)
            v = THEMES[self.current_theme]["vars"]
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
            btn.setFixedHeight(26)
            btn.setMinimumWidth(80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tag: self.remove_tag_visual(t))
            btn.tag = tag
            btn.setToolTip("Click to remove")
            return btn
        else:
            # Available tag (clickable to add)
            btn = QPushButton(display_text)
            v = THEMES[self.current_theme]["vars"]
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
            btn.setFixedHeight(26)
            btn.setMinimumWidth(80)  # Minimum width to prevent truncation
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tag: self.add_tag_visual(t))
            btn.tag = tag
            return btn

    def refresh_tag_buttons(self):
        """Refresh all tag button displays"""
        # Clear selected tags layout
        self.selected_tags_layout.clear()

        # Clear available tags layout
        self.available_tags_layout.clear()

        self.selected_tag_buttons.clear()
        self.available_tag_buttons.clear()

        # Create selected tag buttons with wrapping
        col = 0
        max_cols = 4  # Number of tag buttons per row
        for tag in self.filename_template:
            if tag in self.all_tags:
                btn = self.create_tag_button(tag, is_selected=True)
                self.selected_tags_layout.addWidget(btn)
                self.selected_tag_buttons.append(btn)
                col += 1
                # Start new row after max_cols buttons
                if col >= max_cols:
                    self.selected_tags_layout.newRow()
                    col = 0

        # Create available tag buttons with wrapping support
        col = 0
        max_cols = 4  # Number of buttons per row
        for tag in self.all_tags:
            if tag not in self.filename_template:
                btn = self.create_tag_button(tag, is_selected=False)
                self.available_tags_layout.addWidget(btn)
                self.available_tag_buttons.append(btn)
                col += 1
                # Start new row after max_cols buttons
                if col >= max_cols:
                    self.available_tags_layout.newRow()
                    col = 0

    def add_tag_visual(self, tag):
        """Add tag from available to selected"""
        if tag and tag not in self.filename_template:
            self.filename_template.append(tag)
            self.refresh_tag_buttons()
            self.update_filename_preview()

    def remove_tag_visual(self, tag):
        """Remove tag from selected"""
        if tag and tag in self.filename_template:
            self.filename_template.remove(tag)
            self.refresh_tag_buttons()
            self.update_filename_preview()

    def on_tags_reordered(self):
        """Handle when tags are reordered by drag-drop"""
        # This will be implemented with drag-drop functionality if needed
        # For now, users can remove and re-add tags to reorder
        pass

    def update_filename_preview(self):
        """Update the filename preview"""
        # Create example filename
        example_data = {
            'title': 'Example Video Title',
            'uploader': 'Channel Name',
            'quality': '1080p',
            'format': 'mp4',
            'website': 'YouTube',
            'id': 'dQw4w9WgXcQ',
            'upload_date': '20260115',
            'download_date': '1749000000',
            'duration': '03-45-20',
            'ext': 'mp4'
        }

        # Build filename from template
        parts = []
        for tag in self.filename_template:
            if tag in example_data:
                parts.append(example_data[tag])

        filename = ' - '.join(parts) + '.mp4'
        self.filename_preview.setText(filename)

    def build_filename_template(self):
        """Build yt-dlp output template from selected tags"""
        # Map our tags to yt-dlp template variables
        tag_mapping = {
            'title': '%(title)s',
            'uploader': '%(uploader)s',
            'quality': '%(height)sp' if self.format_combo.currentText() == 'Video' else '%(abr)skbps',
            'format': '%(format_id)s',
            'website': '%(extractor)s',
            'id': '%(id)s',
            'upload_date': '%(upload_date)s',
            'download_date': '%(epoch)s',
            'duration': '%(duration_string)s',
            'ext': '%(ext)s'
        }

        # Build template parts
        parts = []
        for tag in self.filename_template:
            if tag in tag_mapping:
                parts.append(tag_mapping[tag])

        # Join with separator; always append .%(ext)s unless the template already
        # includes the extension placeholder (i.e. the user selected the 'ext' tag).
        if parts:
            template = ' - '.join(parts)
            if '%(ext)s' not in template:
                template += '.%(ext)s'
            return template
        else:
            return '%(title)s.%(ext)s'  # Fallback to default
