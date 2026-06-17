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



class DownloadHandlersMixin:
    """Behaviour mixed into MediaDownloaderApp."""

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
