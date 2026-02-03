#!/usr/bin/env python3
"""
AV Morning Star - Media Downloader
A PyQt5 application for downloading videos and audio from URLs
"""

import sys
import os
import json

# Suppress Qt Wayland warnings
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.wayland=false'

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QListWidget, QComboBox, QProgressBar, QTextEdit,
                             QCheckBox, QScrollArea, QGroupBox, QMessageBox,
                             QFileDialog, QListWidgetItem, QSplashScreen)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush, QPainterPath
import yt_dlp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


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
    """Thread for scraping video URLs from a page"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            # First, try to get playlist/channel info using yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info and 'entries' in info:
                    # This is a playlist/channel
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            # Try multiple fields for uploader
                            uploader = (entry.get('uploader') or 
                                      entry.get('channel') or 
                                      entry.get('uploader_id') or 
                                      entry.get('creator') or 
                                      'Unknown')
                            
                            videos.append({
                                'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'title': entry.get('title', 'Unknown Title'),
                                'duration': entry.get('duration', 0),
                                'uploader': uploader
                            })
                    self.finished.emit(videos)
                else:
                    # Single video
                    uploader = (info.get('uploader') or 
                              info.get('channel') or 
                              info.get('uploader_id') or 
                              info.get('creator') or 
                              'Unknown')
                    
                    videos = [{
                        'url': self.url,
                        'title': info.get('title', 'Unknown Title'),
                        'duration': info.get('duration', 0),
                        'uploader': uploader
                    }]
                    self.finished.emit(videos)
                    
        except Exception as e:
            self.error.emit(f"Error scraping URL: {str(e)}")


class DownloadThread(QThread):
    """Thread for downloading videos/audio"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, urls, output_path, format_type, video_quality=None, 
                 audio_codec='mp3', audio_quality='192', download_subs=False,
                 embed_thumbnail=False, normalize_audio=False, denoise_audio=False,
                 dynamic_normalization=False):
        super().__init__()
        self.urls = urls
        self.output_path = output_path
        self.format_type = format_type
        self.video_quality = video_quality
        self.audio_codec = audio_codec
        self.audio_quality = audio_quality
        self.download_subs = download_subs
        self.embed_thumbnail = embed_thumbnail
        self.normalize_audio = normalize_audio
        self.denoise_audio = denoise_audio
        self.dynamic_normalization = dynamic_normalization
        
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
                # Build custom filename template
                filename_template = self.parent().build_filename_template() if hasattr(self, 'parent') else '%(title)s.%(ext)s'
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.output_path, filename_template),
                    'progress_hooks': [self.progress_hook],
                    'noprogress': False,  # Ensure progress updates are sent
                    'quiet': False,  # Allow progress output
                    'no_warnings': False,
                    'retries': 3,
                    'fragment_retries': 3,
                    'socket_timeout': 30,
                }
                
                # Subtitle options
                if self.download_subs:
                    ydl_opts['writesubtitles'] = True
                    ydl_opts['writeautomaticsub'] = True
                    ydl_opts['subtitleslangs'] = ['en', 'en-US']
                    if self.format_type == 'video':
                        ydl_opts['embedsubtitles'] = True
                
                if self.format_type == 'audio':
                    # Audio extraction with configurable codec and quality
                    postprocessors = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_codec,
                        'preferredquality': self.audio_quality,
                    }]
                    
                    # Build audio filter chain
                    audio_filters = []
                    
                    # Add denoising if requested (FFT-based noise reduction)
                    if self.denoise_audio:
                        audio_filters.append('afftdn=nf=-20')
                    
                    # Add normalization if requested
                    if self.normalize_audio:
                        if self.dynamic_normalization:
                            # Dynamic audio normalization - excellent for varying volumes
                            audio_filters.append('dynaudnorm=p=0.95:m=10:s=12:g=5')
                        else:
                            # EBU R128 loudness normalization (two-pass)
                            audio_filters.append('loudnorm=I=-16:LRA=11:TP=-1.5')
                    
                    # Apply audio filters if any
                    if audio_filters:
                        ydl_opts['postprocessor_args'] = {
                            'ffmpeg': ['-af', ','.join(audio_filters)]
                        }
                    
                    # Add thumbnail embedding if requested
                    if self.embed_thumbnail:
                        postprocessors.append({
                            'key': 'EmbedThumbnail',
                        })
                        ydl_opts['writethumbnail'] = True
                    
                    # Add metadata
                    postprocessors.append({
                        'key': 'FFmpegMetadata',
                    })
                    
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': postprocessors,
                    })
                else:  # video
                    # Parse video quality from UI text
                    quality_text = self.video_quality.lower()
                    if 'best' in quality_text:
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    elif '2160' in quality_text or '4k' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
                    elif '1440' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'
                    elif '1080' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                    elif '720' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    elif '480' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
                    elif '360' in quality_text:
                        ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                    else:
                        ydl_opts['format'] = 'best'
                        
                    ydl_opts['merge_output_format'] = 'mp4'
                
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


class MediaDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.videos_list = []
        self.checkboxes = []
        self.output_path = os.path.expanduser("~/Downloads")
        self.mode = 'basic'  # Default to basic mode
        self.filename_template = ['title', 'quality', 'uploader']  # Default template
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AV Morning Star - Media Downloader")
        self.setMinimumSize(800, 850)
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), 'av-morning-star.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Banner with icon
        banner_layout = QHBoxLayout()
        
        # Icon in banner
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            circular_pixmap = make_circular_pixmap(scaled_pixmap)
            icon_label.setPixmap(circular_pixmap)
            banner_layout.addWidget(icon_label)
        
        # Title section
        title_layout = QVBoxLayout()
        title = QLabel("AV Morning Star")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Video & Audio Downloader")
        subtitle.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(subtitle)
        
        banner_layout.addLayout(title_layout)
        banner_layout.addStretch()
        
        main_layout.addLayout(banner_layout)
        
        # URL Input Section
        url_group = QGroupBox("Enter URL")
        url_layout = QVBoxLayout()
        
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video URL or channel/playlist URL...")
        self.url_input.returnPressed.connect(self.fetch_videos)
        url_input_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.clicked.connect(self.fetch_videos)
        url_input_layout.addWidget(self.fetch_btn)
        
        url_layout.addLayout(url_input_layout)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # Create horizontal layout for Videos List and Filename Template
        content_row = QHBoxLayout()
        
        # Videos List Section (LEFT SIDE)
        videos_group = QGroupBox("Available Videos/Audio")
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
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setEnabled(False)
        select_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none)
        self.select_none_btn.setEnabled(False)
        select_layout.addWidget(self.select_none_btn)
        
        videos_layout.addLayout(select_layout)
        videos_group.setLayout(videos_layout)
        content_row.addWidget(videos_group, 2)  # Stretch factor 2 - larger
        
        # Filename Template Section (RIGHT SIDE)
        filename_group = QGroupBox("Filename Template")
        filename_layout = QVBoxLayout()
        
        # Selected tags container (top section)
        selected_label = QLabel("Selected Tags (drag to reorder, click × to remove):")
        filename_layout.addWidget(selected_label)
        
        # Frame for selected tags
        selected_frame = QWidget()
        selected_frame.setMinimumHeight(60)
        selected_frame.setMaximumHeight(80)
        selected_frame.setStyleSheet("QWidget { background-color: #2d2d2d; border: 2px solid #444; border-radius: 5px; padding: 5px; }")
        self.selected_tags_layout = QHBoxLayout(selected_frame)
        self.selected_tags_layout.setSpacing(10)
        self.selected_tags_layout.setAlignment(Qt.AlignLeft)
        filename_layout.addWidget(selected_frame)
        
        filename_layout.addSpacing(10)
        
        # Available tags container (bottom section)
        available_label = QLabel("Available Tags (click to add):")
        filename_layout.addWidget(available_label)
        
        # Frame for available tags
        available_frame = QWidget()
        available_frame.setMinimumHeight(60)
        available_frame.setMaximumHeight(80)
        available_frame.setStyleSheet("QWidget { background-color: #2d2d2d; border: 2px solid #444; border-radius: 5px; padding: 5px; }")
        self.available_tags_layout = QHBoxLayout(available_frame)
        self.available_tags_layout.setSpacing(10)
        self.available_tags_layout.setAlignment(Qt.AlignLeft)
        filename_layout.addWidget(available_frame)
        
        filename_layout.addSpacing(10)
        
        # Preview
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.filename_preview = QLabel("")
        self.filename_preview.setStyleSheet("QLabel { font-family: monospace; color: #00ff00; font-weight: bold; }")
        preview_layout.addWidget(self.filename_preview)
        preview_layout.addStretch()
        filename_layout.addLayout(preview_layout)
        
        filename_group.setLayout(filename_layout)
        filename_group.setMaximumWidth(450)  # Compact width
        content_row.addWidget(filename_group)  # No stretch - fixed size
        
        # Add the horizontal row to main layout
        main_layout.addLayout(content_row)
        
        # Initialize filename tags
        self.init_filename_tags()
        
        # Download Options Section
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()
        
        # Mode selection row (Basic/Advanced)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Basic (Auto-detect best quality)", "Advanced (Manual settings)"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        options_layout.addLayout(mode_layout)
        
        # Format selection row
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video", "Audio Only"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Quality settings in columns (Video | Audio Codec | Audio Quality)
        quality_columns = QHBoxLayout()
        quality_columns.setSpacing(15)
        
        # Column 1: Video Quality
        video_col = QVBoxLayout()
        video_col.addWidget(QLabel("Video Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "4K (2160p)", "1440p", "1080p", "720p", "480p", "360p"])
        video_col.addWidget(self.quality_combo)
        quality_columns.addLayout(video_col)
        
        # Column 2: Audio Codec
        codec_col = QVBoxLayout()
        codec_col.addWidget(QLabel("Audio Codec:"))
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["MP3", "AAC", "FLAC", "Opus", "M4A"])
        codec_col.addWidget(self.audio_codec_combo)
        quality_columns.addLayout(codec_col)
        
        # Column 3: Audio Quality
        audio_qual_col = QVBoxLayout()
        audio_qual_col.addWidget(QLabel("Audio Quality:"))
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"])
        self.audio_quality_combo.setCurrentIndex(2)  # Default to 192 kbps
        audio_qual_col.addWidget(self.audio_quality_combo)
        quality_columns.addLayout(audio_qual_col)
        
        options_layout.addLayout(quality_columns)
        options_layout.addSpacing(10)
        
        # Advanced options checkboxes in rows
        advanced_row1 = QHBoxLayout()
        advanced_row1.setSpacing(20)
        self.subtitles_checkbox = QCheckBox("Download Subtitles")
        self.subtitles_checkbox.setChecked(False)
        advanced_row1.addWidget(self.subtitles_checkbox)
        
        self.embed_thumbnail_checkbox = QCheckBox("Embed Thumbnail (Audio)")
        self.embed_thumbnail_checkbox.setChecked(True)
        advanced_row1.addWidget(self.embed_thumbnail_checkbox)
        advanced_row1.addStretch()
        options_layout.addLayout(advanced_row1)
        options_layout.addSpacing(8)
        
        # Audio enhancement options row
        advanced_row2 = QHBoxLayout()
        advanced_row2.setSpacing(20)
        
        self.normalize_audio_checkbox = QCheckBox("Normalize Audio (EBU R128)")
        self.normalize_audio_checkbox.setChecked(False)
        self.normalize_audio_checkbox.setToolTip("Professional loudness normalization to -16 LUFS")
        advanced_row2.addWidget(self.normalize_audio_checkbox)
        
        self.dynamic_norm_checkbox = QCheckBox("Dynamic Normalization")
        self.dynamic_norm_checkbox.setChecked(False)
        self.dynamic_norm_checkbox.setToolTip("Better for varying volume levels (alternative to EBU R128)")
        advanced_row2.addWidget(self.dynamic_norm_checkbox)
        
        self.denoise_checkbox = QCheckBox("Denoise Audio")
        self.denoise_checkbox.setChecked(False)
        self.denoise_checkbox.setToolTip("Remove background noise using FFT-based filtering")
        advanced_row2.addWidget(self.denoise_checkbox)
        
        advanced_row2.addStretch()
        options_layout.addLayout(advanced_row2)
        
        # Output path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save to:"))
        self.path_label = QLabel(self.output_path)
        path_layout.addWidget(self.path_label)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.browse_btn)
        
        options_layout.addLayout(path_layout)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Store advanced option widgets for show/hide
        self.advanced_widgets = [
            self.quality_combo, self.audio_codec_combo, self.audio_quality_combo,
            self.embed_thumbnail_checkbox, self.normalize_audio_checkbox,
            self.dynamic_norm_checkbox, self.denoise_checkbox
        ]
        self.advanced_labels = []
        
        # Set initial mode to Basic (hide advanced options)
        self.on_mode_changed("Basic (Auto-detect best quality)")
        
        # Download Button
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        main_layout.addWidget(self.download_btn)
        
        # Progress Section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        self.statusBar().showMessage("Ready")
        
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
            # Selected tag with X button
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)
            
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
                    background-color: #3a8eef;
                }
            """)
            btn.setFixedHeight(26)
            btn.setCursor(Qt.PointingHandCursor)
            
            # X button
            x_btn = QPushButton("×")
            x_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 2px;
                    font-weight: bold;
                    font-size: 14px;
                    max-width: 20px;
                    max-height: 20px;
                }
                QPushButton:hover {
                    background-color: #ff0000;
                }
            """)
            x_btn.setFixedSize(20, 20)
            x_btn.setCursor(Qt.PointingHandCursor)
            x_btn.clicked.connect(lambda checked, t=tag: self.remove_tag_visual(t))
            
            layout.addWidget(btn)
            layout.addWidget(x_btn)
            
            # Store reference
            container.tag = tag
            return container
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
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tag: self.add_tag_visual(t))
            btn.tag = tag
            return btn
    
    def refresh_tag_buttons(self):
        """Refresh all tag button displays"""
        # Clear existing buttons
        while self.selected_tags_layout.count():
            item = self.selected_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.available_tags_layout.count():
            item = self.available_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.selected_tag_buttons.clear()
        self.available_tag_buttons.clear()
        
        # Create selected tag buttons
        for tag in self.filename_template:
            if tag in self.all_tags:
                btn = self.create_tag_button(tag, is_selected=True)
                self.selected_tags_layout.addWidget(btn)
                self.selected_tag_buttons.append(btn)
        
        # Add stretch to push buttons to left
        self.selected_tags_layout.addStretch()
        
        # Create available tag buttons
        for tag in self.all_tags:
            if tag not in self.filename_template:
                btn = self.create_tag_button(tag, is_selected=False)
                self.available_tags_layout.addWidget(btn)
                self.available_tag_buttons.append(btn)
        
        # Add stretch to push buttons to left
        self.available_tags_layout.addStretch()
    
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
            # Hide advanced options
            self.quality_combo.setVisible(False)
            self.audio_codec_combo.setVisible(False)
            self.audio_quality_combo.setVisible(False)
            self.embed_thumbnail_checkbox.setVisible(False)
            self.normalize_audio_checkbox.setVisible(False)
            self.dynamic_norm_checkbox.setVisible(False)
            self.denoise_checkbox.setVisible(False)
            # Hide the labels in the quality columns layout
            quality_layout = self.quality_combo.parent().layout()
            for i in range(quality_layout.count()):
                item = quality_layout.itemAt(i)
                if item and item.layout():
                    for j in range(item.layout().count()):
                        widget = item.layout().itemAt(j).widget()
                        if widget and isinstance(widget, QLabel):
                            widget.setVisible(False)
        else:
            self.mode = 'advanced'
            # Show advanced options
            self.quality_combo.setVisible(True)
            self.audio_codec_combo.setVisible(True)
            self.audio_quality_combo.setVisible(True)
            self.embed_thumbnail_checkbox.setVisible(True)
            self.normalize_audio_checkbox.setVisible(True)
            self.dynamic_norm_checkbox.setVisible(True)
            self.denoise_checkbox.setVisible(True)
            # Show labels
            quality_layout = self.quality_combo.parent().layout()
            for i in range(quality_layout.count()):
                item = quality_layout.itemAt(i)
                if item and item.layout():
                    for j in range(item.layout().count()):
                        widget = item.layout().itemAt(j).widget()
                        if widget and isinstance(widget, QLabel):
                            widget.setVisible(True)
            # Re-apply format-based enabling
            self.on_format_changed(self.format_combo.currentText())
    
    def on_format_changed(self, text):
        """Enable/disable quality selection based on format"""
        # Only apply these rules in Advanced mode
        if self.mode == 'advanced':
            if text == "Audio Only":
                self.quality_combo.setEnabled(False)
                self.audio_codec_combo.setEnabled(True)
                self.audio_quality_combo.setEnabled(True)
                self.embed_thumbnail_checkbox.setEnabled(True)
                self.normalize_audio_checkbox.setEnabled(True)
                self.dynamic_norm_checkbox.setEnabled(True)
                self.denoise_checkbox.setEnabled(True)
            else:
                self.quality_combo.setEnabled(True)
                self.audio_codec_combo.setEnabled(False)
                self.audio_quality_combo.setEnabled(False)
                self.embed_thumbnail_checkbox.setEnabled(False)
                self.normalize_audio_checkbox.setEnabled(False)
                self.dynamic_norm_checkbox.setEnabled(False)
                self.denoise_checkbox.setEnabled(False)
            
    def browse_output_path(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_path)
        if path:
            self.output_path = path
            self.path_label.setText(path)
            
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
            
        self.status_label.setText("Fetching video information...")
        self.statusBar().showMessage("Connecting to URL...")
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        
        # Clear previous results
        self.clear_videos_list()
        
        # Start scraping thread
        self.scraper_thread = URLScraperThread(url)
        self.scraper_thread.finished.connect(self.on_videos_fetched)
        self.scraper_thread.error.connect(self.on_fetch_error)
        self.scraper_thread.start()
        
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
        
    def on_fetch_error(self, error):
        """Handle fetch error"""
        self.fetch_btn.setEnabled(True)
        self.status_label.setText("Error fetching videos")
        self.statusBar().showMessage("Failed to fetch videos")
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
            audio_codec = 'mp3'  # Most compatible
            audio_quality = '320'  # Highest quality
            download_subs = False
            embed_thumbnail = True if format_type == 'audio' else False  # Always embed for audio
            normalize_audio = True if format_type == 'audio' else False  # Auto-normalize audio
            dynamic_normalization = False  # Use standard EBU R128
            denoise_audio = False  # Don't denoise by default
        else:
            # Advanced mode - use manual settings
            video_quality = self.quality_combo.currentText() if format_type == 'video' else None
            audio_codec = self.audio_codec_combo.currentText().lower()
            audio_quality = self.audio_quality_combo.currentText().split()[0]  # Extract number from "192 kbps"
            download_subs = self.subtitles_checkbox.isChecked()
            embed_thumbnail = self.embed_thumbnail_checkbox.isChecked() if format_type == 'audio' else False
            normalize_audio = self.normalize_audio_checkbox.isChecked() if format_type == 'audio' else False
            dynamic_normalization = self.dynamic_norm_checkbox.isChecked() if format_type == 'audio' else False
            denoise_audio = self.denoise_checkbox.isChecked() if format_type == 'audio' else False
        
        self.status_label.setText(f"Starting download of {len(selected_urls)} item(s)...")
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Start download thread
        self.download_thread = DownloadThread(
            selected_urls, self.output_path, format_type, video_quality,
            audio_codec, audio_quality, download_subs, embed_thumbnail, normalize_audio,
            denoise_audio, dynamic_normalization
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


def main():
    app = QApplication(sys.argv)
    
    # Show splash screen if icon exists
    icon_path = os.path.join(os.path.dirname(__file__), 'av-morning-star.png')
    if os.path.exists(icon_path):
        splash_pix = QPixmap(icon_path)
        # Scale splash screen to a reasonable size (400x400)
        scaled_splash = splash_pix.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
