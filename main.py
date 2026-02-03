#!/usr/bin/env python3
"""
AV Morning Star - Media Downloader
A PyQt5 application for downloading videos and audio from URLs
"""

import sys
import os
import json

# Import application constants
from constants import *

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
                             QFileDialog, QSplashScreen, QGridLayout,
                             QDialog)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QPainterPath
import yt_dlp

# Import our modular extractors
from extractors import get_extractor

# Import browser detection utilities
from browser_utils import detect_available_browsers, get_browsers_with_youtube_cookies, get_default_browser


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


class URLScraperThread(QThread):
    """Thread for scraping video URLs from a page using platform-specific extractors"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, url, cookies_from_browser=None):
        super().__init__()
        self.url = url
        self.cookies_from_browser = cookies_from_browser
        
    def run(self):
        try:
            # Get the appropriate extractor for this URL with browser cookies
            extractor = get_extractor(
                self.url, 
                cookies_from_browser=self.cookies_from_browser
            )
            
            # Extract video information
            videos = extractor.extract_info()
            self.finished.emit(videos)
                    
        except Exception as e:
            self.error.emit(f"Error scraping URL: {str(e)}")


class DownloadThread(QThread):
    """Thread for downloading videos/audio using platform-specific extractors"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, urls, output_path, format_type, video_quality=None, 
                 audio_codec='mp3', audio_quality='192', download_subs=False,
                 embed_thumbnail=False, normalize_audio=False, denoise_audio=False,
                 dynamic_normalization=False, filename_template=None, cookies_from_browser=None,
                 video_container='mp4', denoise_video=False, stabilize_video=False, 
                 sharpen_video=False, normalize_video_audio=False, denoise_video_audio=False):
        super().__init__()
        self.urls = urls
        self.output_path = output_path
        self.format_type = format_type
        self.video_quality = video_quality
        self.video_container = video_container
        self.audio_codec = audio_codec
        self.audio_quality = audio_quality
        self.download_subs = download_subs
        self.embed_thumbnail = embed_thumbnail
        self.normalize_audio = normalize_audio
        self.denoise_audio = denoise_audio
        self.dynamic_normalization = dynamic_normalization
        self.filename_template = filename_template or '%(title)s.%(ext)s'
        self.cookies_from_browser = cookies_from_browser
        # Video enhancement options
        self.denoise_video = denoise_video
        self.stabilize_video = stabilize_video
        self.sharpen_video = sharpen_video
        self.normalize_video_audio = normalize_video_audio
        self.denoise_video_audio = denoise_video_audio
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Try to get percentage from different possible keys
            percent = 0
            
            # Method 1: Check for _percent_str
            if '_percent_str' in d:
                try:
                    percent_str = d['_percent_str'].strip().replace('%', '')
                    percent = float(percent_str)
                except (ValueError, AttributeError):
                    pass
            
            # Method 2: Calculate from downloaded/total bytes
            if percent == 0 and 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
                try:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                except (ZeroDivisionError, TypeError):
                    pass
            
            # Method 3: Use estimated total bytes
            if percent == 0 and 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                try:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                except (ZeroDivisionError, TypeError):
                    pass
            
            # Get filename
            filename = d.get('filename', d.get('_filename', 'Downloading...'))
            if filename and len(filename) > 50:
                filename = '...' + filename[-47:]
            
            # Emit progress update
            self.progress.emit(filename, max(0, min(100, int(percent))))
            
        elif d['status'] == 'finished':
            self.progress.emit('Post-processing...', 100)
            
    def run(self):
        successful = 0
        failed = 0
        failed_urls = []
        
        for idx, url in enumerate(self.urls, 1):
            try:
                # Get selected browser for authentication (passed from main window)
                # For downloads, we'll use the same browser that was used for fetching
                # This could be enhanced to store the browser choice per URL
                
                # Get platform-specific extractor with browser cookies
                extractor = get_extractor(url, cookies_from_browser=self.cookies_from_browser)
                
                # Get platform-specific download options
                ydl_opts = extractor.get_download_opts(
                    self.output_path,
                    self.filename_template,
                    self.format_type,
                    self.video_quality,
                    self.audio_codec,
                    self.audio_quality,
                    self.download_subs,
                    self.embed_thumbnail,
                    self.normalize_audio,
                    self.denoise_audio,
                    self.dynamic_normalization,
                    self.video_container,
                    self.denoise_video,
                    self.stabilize_video,
                    self.sharpen_video,
                    self.normalize_video_audio,
                    self.denoise_video_audio
                )
                
                # Add progress hook
                ydl_opts['progress_hooks'] = [self.progress_hook]
                
                self.progress.emit(f'Downloading {idx}/{len(self.urls)}...', 0)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                successful += 1
                    
            except Exception as e:
                failed += 1
                failed_urls.append((url, str(e)))
                # Continue with next download instead of stopping
                self.progress.emit(f'Failed {idx}/{len(self.urls)}, continuing...', 0)
                continue
        
        # Generate summary message
        if failed == 0:
            self.finished.emit(f"All {successful} downloads completed successfully!")
        elif successful == 0:
            error_msg = f"All {failed} downloads failed.\n\nErrors:\n"
            for url, err in failed_urls[:3]:  # Show first 3 errors
                error_msg += f"- {err[:100]}...\n"
            self.error.emit(error_msg)
        else:
            message = f"Completed with mixed results:\n✓ {successful} succeeded\n✗ {failed} failed"
            if failed_urls:
                message += f"\n\nFirst error: {failed_urls[0][1][:150]}"
            self.finished.emit(message)


