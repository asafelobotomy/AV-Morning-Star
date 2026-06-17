"""Video fetch workflow and YouTube auth retry handling."""

from urllib.parse import urlparse

from PyQt5.QtWidgets import QMessageBox

from browser_utils import detect_available_browsers, get_browsers_with_youtube_cookies
from constants import drm_display_name, is_drm_host
from extractors import is_youtube_url, platform_name_for_url
from threads import URLScraperThread

from .cookie_errors import parse_cookie_error


class FetchAuthMixin:
    """Fetch videos and handle authentication retries."""

    def fetch_videos(self, *, _auth_retry=False):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return

        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Error", "Please enter a valid URL starting with http:// or https://")
            return

        # DRM pre-flight: block known DRM hosts before hitting yt-dlp.
        try:
            hostname = (urlparse(url).hostname or '').lower()
        except Exception:
            hostname = ''
        if hostname and is_drm_host(hostname):
            service = drm_display_name(hostname)
            QMessageBox.warning(
                self,
                "DRM-Protected Content",
                f"{service} uses DRM (Digital Rights Management) copy protection.\n\n"
                "DRM-protected content cannot be downloaded by this app.\n\n"
                "Affected services include: Netflix, Disney+, Prime Video, Hulu, Spotify,\n"
                "Apple TV+, HBO Max, Peacock, Crunchyroll, Rakuten TV, and others.\n\n"
                "This is a platform restriction, not a bug."
            )
            return

        if hasattr(self, 'scraper_thread') and self.scraper_thread is not None and self.scraper_thread.isRunning():
            return

        if not _auth_retry:
            self._youtube_auth_handled = False

        cookies_from_browser = None
        is_youtube = is_youtube_url(url)

        resolved_browser = None
        if self.browser_preference not in ('auto', 'none'):
            resolved_browser = self.browser_preference

        platform = platform_name_for_url(url)

        if is_youtube:
            if self.browser_preference not in ('auto', 'none') and resolved_browser:
                cookies_from_browser = resolved_browser
                self.status_label.setText(f"Fetching with {resolved_browser.title()} authentication...")
            else:
                self.status_label.setText("Fetching video information (no authentication)...")
        elif self.browser_preference not in ('auto', 'none') and resolved_browser:
            cookies_from_browser = resolved_browser
            self.status_label.setText(f"Fetching from {platform} with {resolved_browser.title()} authentication...")
        else:
            self.status_label.setText(f"Fetching from {platform}...")

        self.statusBar().showMessage(f"Connecting to {platform}...")
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.clear_videos_list()

        self.scraper_thread = URLScraperThread(url, cookies_from_browser=cookies_from_browser)
        self._fetch_cookies_used = cookies_from_browser
        self.scraper_thread.finished.connect(self.on_videos_fetched)
        self.scraper_thread.error.connect(self.on_fetch_error)
        self.scraper_thread.start()

    def parse_cookie_error(self, error):
        return parse_cookie_error(error)

    def on_fetch_error(self, error):
        user_friendly_error = parse_cookie_error(error)
        error_lower = error.lower()
        is_bot_error = (
            'sign in to confirm' in error_lower
            or ('bot' in error_lower and 'youtube' in error_lower)
        )

        is_youtube = is_youtube_url(self.url_input.text().strip())

        if is_youtube and is_bot_error and not self._youtube_auth_handled:
            self._youtube_auth_handled = True
            browsers_with_youtube = get_browsers_with_youtube_cookies()

            if browsers_with_youtube:
                browser = browsers_with_youtube[0]
                reply = QMessageBox.question(
                    self,
                    "YouTube Authentication Required",
                    f"YouTube is requesting authentication to prevent bot access.\n\n"
                    f"Good news! I detected you're logged into YouTube in {browser.title()}.\n\n"
                    f"Would you like to retry using your {browser.title()} login?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if reply == QMessageBox.Yes:
                    original_preference = self.browser_preference
                    self.browser_preference = browser
                    self.status_label.setText(f"Retrying with {browser} authentication...")
                    self.fetch_videos(_auth_retry=True)
                    self.browser_preference = original_preference
                    return

                self._youtube_auth_handled = False
                self.fetch_btn.setEnabled(True)
                self.status_label.setText("Authentication declined")
                self.statusBar().showMessage("YouTube authentication required")
                return

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
                    "YouTube requires authentication, but I couldn't find any supported browsers.\n\n"
                    "Supported browsers: Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi\n\n"
                    "Please install a browser and sign into YouTube, then try again.\n\n"
                    f"Technical details: {error[:200]}"
                )

            self.fetch_btn.setEnabled(True)
            self.status_label.setText("Authentication required")
            self.statusBar().showMessage("YouTube authentication required")
            QMessageBox.warning(self, "Authentication Required", msg)
            return

        self._youtube_auth_handled = False
        self.fetch_btn.setEnabled(True)
        self.status_label.setText("Error fetching videos")
        self.statusBar().showMessage("Failed to fetch videos")

        if user_friendly_error:
            QMessageBox.critical(self, "Error", user_friendly_error)
        else:
            QMessageBox.critical(self, "Error", error)
