"""Download start/progress/error handlers."""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from threads import DownloadThread

from .download_settings import collect_download_settings, resolve_output_path, validate_output_path


def _plain_message(parent, icon, title, message):
    """Show a QMessageBox with *message* forced to PlainText rendering.

    Prevents Qt AutoText from silently promoting strings that contain angle
    brackets (common in yt-dlp error output) to RichText.
    """
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setIcon(icon)
    box.setTextFormat(Qt.PlainText)
    box.setText(message)
    box.exec_()


class DownloadHandlersMixin:
    """Start downloads and handle progress callbacks."""

    def start_download(self):
        selected_urls = [
            self.videos_list[i]['url']
            for i, checkbox in enumerate(self.checkboxes)
            if checkbox.isChecked()
        ]
        if not selected_urls:
            QMessageBox.warning(self, "Error", "Please select at least one video to download")
            return

        format_type = 'audio' if self.format_combo.currentText() == "Audio Only" else 'video'
        settings = collect_download_settings(self, format_type)

        self.status_label.setText(f"Starting download of {len(selected_urls)} item(s)...")
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        output_path = resolve_output_path(self.output_path)
        if not validate_output_path(self, output_path):
            self.download_btn.setEnabled(True)
            self.fetch_btn.setEnabled(True)
            self.status_label.setText("Invalid output directory")
            return

        resolved_browser = getattr(self, '_fetch_cookies_used', None)
        self.download_thread = DownloadThread(
            selected_urls,
            output_path,
            format_type,
            settings['video_quality'],
            settings['audio_codec'],
            settings['audio_quality'],
            settings['download_subs'],
            settings['embed_thumbnail'],
            settings['normalize_audio'],
            settings['denoise_audio'],
            settings['dynamic_normalization'],
            self.build_filename_template(),
            cookies_from_browser=resolved_browser,
            video_container=settings['video_container'],
            denoise_video=settings['denoise_video'],
            stabilize_video=settings['stabilize_video'],
            sharpen_video=settings['sharpen_video'],
            normalize_video_audio=settings['normalize_video_audio'],
            denoise_video_audio=settings['denoise_video_audio'],
            fetch_lyrics_flag=settings['fetch_lyrics'],
            save_lrc=settings['save_lrc'],
        )
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def on_download_progress(self, filename, percent):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Downloading: {os.path.basename(filename)}")

    def on_download_finished(self, message):
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_label.setText(message)
        self.statusBar().showMessage("All downloads completed!")
        _plain_message(self, QMessageBox.Information, "Success", message)

    def on_download_error(self, error):
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Download failed")
        self.statusBar().showMessage("Download failed - check error message")
        _plain_message(self, QMessageBox.Critical, "Error", error)
