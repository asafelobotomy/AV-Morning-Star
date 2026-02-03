"""
Browser detection and cookie utilities
"""

import os


def detect_available_browsers():
    """
    Detect which browsers are installed and have accessible cookie databases
    
    Returns:
        list: List of browser names that are available (e.g., ['brave', 'firefox'])
    """
    browsers = {
        'brave': [
            '~/.config/BraveSoftware/Brave-Browser/Default/Cookies',
            '~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies',  # macOS
        ],
        'firefox': [
            '~/.mozilla/firefox/',  # Directory with profiles
            '~/Library/Application Support/Firefox/Profiles/',  # macOS
        ],
        'chrome': [
            '~/.config/google-chrome/Default/Cookies',
            '~/Library/Application Support/Google/Chrome/Default/Cookies',  # macOS
        ],
        'chromium': [
            '~/.config/chromium/Default/Cookies',
            '~/Library/Application Support/Chromium/Default/Cookies',  # macOS
        ],
        'edge': [
            '~/.config/microsoft-edge/Default/Cookies',
            '~/Library/Application Support/Microsoft Edge/Default/Cookies',  # macOS
        ],
        'opera': [
            '~/.config/opera/Cookies',
            '~/Library/Application Support/com.operasoftware.Opera/Cookies',  # macOS
        ],
        'vivaldi': [
            '~/.config/vivaldi/Default/Cookies',
            '~/Library/Application Support/Vivaldi/Default/Cookies',  # macOS
        ],
    }
    
    available = []
    for browser, paths in browsers.items():
        for path in paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                available.append(browser)
                break  # Found this browser, move to next
    
    return available


def get_browsers_with_youtube_cookies():
    """
    Check which browsers have YouTube cookies (indicating user is logged in)
    
    Returns:
        list: List of browser names with YouTube authentication cookies
    """
    try:
        import yt_dlp.cookies
    except ImportError:
        return []
    
    available_browsers = detect_available_browsers()
    browsers_with_youtube = []
    
    for browser in available_browsers:
        try:
            # Try to extract cookies
            jar = yt_dlp.cookies.extract_cookies_from_browser(browser)
            
            # Check for YouTube authentication cookies
            youtube_cookies = [c for c in jar if 'youtube.com' in c.domain]
            auth_cookies = [c for c in youtube_cookies if any(
                x in c.name.upper() for x in ['SAPISID', 'SSID', 'SID', 'HSID', 'APISID']
            )]
            
            if auth_cookies:
                browsers_with_youtube.append(browser)
        except Exception:
            # Browser exists but cookies not accessible or no cookies
            continue
    
    return browsers_with_youtube


def get_default_browser():
    """
    Get the best default browser to use
    
    Priority:
    1. Browser with YouTube cookies
    2. First available browser
    3. None (cookieless)
    
    Returns:
        str: Browser name or 'none'
    """
    # Try to find browser with YouTube login
    browsers_with_youtube = get_browsers_with_youtube_cookies()
    if browsers_with_youtube:
        return browsers_with_youtube[0]  # Return first one with YouTube cookies
    
    # Fall back to any available browser
    available = detect_available_browsers()
    if available:
        return available[0]
    
    # No browsers found
    return 'none'
