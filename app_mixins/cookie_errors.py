"""User-friendly messages for yt-dlp cookie access errors."""

from browser_utils import detect_available_browsers

_SUPPORTED_BROWSERS = (
    'firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera', 'vivaldi',
)


def parse_cookie_error(error):
    """Parse yt-dlp cookie errors into user-friendly messages."""
    error_lower = error.lower()

    if 'could not find' in error_lower and 'cookies database' in error_lower:
        for browser in _SUPPORTED_BROWSERS:
            if browser in error_lower:
                return _browser_not_found_message(browser.title())

    if 'database' in error_lower and ('corrupt' in error_lower or 'malformed' in error_lower):
        return (
            "❌ Browser cookie database is corrupted\n\n"
            "The selected browser's cookie file appears to be damaged or corrupted.\n\n"
            "💡 Try these solutions:\n"
            "  1. Restart your browser and try again\n"
            "  2. Use 'Auto (Recommended)' to try a different browser\n"
            "  3. Clear browser cookies and sign into YouTube again\n"
        )

    if 'permission denied' in error_lower or 'access denied' in error_lower:
        return (
            "❌ Permission denied\n\n"
            "Cannot access browser cookies due to file permissions.\n\n"
            "💡 This can happen if:\n"
            "  - The browser is currently running (some browsers lock cookie files)\n"
            "  - Your user account doesn't have permission to read the cookie file\n\n"
            "Try closing the browser and running this app again."
        )

    return None


def _browser_not_found_message(browser_display):
    available = detect_available_browsers()
    if available:
        msg = (
            f"❌ {browser_display} cookies not found\n\n"
            f"The selected browser ({browser_display}) doesn't appear to be installed "
            f"or doesn't have cookies on this system.\n\n"
            f"Installed browsers on this system:\n"
        )
        for browser in available:
            msg += f"  • {browser.title()}\n"
        msg += (
            "\n💡 Recommendation: Sign into YouTube in one of these browsers, "
            "then use 'Auto (Recommended)' mode in Tools > Preferences."
        )
        return msg

    return (
        f"❌ {browser_display} not found\n\n"
        f"I couldn't find {browser_display} or any other supported browsers on your system.\n\n"
        f"Supported browsers: Firefox, Chrome, Brave, Edge, Chromium, Opera, Vivaldi\n\n"
        f"💡 Recommendation: Install a browser, sign into YouTube, then use 'Auto (Recommended)' mode."
    )