class PreferencesDialog(QDialog):
    """Preferences dialog for application settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(PREFERENCES_WINDOW_TITLE)
        self.setMinimumSize(PREFERENCES_WINDOW_MIN_WIDTH, PREFERENCES_WINDOW_MIN_HEIGHT)
        self.setModal(True)
        
        # Get parent's current settings
        self.parent_app = parent
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Preferences")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Authentication section
        auth_group = QGroupBox(GROUP_AUTHENTICATION)
        auth_layout = QVBoxLayout()
        
        # Main description
        main_desc = QLabel(
            "To download YouTube videos, AV Morning Star can use your browser's login session.\n"
            "Simply select the browser where you're logged into YouTube."
        )
        main_desc.setWordWrap(True)
        main_desc.setStyleSheet("QLabel { font-size: 10pt; margin-bottom: 15px; }")
        auth_layout.addWidget(main_desc)
        
        # Browser selector
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Authentication:"))
        
        self.browser_combo = QComboBox()
        self.browser_combo.addItems([
            "Auto (Recommended)",
            "None (No authentication)",
            "Firefox",
            "Chrome",
            "Brave",
            "Edge",
            "Chromium",
            "Opera",
            "Vivaldi"
        ])
        self.browser_combo.setToolTip("Auto mode automatically finds the best browser with YouTube login")
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addStretch()
        
        auth_layout.addLayout(browser_layout)
        
        # Instructions
        instructions = QLabel(
            "<b>Important:</b> Make sure you're logged into YouTube in the selected browser before downloading."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #ff8800; font-size: 9pt; margin-top: 10px; background-color: #2a2a2a; padding: 8px; border-radius: 4px; }")
        auth_layout.addWidget(instructions)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(BTN_CANCEL)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(BTN_SAVE)
        save_btn.clicked.connect(self.save_preferences)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Load current settings
        if parent:
            current_browser = getattr(parent, 'browser_preference', 'auto')
            browser_map = {
                'auto': 0,
                'none': 1,
                'firefox': 2,
                'chrome': 3,
                'brave': 4,
                'edge': 5,
                'chromium': 6,
                'opera': 7,
                'vivaldi': 8
            }
            self.browser_combo.setCurrentIndex(browser_map.get(current_browser, 0))
    
    def save_preferences(self):
        """Save preferences and close dialog"""
        if self.parent_app:
            browser_text = self.browser_combo.currentText()
            if "Auto" in browser_text:
                self.parent_app.browser_preference = 'auto'
            elif "None" in browser_text:
                self.parent_app.browser_preference = 'none'
            else:
                # Extract browser name (e.g., "Firefox" -> "firefox")
                self.parent_app.browser_preference = browser_text.lower()
        self.close()


class MediaDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.videos_list = []
        self.checkboxes = []
        self.output_path = os.path.expanduser(DEFAULT_OUTPUT_DIR)
        self.mode = MODE_BASIC  # Default to basic mode
        self.filename_template = DEFAULT_FILENAME_TAGS.copy()  # Default template
        
        # Default to Auto mode (will detect best browser at runtime)
        self.browser_preference = DEFAULT_BROWSER_PREFERENCE
        
        # Track if we've tried cookieless and it failed
        self.cookieless_failed = False
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), ICON_FILENAME)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create menu bar
        menubar = self.menuBar()
        
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
        selected_frame.setStyleSheet("QWidget { background-color: #2d2d2d; border: 2px solid #444; border-radius: 5px; padding: 5px; }")
        selected_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.selected_tags_layout = FlowLayout(selected_frame)
        self.selected_tags_layout.setSpacing(10)
        filename_layout.addWidget(selected_frame)
        
        filename_layout.addSpacing(10)
        
        # Available tags container (bottom section)
        available_label = QLabel("Available Tags (click to add):")
        filename_layout.addWidget(available_label)
        
        # Frame for available tags with wrapping
        available_frame = QWidget()
        available_frame.setStyleSheet("QWidget { background-color: #2d2d2d; border: 2px solid #444; border-radius: 5px; padding: 5px; }")
        available_frame.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Minimum)
        self.available_tags_layout = FlowLayout(available_frame)
        self.available_tags_layout.setSpacing(10)
        filename_layout.addWidget(available_frame)
        
        filename_layout.addSpacing(10)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.filename_preview = QLabel("")
        self.filename_preview.setStyleSheet("QLabel { font-family: monospace; color: #00ff00; font-weight: bold; }")
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
            "Reduce camera shake using deshake filter.\n"
            "Uses 32px search range with edge mirroring.\n"
            "Best for: handheld footage, action cameras\n"
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
            'download_date': 'Download Date',
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
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #ff4444;
                }
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
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    color: white;
                    border: 2px solid #777;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #666;
                    border-color: #4a9eff;
                }
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
            'download_date': '20260202',
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
        
        # Join with separator and add extension
        if parts:
            return ' - '.join(parts)
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
        
        # Smart cookie detection strategy:
        # 1. For YouTube URLs: Try cookieless first (unless we know it failed before)
        # 2. If cookieless fails with bot detection, auto-retry with best browser
        # 3. For non-YouTube URLs: Use cookies if available
        
        cookies_from_browser = None
        is_youtube = 'youtube.com' in url.lower() or 'youtu.be' in url.lower()
        
        # Resolve 'auto' preference to actual browser
        resolved_browser = None
        if self.browser_preference == 'auto':
            resolved_browser = get_default_browser()
        elif self.browser_preference != 'none':
            resolved_browser = self.browser_preference
        
        if is_youtube:
            # YouTube: Try cookieless first unless we've already failed
            if self.cookieless_failed or resolved_browser:
                # Either we know cookieless doesn't work, or user has set a browser preference
                if resolved_browser:
                    cookies_from_browser = resolved_browser
                    browser_display = resolved_browser.title()
                    if self.browser_preference == 'auto':
                        self.status_label.setText(f"Auto-detected {browser_display}, fetching...")
                    else:
                        self.status_label.setText(f"Fetching with {browser_display} authentication...")
                else:
                    self.status_label.setText("Fetching (no authentication)...")
            else:
                # First attempt: try without cookies
                self.status_label.setText("Fetching video information (no authentication)...")
        else:
            # Non-YouTube: Use cookies if we have a browser set
            if resolved_browser:
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
        self.scraper_thread.finished.connect(self.on_videos_fetched)
        self.scraper_thread.error.connect(self.on_fetch_error)
        self.scraper_thread.start()
    
    def browse_output_path(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.output_path)
        if directory:
            self.output_path = directory
            self.path_label.setText(self.output_path)
        
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
            
            checkbox_text = f"{video['title']}\n   Uploader: {video.get('uploader', 'Unknown')} | Duration: {duration_str}"
            checkbox = QCheckBox(checkbox_text)
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
            for browser in ['firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera', 'vivaldi', 'safari']:
                if browser in error_lower:
                    browser_display = browser.title()
                    
                    # Get available browsers
                    available = detect_available_browsers()
                    
                    if available:
                        msg = (
                            f"❌ {browser_display} cookies not found\n\n"
                            f"The selected browser ({browser_display}) doesn't appear to be installed "
                            f"or doesn't have cookies on this system.\n\n"
                            f"Available browsers with YouTube login:\n"
                        )
                        
                        # List browsers with YouTube cookies
                        yt_browsers = get_browsers_with_youtube_cookies()
                        if yt_browsers:
                            for b in yt_browsers:
                                msg += f"  ✓ {b.title()}\n"
                            msg += f"\n💡 Recommendation: Set authentication to 'Auto (Recommended)' "
                            msg += f"in Tools > Preferences, and I'll automatically use {yt_browsers[0].title()}."
                        else:
                            msg += f"  (None detected with YouTube login)\n\n"
                            msg += f"💡 Recommendation: Sign into YouTube in one of your browsers, "
                            msg += f"then use 'Auto (Recommended)' mode."
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
        is_bot_error = ('bot' in error.lower() or 'sign in to confirm' in error.lower() or 
                       'requested format is not available' in error.lower())
        
        url = self.url_input.text().strip()
        is_youtube = 'youtube.com' in url.lower() or 'youtu.be' in url.lower()
        
        # If YouTube bot detection and we haven't tried cookies yet
        if is_youtube and is_bot_error and not self.cookieless_failed:
            self.cookieless_failed = True
            
            # Try to find a browser with YouTube cookies
            browsers_with_youtube = get_browsers_with_youtube_cookies()
            
            if browsers_with_youtube:
                # Auto-retry with detected browser
                browser = browsers_with_youtube[0]
                self.browser_preference = browser
                
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
                    self.status_label.setText(f"Retrying with {browser} authentication...")
                    self.fetch_videos()  # Retry automatically
                    return
                else:
                    # User declined, show error
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
        
        # Not a bot error, or already tried cookies - show error
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
            normalize_audio = True if format_type == 'audio' else False  # Auto-normalize audio
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
            audio_codec = self.audio_codec_combo.currentText().lower().replace(' vorbis', '').replace(' ', '')  # Clean codec name
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
        
        # Resolve 'auto' browser preference to actual browser name
        resolved_browser = None
        if self.browser_preference == 'auto':
            resolved_browser = get_default_browser()
        elif self.browser_preference != 'none':
            resolved_browser = self.browser_preference
        
        # Start download thread with browser cookies
        self.download_thread = DownloadThread(
            selected_urls, self.output_path, format_type, video_quality,
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


def main():
    # Set WM_CLASS before creating QApplication (critical for KDE/Wayland)
    os.environ['RESOURCE_NAME'] = 'av-morning-star'
    
    app = QApplication(sys.argv)
    
    # Set application name and icon for desktop environments
    app.setApplicationName("av-morning-star")
    app.setApplicationDisplayName(APP_FULL_TITLE)
    app.setDesktopFileName("av-morning-star.desktop")
    
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
