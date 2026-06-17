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



class WindowLifecycleMixin:
    """Behaviour mixed into MediaDownloaderApp."""

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
