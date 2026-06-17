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



class FetchAuthMixin:
    """Behaviour mixed into MediaDownloaderApp."""

    def fetch_videos(self, *, _auth_retry=False):
        """Fetch videos from URL."""
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

        if not _auth_retry:
            self._youtube_auth_handled = False

        cookies_from_browser = None
        is_youtube = is_youtube_url(url)

        # Resolve explicit browser preference only — never probe cookie stores here.
        resolved_browser = None
        if self.browser_preference not in ('auto', 'none'):
            resolved_browser = self.browser_preference

        if is_youtube:
            explicit_browser_chosen = self.browser_preference not in ('auto', 'none')
            if explicit_browser_chosen and resolved_browser:
                cookies_from_browser = resolved_browser
                self.status_label.setText(
                    f"Fetching with {resolved_browser.title()} authentication..."
                )
            else:
                self.status_label.setText("Fetching video information (no authentication)...")
        elif self.browser_preference not in ('auto', 'none') and resolved_browser:
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
        if is_youtube and is_bot_error and not self._youtube_auth_handled:
            self._youtube_auth_handled = True

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
                    original_preference = self.browser_preference
                    self.browser_preference = browser
                    self.status_label.setText(f"Retrying with {browser} authentication...")
                    self.fetch_videos(_auth_retry=True)
                    self.browser_preference = original_preference
                    return
                else:
                    self._youtube_auth_handled = False
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
        self._youtube_auth_handled = False
        self.fetch_btn.setEnabled(True)
        self.status_label.setText("Error fetching videos")
        self.statusBar().showMessage("Failed to fetch videos")

        # Show user-friendly error if available, otherwise show technical error
        if user_friendly_error:
            QMessageBox.critical(self, "Error", user_friendly_error)
        else:
            QMessageBox.critical(self, "Error", error)
