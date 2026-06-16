#!/usr/bin/env python3
"""
AV Morning Star - Media Downloader
A PyQt5 application for downloading videos and audio from URLs
"""

import sys
import os
import pathlib

# Import application constants
from constants import *
from themes import THEMES

# Suppress Qt Wayland warnings
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.wayland=false'

# Add Deno to PATH if installed (required for YouTube PO tokens)
deno_path = os.path.expanduser('~/.deno/bin')
if os.path.exists(deno_path) and deno_path not in os.environ.get('PATH', ''):
    os.environ['PATH'] = f"{deno_path}:{os.environ.get('PATH', '')}"
    os.environ['DENO_INSTALL'] = os.path.expanduser('~/.deno')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QComboBox, QProgressBar,
                             QCheckBox, QScrollArea, QGroupBox, QMessageBox,
                             QFileDialog, QSplashScreen, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QPainterPath

# Import our modular extractors
from extractors import is_youtube_url

# Import browser detection utilities
from browser_utils import detect_available_browsers, get_browsers_with_youtube_cookies

from threads import URLScraperThread, DownloadThread
from dialogs import PreferencesDialog
from settings import (
    load_browser_preference,
    load_output_path,
    load_theme,
    save_output_path,
    save_theme,
)


class FlowLayout(QVBoxLayout):
    """Custom layout that flows items left-to-right and wraps to new rows"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(10)
        self.rows = []

    def addWidget(self, widget):
        # Find current row or create new one
        if not self.rows or not hasattr(self, '_current_row'):
            self._current_row = QHBoxLayout()
            self._current_row.setSpacing(10)
            self._current_row.setAlignment(Qt.AlignLeft)
            super().addLayout(self._current_row)
            self.rows.append(self._current_row)

        self._current_row.addWidget(widget)

    def newRow(self):
        """Force a new row"""
        self._current_row = QHBoxLayout()
        self._current_row.setSpacing(10)
        self._current_row.setAlignment(Qt.AlignLeft)
        super().addLayout(self._current_row)
        self.rows.append(self._current_row)

    def clear(self):
        """Clear all widgets"""
        while self.count():
            item = self.takeAt(0)
            if item.layout():
                while item.layout().count():
                    widget_item = item.layout().takeAt(0)
                    if widget_item.widget():
                        widget_item.widget().deleteLater()
                item.layout().deleteLater()
        self.rows = []


class VideoCheckbox(QWidget):
    """Custom widget combining a checkbox with a word-wrapping label"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(8)

        # Checkbox (indicator only)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        layout.addWidget(self.checkbox, 0, Qt.AlignTop)

        # Label with word wrap
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.mousePressEvent = self._on_label_click
        layout.addWidget(self.label, 1)  # Stretch factor 1 to take remaining space

    def _on_label_click(self, event):
        """Toggle checkbox when label is clicked"""
        self.checkbox.setChecked(not self.checkbox.isChecked())

    def isChecked(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked):
        self.checkbox.setChecked(checked)


def make_circular_pixmap(pixmap):
    """Create a circular version of a pixmap"""
    size = min(pixmap.width(), pixmap.height())
    circular = QPixmap(size, size)
    circular.fill(Qt.transparent)

    painter = QPainter(circular)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    # Scale the pixmap to fill the circle completely
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Center the scaled image
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()

    return circular


class MediaDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.videos_list = []
        self.checkboxes = []
        self.output_path = os.path.expanduser(load_output_path())
        self.mode = MODE_BASIC  # Default to basic mode
        self.filename_template = DEFAULT_FILENAME_TAGS.copy()  # Default template

        self.browser_preference = load_browser_preference()

        # Track if we've tried cookieless and it failed
        self.cookieless_failed = False

        self.current_theme = load_theme()

        self.init_ui()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)

        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), ICON_FILENAME)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Create menu bar
        menubar = self.menuBar()

        # View menu
        view_menu = menubar.addMenu("View")
        self.dark_mode_action = view_menu.addAction("Dark Mode")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.current_theme == "dark")
        self.dark_mode_action.triggered.connect(self._on_theme_toggle)

        # Tools menu
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

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Banner with icon
        banner_layout = QHBoxLayout()
        banner_layout.addStretch()  # Add stretch before content to center it

        # Icon in banner
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            circular_pixmap = make_circular_pixmap(scaled_pixmap)
            icon_label.setPixmap(circular_pixmap)
            banner_layout.addWidget(icon_label)

        # Title section
        title_layout = QVBoxLayout()
        title = QLabel(APP_NAME)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)

        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)

        banner_layout.addLayout(title_layout)
        banner_layout.addStretch()  # Add stretch after content to center it

        main_layout.addLayout(banner_layout)

        # URL Input Section
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

        # Create horizontal layout for Videos List and Filename Template
        content_row = QHBoxLayout()

        # Videos List Section (LEFT SIDE)
        videos_group = QGroupBox(GROUP_AVAILABLE_VIDEOS)
        videos_layout = QVBoxLayout()

        # Scroll area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(120)
        scroll.setMaximumHeight(180)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scroll

        self.videos_container = QWidget()
        self.videos_container_layout = QVBoxLayout(self.videos_container)
        scroll.setWidget(self.videos_container)

        videos_layout.addWidget(scroll)

        # Select all/none buttons
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
        content_row.addWidget(videos_group, 2)  # Stretch factor 2 - larger

        # Filename Template Section (RIGHT SIDE)
        filename_group = QGroupBox(GROUP_FILENAME_TEMPLATE)
        filename_layout = QVBoxLayout()

        # Selected tags container (top section)
        selected_label = QLabel("Selected Tags (click to remove):")
        filename_layout.addWidget(selected_label)

        # Frame for selected tags with wrapping
        selected_frame = QWidget()
        selected_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.selected_tags_layout = FlowLayout(selected_frame)
        self.selected_tags_layout.setSpacing(10)
        filename_layout.addWidget(selected_frame)
        self._selected_frame = selected_frame

        filename_layout.addSpacing(10)

        # Available tags container (bottom section)
        available_label = QLabel("Available Tags (click to add):")
        filename_layout.addWidget(available_label)

        # Frame for available tags with wrapping
        available_frame = QWidget()
        available_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.available_tags_layout = FlowLayout(available_frame)
        self.available_tags_layout.setSpacing(10)
        filename_layout.addWidget(available_frame)
        self._available_frame = available_frame

        filename_layout.addSpacing(10)

        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.filename_preview = QLabel("")
        self.filename_preview.setStyleSheet("QLabel { font-family: monospace; font-weight: bold; }")
        self.filename_preview.setWordWrap(True)
        self.filename_preview.setMaximumHeight(60)
        preview_layout.addWidget(self.filename_preview)
        filename_layout.addLayout(preview_layout)

        filename_group.setLayout(filename_layout)
        filename_group.setMaximumWidth(450)  # Compact width
        content_row.addWidget(filename_group)  # No stretch - fixed size

        # Add the horizontal row to main layout
        main_layout.addLayout(content_row)

        # Initialize filename tags
        self.init_filename_tags()

        # Download Options Section
        options_group = QGroupBox(GROUP_DOWNLOAD_OPTIONS)
        options_layout = QVBoxLayout()

        # First row: Mode and Format in grid
        top_grid = QGridLayout()
        top_grid.setSpacing(10)

        top_grid.addWidget(QLabel("Mode:"), 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Basic (Auto-detect best quality)", "Advanced (Manual settings)"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        top_grid.addWidget(self.mode_combo, 0, 1)

        top_grid.addWidget(QLabel("Format:"), 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video", "Audio Only"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        top_grid.addWidget(self.format_combo, 0, 3)

        options_layout.addLayout(top_grid)

        # === VIDEO OPTIONS (shown when Video is selected) ===
        self.video_options_widget = QWidget()
        video_options_layout = QVBoxLayout(self.video_options_widget)
        video_options_layout.setContentsMargins(0, 5, 0, 5)
        video_options_layout.setSpacing(8)

        # Video format row
        video_format_layout = QGridLayout()
        video_format_layout.setSpacing(10)

        video_format_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(VIDEO_QUALITIES)
        video_format_layout.addWidget(self.quality_combo, 0, 1)

        video_format_layout.addWidget(QLabel("Video Format:"), 0, 2)
        self.video_container_combo = QComboBox()
        self.video_container_combo.addItems(VIDEO_CONTAINERS)
        self.video_container_combo.currentTextChanged.connect(self.on_video_format_changed)
        video_format_layout.addWidget(self.video_container_combo, 0, 3)

        self.subtitles_checkbox = QCheckBox("Download Subtitles")
        self.subtitles_checkbox.setChecked(False)
        video_format_layout.addWidget(self.subtitles_checkbox, 0, 4)

        video_options_layout.addLayout(video_format_layout)

        # Video enhancement options row
        video_enhance_layout = QHBoxLayout()
        video_enhance_layout.setSpacing(15)

        self.video_denoise_checkbox = QCheckBox("Denoise Video")
        self.video_denoise_checkbox.setChecked(False)
        self.video_denoise_checkbox.setToolTip(
            "Remove video noise/grain using hqdn3d 3D temporal denoiser.\n"
            "Uses balanced settings (4:3:6:4.5) for quality preservation.\n"
            "Best for: grainy footage, low-light recordings"
        )
        video_enhance_layout.addWidget(self.video_denoise_checkbox)

        self.video_stabilize_checkbox = QCheckBox("Stabilize Video")
        self.video_stabilize_checkbox.setChecked(False)
        self.video_stabilize_checkbox.setToolTip(
            "Reduce camera shake using deshake filter (single-pass).\n"
            "Uses 32px search range with edge mirroring.\n"
            "Best for: mild handheld shake; severe shake may need vidstab.\n"
            "Note: May add processing time"
        )
        video_enhance_layout.addWidget(self.video_stabilize_checkbox)

        self.video_sharpen_checkbox = QCheckBox("Sharpen")
        self.video_sharpen_checkbox.setChecked(False)
        self.video_sharpen_checkbox.setToolTip(
            "Enhance video sharpness using unsharp mask filter.\n"
            "Uses moderate settings (5x5 kernel, 0.8 strength).\n"
            "Best for: slightly soft footage, after denoising"
        )
        video_enhance_layout.addWidget(self.video_sharpen_checkbox)

        video_enhance_layout.addStretch()
        video_options_layout.addLayout(video_enhance_layout)

        # Video audio enhancement options row
        video_audio_layout = QHBoxLayout()
        video_audio_layout.setSpacing(15)

        self.video_normalize_audio_checkbox = QCheckBox("Normalize Audio")
        self.video_normalize_audio_checkbox.setChecked(False)
        self.video_normalize_audio_checkbox.setToolTip(
            "Normalize audio to EBU R128 broadcast standard.\n"
            "Target: -16 LUFS with -1.5 dB true peak limit.\n"
            "Includes sample rate correction (48kHz).\n"
            "Best for: consistent playback volume"
        )
        video_audio_layout.addWidget(self.video_normalize_audio_checkbox)

        self.video_denoise_audio_checkbox = QCheckBox("Denoise Audio")
        self.video_denoise_audio_checkbox.setChecked(False)
        self.video_denoise_audio_checkbox.setToolTip(
            "Remove background noise using FFT-based filter.\n"
            "Uses adaptive noise floor tracking (-20dB, 15dB reduction).\n"
            "Best for: recordings with hiss, hum, or ambient noise"
        )
        video_audio_layout.addWidget(self.video_denoise_audio_checkbox)

        video_audio_layout.addStretch()
        video_options_layout.addLayout(video_audio_layout)

        options_layout.addWidget(self.video_options_widget)

        # === AUDIO OPTIONS (shown when Audio Only is selected) ===
        self.audio_options_widget = QWidget()
        audio_options_layout = QVBoxLayout(self.audio_options_widget)
        audio_options_layout.setContentsMargins(0, 5, 0, 5)
        audio_options_layout.setSpacing(8)

        # Audio codec and quality row
        audio_format_layout = QGridLayout()
        audio_format_layout.setSpacing(10)

        audio_format_layout.addWidget(QLabel("Audio Codec:"), 0, 0)
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(AUDIO_CODECS)
        self.audio_codec_combo.currentTextChanged.connect(self.on_audio_codec_changed)
        audio_format_layout.addWidget(self.audio_codec_combo, 0, 1)

        audio_format_layout.addWidget(QLabel("Audio Quality:"), 0, 2)
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(AUDIO_BITRATES)
        self.audio_quality_combo.setCurrentIndex(3)  # Default to 192 kbps
        audio_format_layout.addWidget(self.audio_quality_combo, 0, 3)

        self.embed_thumbnail_checkbox = QCheckBox("Embed Thumbnail")
        self.embed_thumbnail_checkbox.setChecked(True)
        self.embed_thumbnail_checkbox.setToolTip("Embed album art/thumbnail in audio file")
        audio_format_layout.addWidget(self.embed_thumbnail_checkbox, 0, 4)

        audio_options_layout.addLayout(audio_format_layout)

        # Audio enhancement options row
        audio_enhance_layout = QHBoxLayout()
        audio_enhance_layout.setSpacing(15)

        self.normalize_audio_checkbox = QCheckBox("Normalize Audio (EBU R128)")
        self.normalize_audio_checkbox.setChecked(False)
        self.normalize_audio_checkbox.setToolTip(
            "Professional loudness normalization to EBU R128 standard.\n"
            "Target: -16 LUFS, loudness range 11 LU, true peak -1.5 dB.\n"
            "Includes sample rate correction to prevent drift.\n"
            "Best for: broadcast, streaming, consistent playback"
        )
        audio_enhance_layout.addWidget(self.normalize_audio_checkbox)

        self.dynamic_norm_checkbox = QCheckBox("Dynamic Normalization")
        self.dynamic_norm_checkbox.setChecked(False)
        self.dynamic_norm_checkbox.setToolTip(
            "Dynamic audio normalizer for varying volume levels.\n"
            "Uses: 95% peak target, 10dB max gain, smooth transitions.\n"
            "Alternative to EBU R128 for podcasts/lectures.\n"
            "Best for: speech with varying loudness"
        )
        audio_enhance_layout.addWidget(self.dynamic_norm_checkbox)

        self.denoise_checkbox = QCheckBox("Denoise Audio")
        self.denoise_checkbox.setChecked(False)
        self.denoise_checkbox.setToolTip(
            "Remove background noise using FFT-based filter.\n"
            "Uses adaptive noise floor tracking for best results.\n"
            "Settings: -20dB floor, 15dB reduction, adaptive tracking.\n"
            "Best for: recordings with hiss, hum, or ambient noise"
        )
        audio_enhance_layout.addWidget(self.denoise_checkbox)

        audio_enhance_layout.addStretch()
        audio_options_layout.addLayout(audio_enhance_layout)

        options_layout.addWidget(self.audio_options_widget)

        # Hide audio options initially (Video is default)
        self.audio_options_widget.setVisible(False)

        # Output path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save to:"))
        self.path_label = QLabel(self.output_path)
        path_layout.addWidget(self.path_label)

        self.browse_btn = QPushButton(BTN_BROWSE)
        self.browse_btn.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.browse_btn)

        options_layout.addLayout(path_layout)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Store advanced option widgets for show/hide
        self.advanced_widgets = [
            self.quality_combo, self.video_container_combo, self.audio_codec_combo, self.audio_quality_combo,
            self.embed_thumbnail_checkbox, self.normalize_audio_checkbox,
            self.dynamic_norm_checkbox, self.denoise_checkbox
        ]
        self.advanced_labels = []

        # Set initial mode to Basic (hide advanced options)
        self.on_mode_changed("Basic (Auto-detect best quality)")

        # Download Button
        self.download_btn = QPushButton(BTN_DOWNLOAD_SELECTED)
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        main_layout.addWidget(self.download_btn)

        # Progress Section
        progress_group = QGroupBox(GROUP_PROGRESS)
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(STATUS_READY)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        self.statusBar().showMessage(STATUS_READY)

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

    def on_mode_changed(self, text):
        """Toggle between Basic and Advanced modes"""
        if "Basic" in text:
            self.mode = 'basic'
            # Hide both video and audio options in basic mode
            self.video_options_widget.setVisible(False)
            self.audio_options_widget.setVisible(False)
        else:
            self.mode = 'advanced'
            # Show appropriate options based on format selection
            self.on_format_changed(self.format_combo.currentText())

    def on_format_changed(self, text):
        """Show/hide relevant options based on format selection"""
        if text == "Audio Only":
            # Show audio options, hide video options
            self.video_options_widget.setVisible(False)
            if self.mode == 'advanced':
                self.audio_options_widget.setVisible(True)
        else:
            # Show video options, hide audio options
            self.audio_options_widget.setVisible(False)
            if self.mode == 'advanced':
                self.video_options_widget.setVisible(True)

    def on_video_format_changed(self, text):
        """Enable/disable video enhancement options based on container format compatibility"""
        # Formats that support video enhancement (re-encoding with filters)
        # MP4, MKV, MOV, WebM support modern codecs and filter chains
        # AVI, FLV are legacy formats with limited codec support - filters cause errors
        supported_formats = ['MP4', 'MKV', 'MOV', 'WebM']
        format_supports_enhancement = text in supported_formats

        # Video enhancement checkboxes
        video_enhancement_checkboxes = [
            self.video_denoise_checkbox,
            self.video_stabilize_checkbox,
            self.video_sharpen_checkbox,
            self.video_normalize_audio_checkbox,
            self.video_denoise_audio_checkbox,
        ]

        # Original tooltips for when enabled
        original_tooltips = {
            self.video_denoise_checkbox: (
                "Remove video noise/grain using hqdn3d 3D temporal denoiser.\n"
                "Uses balanced settings (4:3:6:4.5) for quality preservation.\n"
                "Best for: grainy footage, low-light recordings"
            ),
            self.video_stabilize_checkbox: (
                "Reduce camera shake using deshake filter (single-pass).\n"
                "Uses 32px search range with edge mirroring.\n"
                "Best for: mild handheld shake; severe shake may need vidstab.\n"
                "Note: May add processing time"
            ),
            self.video_sharpen_checkbox: (
                "Enhance video sharpness using unsharp mask filter.\n"
                "Uses moderate settings (5x5 kernel, 0.8 strength).\n"
                "Best for: slightly soft footage, after denoising"
            ),
            self.video_normalize_audio_checkbox: (
                "Normalize audio to EBU R128 broadcast standard.\n"
                "Target: -16 LUFS with -1.5 dB true peak limit.\n"
                "Includes sample rate correction (48kHz).\n"
                "Best for: consistent playback volume"
            ),
            self.video_denoise_audio_checkbox: (
                "Remove background noise using FFT-based filter.\n"
                "Uses adaptive noise floor tracking (-20dB, 15dB reduction).\n"
                "Best for: recordings with hiss, hum, or ambient noise"
            ),
        }

        for checkbox in video_enhancement_checkboxes:
            checkbox.setEnabled(format_supports_enhancement)
            if format_supports_enhancement:
                # Restore original tooltip
                checkbox.setToolTip(original_tooltips[checkbox])
            else:
                # Uncheck and show disabled tooltip
                checkbox.setChecked(False)
                checkbox.setToolTip(
                    f"Not available for {text} format.\n\n"
                    f"{text} is a legacy format with limited codec support.\n"
                    f"Video enhancement requires re-encoding which isn't\n"
                    f"compatible with {text}.\n\n"
                    f"Use MP4, MKV, MOV, or WebM for video enhancement."
                )

    def on_audio_codec_changed(self, text):
        """Enable/disable audio options based on codec compatibility"""
        # Codecs that support thumbnail embedding (have metadata containers)
        # WAV is raw audio with no metadata support
        # FLAC supports metadata but thumbnail embedding can be problematic
        thumbnail_supported_codecs = ['MP3', 'AAC', 'M4A', 'Opus', 'OGG Vorbis', 'FLAC', 'ALAC']
        codec_supports_thumbnail = text in thumbnail_supported_codecs

        # Handle thumbnail embedding
        self.embed_thumbnail_checkbox.setEnabled(codec_supports_thumbnail)
        if codec_supports_thumbnail:
            self.embed_thumbnail_checkbox.setToolTip("Embed album art/thumbnail in audio file")
        else:
            self.embed_thumbnail_checkbox.setChecked(False)
            self.embed_thumbnail_checkbox.setToolTip(
                f"Not available for {text} format.\n\n"
                f"{text} is a raw audio format without metadata support.\n"
                f"Thumbnails cannot be embedded in this format.\n\n"
                f"Use MP3, AAC, M4A, FLAC, or OGG for thumbnail embedding."
            )

        # Lossless codecs should disable bitrate selection (use quality 0)
        lossless_codecs = ['FLAC', 'WAV', 'ALAC']
        is_lossless = text in lossless_codecs

        # When lossless codec is selected, show only Lossless quality option meaningfully
        # Other codecs can use bitrate selection
        if is_lossless:
            # For lossless, bitrate doesn't apply - select Lossless if available
            lossless_index = self.audio_quality_combo.findText("Lossless")
            if lossless_index >= 0:
                self.audio_quality_combo.setCurrentIndex(lossless_index)
            self.audio_quality_combo.setToolTip(
                f"{text} is a lossless codec.\n"
                f"Quality setting doesn't affect file size or quality.\n"
                f"Audio will be stored at full quality."
            )
        else:
            self.audio_quality_combo.setToolTip(
                "Select audio bitrate (higher = better quality, larger file)"
            )

    def fetch_videos(self):
        """Fetch videos from URL"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Error", "Please enter a valid URL starting with http:// or https://")
            return

        # Prevent re-entrant fetch while a scrape is already in flight.
        if hasattr(self, 'scraper_thread') and self.scraper_thread is not None and self.scraper_thread.isRunning():
            return

        # Reset per-request state so each new user-initiated fetch starts clean.
        # on_fetch_error sets this True then immediately calls fetch_videos() for the
        # bot-detection retry; that retry call relies on explicit_browser_chosen (not
        # this flag), so resetting here is safe and prevents the flag from leaking
        # across separate user requests.
        self.cookieless_failed = False

        # Smart cookie detection strategy:
        # 1. For YouTube URLs: Try cookieless first (unless we know it failed before)
        # 2. If cookieless fails with bot detection, auto-retry with best browser
        # 3. For non-YouTube URLs: Use cookies if available

        cookies_from_browser = None
        is_youtube = is_youtube_url(url)

        # Resolve explicit browser preference only — never probe cookie stores here.
        # Auto mode defers cookie reads until on_fetch_error prompts the user.
        resolved_browser = None
        if self.browser_preference not in ('auto', 'none'):
            resolved_browser = self.browser_preference

        if is_youtube:
            # YouTube authentication strategy:
            # - 'auto' mode: always try cookieless first; only use cookies after a
            #   bot-detection failure for this request (see on_fetch_error).
            # - explicit browser preference: use that browser immediately.
            # - 'none': never use cookies.
            explicit_browser_chosen = self.browser_preference not in ('auto', 'none')
            if self.cookieless_failed or explicit_browser_chosen:
                # Either a prior bot-detection failure on this URL forced a retry,
                # or the user explicitly selected a specific browser.
                if resolved_browser:
                    cookies_from_browser = resolved_browser
                    browser_display = resolved_browser.title()
                    if explicit_browser_chosen:
                        self.status_label.setText(f"Fetching with {browser_display} authentication...")
                    else:
                        self.status_label.setText(f"Retrying with {browser_display} authentication...")
                else:
                    self.status_label.setText("Fetching (no authentication)...")
            else:
                # Auto or none mode on first attempt: go cookieless
                self.status_label.setText("Fetching video information (no authentication)...")
        else:
            # Non-YouTube: only use cookies when the user explicitly chose a browser.
            # Auto-forwarding cookies to arbitrary sites is an unnecessary privacy risk.
            if self.browser_preference not in ('auto', 'none') and resolved_browser:
                cookies_from_browser = resolved_browser

        self.statusBar().showMessage("Connecting to URL...")
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)

        # Clear previous results
        self.clear_videos_list()

        # Start scraping thread
        self.scraper_thread = URLScraperThread(
            url,
            cookies_from_browser=cookies_from_browser
        )
        # Record the auth decision made for this fetch so start_download can
        # mirror it exactly, preserving the Auto-mode privacy contract.
        self._fetch_cookies_used = cookies_from_browser
        self.scraper_thread.finished.connect(self.on_videos_fetched)
        self.scraper_thread.error.connect(self.on_fetch_error)
        self.scraper_thread.start()

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

    def parse_cookie_error(self, error):
        """Parse yt-dlp cookie errors into user-friendly messages"""
        error_lower = error.lower()

        # Cookie database not found errors
        if 'could not find' in error_lower and 'cookies database' in error_lower:
            # Extract browser name from error
            for browser in ['firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera', 'vivaldi']:
                if browser in error_lower:
                    browser_display = browser.title()

                    # Get available browsers
                    available = detect_available_browsers()

                    if available:
                        msg = (
                            f"❌ {browser_display} cookies not found\n\n"
                            f"The selected browser ({browser_display}) doesn't appear to be installed "
                            f"or doesn't have cookies on this system.\n\n"
                            f"Installed browsers on this system:\n"
                        )

                        for b in available:
                            msg += f"  • {b.title()}\n"
                        msg += (
                            f"\n💡 Recommendation: Sign into YouTube in one of these browsers, "
                            f"then use 'Auto (Recommended)' mode in Tools > Preferences."
                        )
                    else:
                        msg = (
                            f"❌ {browser_display} not found\n\n"
                            f"I couldn't find {browser_display} or any other supported browsers on your system.\n\n"
                            f"Supported browsers: Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi\n\n"
                            f"💡 Recommendation: Install a browser, sign into YouTube, then use 'Auto (Recommended)' mode."
                        )

                    return msg

        # Corrupted cookie database
        if 'database' in error_lower and ('corrupt' in error_lower or 'malformed' in error_lower):
            return (
                "❌ Browser cookie database is corrupted\n\n"
                "The selected browser's cookie file appears to be damaged or corrupted.\n\n"
                "💡 Try these solutions:\n"
                "  1. Restart your browser and try again\n"
                "  2. Use 'Auto (Recommended)' to try a different browser\n"
                "  3. Clear browser cookies and sign into YouTube again\n"
            )

        # Permission errors
        if 'permission denied' in error_lower or 'access denied' in error_lower:
            return (
                "❌ Permission denied\n\n"
                "Cannot access browser cookies due to file permissions.\n\n"
                "💡 This can happen if:\n"
                "  - The browser is currently running (some browsers lock cookie files)\n"
                "  - Your user account doesn't have permission to read the cookie file\n\n"
                "Try closing the browser and running this app again."
            )

        # No user-friendly version available
        return None

    def on_fetch_error(self, error):
        """Handle fetch error with smart cookie retry"""
        # Parse common yt-dlp cookie errors into user-friendly messages
        user_friendly_error = self.parse_cookie_error(error)

        # Check if this is a YouTube bot detection error
        error_lower = error.lower()
        is_bot_error = (
            'sign in to confirm' in error_lower
            or ('bot' in error_lower and 'youtube' in error_lower)
        )

        url = self.url_input.text().strip()
        is_youtube = is_youtube_url(url)

        # If YouTube bot detection and we haven't tried cookies yet
        if is_youtube and is_bot_error and not self.cookieless_failed:
            self.cookieless_failed = True

            # Try to find a browser with YouTube cookies
            browsers_with_youtube = get_browsers_with_youtube_cookies()

            if browsers_with_youtube:
                # Auto-retry with detected browser — do NOT mutate browser_preference
                # so the user's original setting is preserved for future requests.
                browser = browsers_with_youtube[0]

                reply = QMessageBox.question(
                    self,
                    "YouTube Authentication Required",
                    f"YouTube is requesting authentication to prevent bot access.\n\n"
                    f"Good news! I detected you're logged into YouTube in {browser.title()}.\n\n"
                    f"Would you like to retry using your {browser.title()} login?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # Temporarily override resolved_browser for this single retry by
                    # storing it in a per-request attribute; fetch_videos reads
                    # cookieless_failed and will pick up resolved_browser from
                    # browser_preference — so we set it only for the retry call and
                    # immediately restore the original value.
                    original_preference = self.browser_preference
                    self.browser_preference = browser
                    self.status_label.setText(f"Retrying with {browser} authentication...")
                    self.fetch_videos()  # Retry automatically
                    # Re-assert the flag now that fetch_videos() has reset it.
                    # This prevents on_fetch_error from re-prompting if the retry
                    # itself also triggers a bot-detection failure.
                    self.cookieless_failed = True
                    self.browser_preference = original_preference  # Restore
                    return
                else:
                    # User declined, show error
                    self.cookieless_failed = False  # Reset so next fetch starts clean
                    self.fetch_btn.setEnabled(True)
                    self.status_label.setText("Authentication declined")
                    self.statusBar().showMessage("YouTube authentication required")
                    return
            else:
                # No browsers with YouTube cookies found
                available_browsers = detect_available_browsers()

                if available_browsers:
                    msg = (
                        f"YouTube requires authentication to download this video.\n\n"
                        f"I found these browsers on your system:\n"
                        f"  • {', '.join([b.title() for b in available_browsers])}\n\n"
                        f"To fix this:\n"
                        f"1. Sign into YouTube in one of these browsers\n"
                        f"2. Go to Tools > Preferences\n"
                        f"3. Select your browser\n"
                        f"4. Try fetching again\n\n"
                        f"Technical details: {error[:200]}"
                    )
                else:
                    msg = (
                        f"YouTube requires authentication, but I couldn't find any supported browsers.\n\n"
                        f"Supported browsers: Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi\n\n"
                        f"Please install a browser and sign into YouTube, then try again.\n\n"
                        f"Technical details: {error[:200]}"
                    )

                self.fetch_btn.setEnabled(True)
                self.status_label.setText("Authentication required")
                self.statusBar().showMessage("YouTube authentication required")
                QMessageBox.warning(self, "Authentication Required", msg)
                return

        # Not a bot error, or already tried cookies - show error.
        # Reset the retry flag so the next fresh user request starts cookieless again.
        self.cookieless_failed = False
        self.fetch_btn.setEnabled(True)
        self.status_label.setText("Error fetching videos")
        self.statusBar().showMessage("Failed to fetch videos")

        # Show user-friendly error if available, otherwise show technical error
        if user_friendly_error:
            QMessageBox.critical(self, "Error", user_friendly_error)
        else:
            QMessageBox.critical(self, "Error", error)

    def select_all(self):
        """Select all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def select_none(self):
        """Deselect all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    def start_download(self):
        """Start downloading selected videos"""
        selected_urls = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected_urls.append(self.videos_list[i]['url'])

        if not selected_urls:
            QMessageBox.warning(self, "Error", "Please select at least one video to download")
            return

        # Gather download options
        format_type = 'audio' if self.format_combo.currentText() == "Audio Only" else 'video'

        # In Basic mode, use auto-detect best settings
        if self.mode == 'basic':
            video_quality = 'Best'  # Auto-detect best quality
            video_container = 'mp4'  # Most compatible
            audio_codec = 'mp3'  # Most compatible
            audio_quality = '320'  # Highest quality
            download_subs = False
            embed_thumbnail = True if format_type == 'audio' else False  # Always embed for audio
            normalize_audio = False
            dynamic_normalization = False  # Use standard EBU R128
            denoise_audio = False  # Don't denoise by default
            # Video enhancement (off in basic mode)
            denoise_video = False
            stabilize_video = False
            sharpen_video = False
            normalize_video_audio = False
            denoise_video_audio = False
        else:
            # Advanced mode - use manual settings
            video_quality = self.quality_combo.currentText() if format_type == 'video' else None
            video_container = self.video_container_combo.currentText().lower() if format_type == 'video' else None
            audio_codec_label = self.audio_codec_combo.currentText()
            # Map UI labels to the codec names yt-dlp's FFmpegExtractAudio expects.
            # String-munging cannot handle all cases (e.g. "OGG Vorbis" → "vorbis"),
            # so use an explicit table instead.
            _codec_map = {
                'MP3': 'mp3',
                'AAC': 'aac',
                'FLAC': 'flac',
                'Opus': 'opus',
                'M4A': 'm4a',
                'WAV': 'wav',
                'ALAC': 'alac',
                'OGG Vorbis': 'vorbis',
            }
            audio_codec = _codec_map.get(audio_codec_label, audio_codec_label.lower())
            audio_quality_text = self.audio_quality_combo.currentText()
            # Handle lossless vs bitrate
            if 'lossless' in audio_quality_text.lower():
                audio_quality = '0'  # Best quality for lossless codecs
            else:
                audio_quality = audio_quality_text.split()[0]  # Extract number from "192 kbps"
            download_subs = self.subtitles_checkbox.isChecked()
            embed_thumbnail = self.embed_thumbnail_checkbox.isChecked() if format_type == 'audio' else False
            normalize_audio = self.normalize_audio_checkbox.isChecked() if format_type == 'audio' else False
            dynamic_normalization = self.dynamic_norm_checkbox.isChecked() if format_type == 'audio' else False
            denoise_audio = self.denoise_checkbox.isChecked() if format_type == 'audio' else False
            # Video enhancement options
            denoise_video = self.video_denoise_checkbox.isChecked() if format_type == 'video' else False
            stabilize_video = self.video_stabilize_checkbox.isChecked() if format_type == 'video' else False
            sharpen_video = self.video_sharpen_checkbox.isChecked() if format_type == 'video' else False
            normalize_video_audio = self.video_normalize_audio_checkbox.isChecked() if format_type == 'video' else False
            denoise_video_audio = self.video_denoise_audio_checkbox.isChecked() if format_type == 'video' else False

        self.status_label.setText(f"Starting download of {len(selected_urls)} item(s)...")
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # Build filename template
        filename_template = self.build_filename_template()

        # Resolve output path to a canonical absolute path (guards against path traversal)
        output_path = str(pathlib.Path(self.output_path).resolve())

        # Validate output directory before spinning up the background thread so
        # filesystem problems are surfaced immediately as a clear, targeted error.
        if not os.path.exists(output_path):
            QMessageBox.critical(self, "Invalid Output Directory",
                                 f"The output directory does not exist:\n{output_path}\n\n"
                                 "Please choose a valid directory in the path selector.")
            self.download_btn.setEnabled(True)
            self.fetch_btn.setEnabled(True)
            self.status_label.setText("Invalid output directory")
            return
        if not os.path.isdir(output_path):
            QMessageBox.critical(self, "Invalid Output Directory",
                                 f"The selected path is not a directory:\n{output_path}")
            self.download_btn.setEnabled(True)
            self.fetch_btn.setEnabled(True)
            self.status_label.setText("Invalid output directory")
            return
        if not os.access(output_path, os.W_OK):
            QMessageBox.critical(self, "Output Directory Not Writable",
                                 f"Cannot write to the output directory:\n{output_path}\n\n"
                                 "Check file permissions and try again.")
            self.download_btn.setEnabled(True)
            self.fetch_btn.setEnabled(True)
            self.status_label.setText("Output directory not writable")
            return

        # Use the same browser cookies that were resolved during the fetch.
        # This ensures downloads are authenticated if and only if the preceding
        # fetch actually used authentication, preserving the Auto-mode privacy
        # contract (cookieless unless bot-detection forced a retry).
        resolved_browser = getattr(self, '_fetch_cookies_used', None)

        # Start download thread with browser cookies
        self.download_thread = DownloadThread(
            selected_urls, output_path, format_type, video_quality,
            audio_codec, audio_quality, download_subs, embed_thumbnail, normalize_audio,
            denoise_audio, dynamic_normalization, filename_template,
            cookies_from_browser=resolved_browser, video_container=video_container,
            denoise_video=denoise_video, stabilize_video=stabilize_video,
            sharpen_video=sharpen_video, normalize_video_audio=normalize_video_audio,
            denoise_video_audio=denoise_video_audio
        )
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def on_download_progress(self, filename, percent):
        """Update download progress"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Downloading: {os.path.basename(filename)}")

    def on_download_finished(self, message):
        """Handle download completion"""
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_label.setText(message)
        self.statusBar().showMessage("All downloads completed!")
        QMessageBox.information(self, "Success", message)

    def on_download_error(self, error):
        """Handle download error"""
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Download failed")
        self.statusBar().showMessage("Download failed - check error message")
        QMessageBox.critical(self, "Error", error)

    def closeEvent(self, event):
        """Gracefully stop any running worker threads before closing."""
        threads = []
        if hasattr(self, 'scraper_thread') and self.scraper_thread is not None:
            threads.append(self.scraper_thread)
        if hasattr(self, 'download_thread') and self.download_thread is not None:
            threads.append(self.download_thread)

        running = [t for t in threads if t.isRunning()]
        if running:
            reply = QMessageBox.question(
                self, "Exit",
                "A download or fetch is still in progress. Exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return

        # Ask each thread to stop cooperatively, then wait for a clean exit.
        # We never call terminate() — forced teardown while yt-dlp is active
        # can leave partial files and undefined interpreter state.
        for t in running:
            t.requestInterruption()

        still_running = []
        for t in running:
            if not t.wait(5000):
                still_running.append(t)

        if still_running:
            # A thread did not stop in time; keep the window open so the user
            # can try again or wait longer rather than closing over a live thread.
            QMessageBox.warning(
                self, "Still stopping",
                "A background task is taking longer than expected to stop.\n"
                "Please wait a moment and try closing again.",
            )
            event.ignore()
            return

        event.accept()

    def show_preferences(self):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, ABOUT_WINDOW_TITLE, ABOUT_TEXT)

    def show_help(self):
        """Show help dialog"""
        help_text = HELP_GETTING_STARTED + HELP_YOUTUBE_AUTH + HELP_SUPPORTED_SITES + HELP_MORE_INFO
        msg = QMessageBox(self)
        msg.setWindowTitle(HELP_WINDOW_TITLE)
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    # ------------------------------------------------------------------
    # Theme helpers
    # ------------------------------------------------------------------

    def _on_theme_toggle(self, checked):
        """Called when the View > Dark Mode menu item is toggled."""
        self.apply_theme("dark" if checked else "light")

    def apply_theme(self, theme_name):
        """Apply *theme_name* ('dark' or 'light') to the whole application."""
        from themes import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        self.current_theme = theme_name
        save_theme(theme_name)

        # Apply global QSS
        QApplication.instance().setStyleSheet(theme["stylesheet"])

        # Sync the menu checkbox without re-triggering the signal
        if hasattr(self, "dark_mode_action"):
            self.dark_mode_action.blockSignals(True)
            self.dark_mode_action.setChecked(theme_name == "dark")
            self.dark_mode_action.blockSignals(False)

        # Update dynamically-styled widgets that QSS can't reach cleanly
        v = theme["vars"]
        if hasattr(self, "_selected_frame"):
            self._selected_frame.setStyleSheet(
                f"QWidget {{ background-color: {v['frame_bg']}; "
                f"border: 2px solid {v['frame_border']}; "
                f"border-radius: 5px; padding: 5px; }}"
            )
        if hasattr(self, "_available_frame"):
            self._available_frame.setStyleSheet(
                f"QWidget {{ background-color: {v['frame_bg']}; "
                f"border: 2px solid {v['frame_border']}; "
                f"border-radius: 5px; padding: 5px; }}"
            )
        if hasattr(self, "filename_preview"):
            self.filename_preview.setStyleSheet(
                f"QLabel {{ font-family: monospace; color: {v['preview_fg']}; font-weight: bold; }}"
            )

        # Rebuild tag buttons so they pick up the new colours
        if hasattr(self, "refresh_tag_buttons"):
            self.refresh_tag_buttons()


