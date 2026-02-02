#!/usr/bin/env python3
"""
AV Morning Star - Media Downloader
A PyQt5 application for downloading videos and audio from URLs
"""

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QListWidget, QComboBox, QProgressBar, QTextEdit,
                             QCheckBox, QScrollArea, QGroupBox, QMessageBox,
                             QFileDialog, QListWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont
import yt_dlp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


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
                            videos.append({
                                'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'title': entry.get('title', 'Unknown Title'),
                                'duration': entry.get('duration', 0),
                                'uploader': entry.get('uploader', 'Unknown')
                            })
                    self.finished.emit(videos)
                else:
                    # Single video
                    videos = [{
                        'url': self.url,
                        'title': info.get('title', 'Unknown Title'),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', 'Unknown')
                    }]
                    self.finished.emit(videos)
                    
        except Exception as e:
            self.error.emit(f"Error scraping URL: {str(e)}")


class DownloadThread(QThread):
    """Thread for downloading videos/audio"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, urls, output_path, format_type, video_quality=None):
        super().__init__()
        self.urls = urls
        self.output_path = output_path
        self.format_type = format_type
        self.video_quality = video_quality
        
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
                ydl_opts = {
                    'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'noprogress': False,  # Ensure progress updates are sent
                    'quiet': False,  # Allow progress output
                    'no_warnings': False,
                    'retries': 3,
                    'fragment_retries': 3,
                    'socket_timeout': 30,
                }
                
                if self.format_type == 'audio':
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })
                else:  # video
                    if self.video_quality == 'best':
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    elif self.video_quality == '1080p':
                        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                    elif self.video_quality == '720p':
                        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    elif self.video_quality == '480p':
                        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
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
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AV Morning Star - Media Downloader")
        self.setMinimumSize(800, 600)
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), 'av-morning-star.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("AV Morning Star")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Video & Audio Downloader")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
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
        
        # Videos List Section
        videos_group = QGroupBox("Available Videos/Audio")
        videos_layout = QVBoxLayout()
        
        # Scroll area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        
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
        main_layout.addWidget(videos_group)
        
        # Download Options Section
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video", "Audio Only"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        # Quality selection
        format_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "1080p", "720p", "480p"])
        format_layout.addWidget(self.quality_combo)
        
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
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
        
    def on_format_changed(self, text):
        """Enable/disable quality selection based on format"""
        if text == "Audio Only":
            self.quality_combo.setEnabled(False)
        else:
            self.quality_combo.setEnabled(True)
            
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
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
            
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
            
        # Determine format and quality
        format_type = 'audio' if self.format_combo.currentText() == "Audio Only" else 'video'
        quality = self.quality_combo.currentText().lower() if format_type == 'video' else None
        
        self.status_label.setText(f"Starting download of {len(selected_urls)} item(s)...")
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Start download thread
        self.download_thread = DownloadThread(selected_urls, self.output_path, format_type, quality)
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
    window = MediaDownloaderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
