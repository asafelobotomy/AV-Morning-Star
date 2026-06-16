"""
Browser detection and cookie utilities
"""

import glob
import os
import logging

logger = logging.getLogger(__name__)

# Chromium-based browsers: config directory roots (Linux + macOS).
_CHROMIUM_ROOTS = {
    'brave': [
        '~/.config/BraveSoftware/Brave-Browser',
        '~/Library/Application Support/BraveSoftware/Brave-Browser',
    ],
    'chrome': [
        '~/.config/google-chrome',
        '~/Library/Application Support/Google/Chrome',
    ],
    'chromium': [
        '~/.config/chromium',
        '~/Library/Application Support/Chromium',
    ],
    'edge': [
        '~/.config/microsoft-edge',
        '~/Library/Application Support/Microsoft Edge',
    ],
    'opera': [
        '~/.config/opera',
        '~/Library/Application Support/com.operasoftware.Opera',
    ],
    'vivaldi': [
        '~/.config/vivaldi',
        '~/Library/Application Support/Vivaldi',
    ],
}

_FIREFOX_ROOTS = [
    '~/.mozilla/firefox',
    '~/Library/Application Support/Firefox/Profiles',
]


def _has_chromium_cookies(config_root):
    """Return True if any Chromium profile under *config_root* has a Cookies DB."""
    root = os.path.expanduser(config_root)
    if not os.path.isdir(root):
        return False

    profile_dirs = [os.path.join(root, 'Default')]
    profile_dirs.extend(glob.glob(os.path.join(root, 'Profile *')))
    profile_dirs.extend(glob.glob(os.path.join(root, '* Profile')))

    for profile_dir in profile_dirs:
        if os.path.isfile(os.path.join(profile_dir, 'Cookies')):
            return True
    return False


def _has_firefox_cookies():
    """Return True if any Firefox profile contains cookies.sqlite."""
    for root_pattern in _FIREFOX_ROOTS:
        root = os.path.expanduser(root_pattern)
        if not os.path.isdir(root):
            continue
        for entry in os.listdir(root):
            profile_dir = os.path.join(root, entry)
            if os.path.isfile(os.path.join(profile_dir, 'cookies.sqlite')):
                return True
    return False


def detect_available_browsers():
    """
    Detect which browsers are installed and have accessible cookie databases.

    Returns:
        list: Browser names that are available (e.g., ['brave', 'firefox'])
    """
    available = []

    if _has_firefox_cookies():
        available.append('firefox')

    for browser, roots in _CHROMIUM_ROOTS.items():
        if any(_has_chromium_cookies(root) for root in roots):
            available.append(browser)

    return available


def get_browsers_with_youtube_cookies():
    """
    Check which browsers have YouTube cookies (indicating user is logged in).

    Only call this after the user has consented to cookie use (e.g. bot-detection retry).

    Returns:
        list: Browser names with YouTube authentication cookies
    """
    try:
        import yt_dlp.cookies
    except ImportError:
        return []

    available_browsers = detect_available_browsers()
    browsers_with_youtube = []

    for browser in available_browsers:
        try:
            jar = yt_dlp.cookies.extract_cookies_from_browser(browser)

            youtube_cookies = [c for c in jar if 'youtube.com' in c.domain]
            auth_cookies = [c for c in youtube_cookies if any(
                x in c.name.upper() for x in ['SAPISID', 'SSID', 'SID', 'HSID', 'APISID']
            )]

            if auth_cookies:
                browsers_with_youtube.append(browser)
        except PermissionError as exc:
            logger.warning("Cannot read %s cookie store (permission denied): %s", browser, exc)
        except OSError as exc:
            logger.warning("Cannot read %s cookie store: %s", browser, exc)
        except Exception as exc:  # noqa: BLE001 — yt-dlp raises miscellaneous internal errors
            logger.debug("Skipping %s during YouTube cookie check: %s", browser, exc)

    return browsers_with_youtube


def get_default_browser():
    """
    Get the best default browser to use when cookies are needed.

    Priority:
    1. Browser with YouTube cookies
    2. First available browser
    3. 'none' (cookieless)

    Returns:
        str: Browser name or 'none'
    """
    browsers_with_youtube = get_browsers_with_youtube_cookies()
    if browsers_with_youtube:
        return browsers_with_youtube[0]

    available = detect_available_browsers()
    if available:
        return available[0]

    return 'none'