def main():
    # Set WM_CLASS before creating QApplication (critical for KDE/Wayland)
    os.environ['RESOURCE_NAME'] = 'av-morning-star'

    app = QApplication(sys.argv)

    # Use Fusion style as the base so our QSS has consistent rendering across DEs
    app.setStyle("Fusion")

    # Set application name and icon for desktop environments
    app.setApplicationName("av-morning-star")
    app.setApplicationDisplayName(APP_FULL_TITLE)
    app.setDesktopFileName("com.github.asafelobotomy.avmorningstar.desktop")

    # Set application icon (affects taskbar and window decorations)
    icon_path = os.path.join(os.path.dirname(__file__), ICON_FILENAME)
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)  # Set for all windows

    # Show splash screen if icon exists
    if os.path.exists(icon_path):
        splash_pix = QPixmap(icon_path)
        # Scale splash screen to a reasonable size (400x400)
        scaled_splash = splash_pix.scaled(ICON_SPLASH_SIZE, ICON_SPLASH_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        circular_splash = make_circular_pixmap(scaled_splash)
        splash = QSplashScreen(circular_splash, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()

        # Create main window
        window = MediaDownloaderApp()

        # Close splash and show window after a short delay
        QTimer.singleShot(1500, splash.close)
        QTimer.singleShot(1500, window.show)
    else:
        # No splash screen, just show window
        window = MediaDownloaderApp()
        window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
