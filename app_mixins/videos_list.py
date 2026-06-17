"""Mixin methods for MediaDownloaderApp."""


from PyQt5.QtWidgets import (
    QFileDialog,
)

from settings import save_output_path
from ui_widgets import VideoCheckbox


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
