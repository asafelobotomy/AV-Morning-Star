"""Mixin methods for MediaDownloaderApp."""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
)

from constants import (
    ABOUT_TEXT,
    ABOUT_WINDOW_TITLE,
    HELP_GETTING_STARTED,
    HELP_MORE_INFO,
    HELP_SUPPORTED_SITES,
    HELP_WINDOW_TITLE,
    HELP_YOUTUBE_AUTH,
)
from dialogs import PreferencesDialog
from settings import save_theme


class WindowLifecycleMixin:
    """Behaviour mixed into MediaDownloaderApp."""

    def closeEvent(self, event):
        """Gracefully stop any running worker threads before closing."""
        threads = []
        if hasattr(self, 'scraper_thread') and self.scraper_thread is not None:
            threads.append(self.scraper_thread)
        if hasattr(self, 'download_thread') and self.download_thread is not None:
            threads.append(self.download_thread)
        if getattr(self, 'cookie_scan_thread', None) is not None:
            threads.append(self.cookie_scan_thread)

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

    def apply_theme(self, theme_name):
        """Apply *theme_name* ('uq', 'dark' or 'light') to the whole application."""
        from themes import resolve_theme
        theme = resolve_theme(theme_name)
        self.current_theme = theme_name
        self._active_theme = theme
        save_theme(theme_name)

        app = QApplication.instance()
        app.setStyleSheet(theme["stylesheet"])
        if theme.get("font_family"):
            font = app.font()
            font.setFamily(theme["font_family"])
            if theme.get("font_size"):
                font.setPointSize(int(theme["font_size"]))
            app.setFont(font)

        if hasattr(self, "theme_actions") and theme_name in self.theme_actions:
            self.theme_actions[theme_name].setChecked(True)
        self._watch_uq_theme()

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

    def _watch_uq_theme(self):
        """Re-apply the theme when uQ rewrites tokens.json (only while on "uq")."""
        from PyQt5.QtCore import QFileSystemWatcher, QTimer

        from themes import tokens_path
        if not hasattr(self, "_theme_watcher"):
            self._theme_watcher = QFileSystemWatcher(self)
            self._theme_debounce = QTimer(self)
            self._theme_debounce.setSingleShot(True)
            self._theme_debounce.setInterval(150)
            self._theme_debounce.timeout.connect(self._on_uq_theme_changed)
            self._theme_watcher.fileChanged.connect(lambda _p: self._theme_debounce.start())
            self._theme_watcher.directoryChanged.connect(lambda _p: self._theme_debounce.start())
        watcher = self._theme_watcher
        stale = watcher.files() + watcher.directories()
        if stale:
            watcher.removePaths(stale)
        if self.current_theme != "uq":
            return
        path = tokens_path()
        # uqd replaces the file atomically, so watch the directory too and re-add the file.
        for target in (path.parent.parent, path.parent, path):
            if target.exists():
                watcher.addPath(str(target))

    def _on_uq_theme_changed(self):
        if self.current_theme == "uq":
            self.apply_theme("uq")
