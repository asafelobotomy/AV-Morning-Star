#!/usr/bin/env python3
"""
AV Morning Star - Media Downloader
A PyQt5 application for downloading videos and audio from URLs
"""

import os
import sys
import traceback

from constants import (
    APP_FULL_TITLE,
    DEFAULT_FILENAME_TAGS,
    ICON_FILENAME,
    ICON_SPLASH_SIZE,
    MODE_BASIC,
)
from settings import load_browser_preference, load_output_path, load_theme

# Suppress Qt Wayland warnings
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.wayland=false'

# Add Deno to PATH if installed (required for YouTube PO tokens)
deno_path = os.path.expanduser('~/.deno/bin')
if os.path.exists(deno_path) and deno_path not in os.environ.get('PATH', ''):
    os.environ['PATH'] = f"{deno_path}:{os.environ.get('PATH', '')}"
    os.environ['DENO_INSTALL'] = os.path.expanduser('~/.deno')

from PyQt5.QtCore import Qt, QTimer  # noqa: E402
from PyQt5.QtGui import QIcon, QPixmap  # noqa: E402
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen  # noqa: E402

from app_mixins import (  # noqa: E402
    DownloadHandlersMixin,
    FetchAuthMixin,
    FilenameTagsMixin,
    FormatHandlersMixin,
    UILayoutMixin,
    UIOptionsMixin,
    VideosListMixin,
    WindowLifecycleMixin,
)
from ui_widgets import make_circular_pixmap  # noqa: E402


class MediaDownloaderApp(
    QMainWindow,
    UILayoutMixin,
    UIOptionsMixin,
    FilenameTagsMixin,
    FormatHandlersMixin,
    FetchAuthMixin,
    VideosListMixin,
    DownloadHandlersMixin,
    WindowLifecycleMixin,
):
    def __init__(self):
        super().__init__()
        self.videos_list = []
        self.checkboxes = []
        self.output_path = os.path.expanduser(load_output_path())
        self.mode = MODE_BASIC
        self.filename_template = DEFAULT_FILENAME_TAGS.copy()
        self.browser_preference = load_browser_preference()
        self._youtube_auth_handled = False
        self.current_theme = load_theme()

        self.init_ui()
        self.apply_theme(self.current_theme)


def _excepthook(exc_type, exc_value, exc_tb):
    """Log uncaught exceptions instead of letting PyQt5 abort the process.

    Without a custom hook, PyQt5 calls qFatal() on any exception raised in a
    slot, killing the whole app (and every in-flight download) with SIGABRT.
    """
    traceback.print_exception(exc_type, exc_value, exc_tb)
    app = QApplication.instance()
    if app is None:
        return
    from PyQt5.QtWidgets import QMessageBox
    box = QMessageBox(app.activeWindow())
    box.setWindowTitle("Unexpected Error")
    box.setIcon(QMessageBox.Critical)
    box.setTextFormat(Qt.PlainText)
    box.setText(f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}")
    box.exec_()


def main():
    os.environ['RESOURCE_NAME'] = 'av-morning-star'
    sys.excepthook = _excepthook

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("av-morning-star")
    app.setApplicationDisplayName(APP_FULL_TITLE)
    app.setDesktopFileName("com.github.asafelobotomy.avmorningstar.desktop")

    icon_path = os.path.join(os.path.dirname(__file__), ICON_FILENAME)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    if os.path.exists(icon_path):
        splash_pix = QPixmap(icon_path)
        scaled_splash = splash_pix.scaled(
            ICON_SPLASH_SIZE, ICON_SPLASH_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation,
        )
        splash = QSplashScreen(make_circular_pixmap(scaled_splash), Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()

        window = MediaDownloaderApp()
        QTimer.singleShot(1500, splash.close)
        QTimer.singleShot(1500, window.show)
    else:
        window = MediaDownloaderApp()
        window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
