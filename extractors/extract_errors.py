"""User-facing yt-dlp metadata extraction error messages."""


def format_extract_error(error_msg):
    lower = error_msg.lower()

    # DRM-protected services — yt-dlp raises this explicitly via KnownDRMIE
    if 'known to use drm protection' in lower or (
        'drm' in lower and 'not be supported' in lower
    ):
        return Exception(
            "This service uses DRM copy protection and cannot be downloaded.\n\n"
            "DRM-protected services include: Netflix, Disney+, Prime Video, Hulu,\n"
            "Spotify, Apple TV+, HBO Max, Peacock, Crunchyroll, Rakuten TV, and others.\n\n"
            "This is a platform restriction, not a bug in the app."
        )

    # Geo-restriction
    if (
        'not available in your country' in lower
        or 'not available in your region' in lower
        or 'geo' in lower and ('restrict' in lower or 'block' in lower)
        or 'georestrict' in lower
        or 'this video is not available' in lower and 'region' in lower
    ):
        return Exception(
            "This content is not available in your region.\n\n"
            "The site or content owner has restricted access based on location.\n\n"
            "Possible workarounds:\n"
            "• Use a VPN to appear to connect from another country\n"
            "• Try a different video from the same site\n\n"
            "The app cannot bypass geographic restrictions."
        )

    # Login required / members-only
    if (
        'login required' in lower
        or 'members only' in lower
        or 'subscriber only' in lower
        or 'requires subscription' in lower
        or 'log in to' in lower
        or 'please log in' in lower
    ):
        return Exception(
            "This content requires you to be logged in.\n\n"
            "To download it:\n"
            "1. Log in to this site in your browser\n"
            "2. Open Tools > Preferences\n"
            "3. Select that browser under Authentication\n"
            "4. Try fetching again\n\n"
            "The app will use your browser's login session."
        )

    # Rate limiting
    if (
        'rate' in lower and 'limit' in lower
        or 'too many requests' in lower
        or '429' in lower
    ):
        return Exception(
            "Rate limited — the site is temporarily blocking requests.\n\n"
            "Please wait a few minutes and try again.\n\n"
            "If this keeps happening, try:\n"
            "• Logging in via Tools > Preferences (cookies reduce rate limits)\n"
            "• Downloading fewer items at once"
        )

    # Content removed / unavailable
    if (
        'this video has been removed' in lower
        or 'video unavailable' in lower
        or 'private video' in lower
        or 'deleted' in lower and 'video' in lower
    ):
        return Exception(
            "Video is private or unavailable.\n\n"
            "This video cannot be accessed. It may be:\n"
            "• Set to private by the uploader\n"
            "• Removed by the platform\n"
            "• Not available in your region\n\n"
            "Please try a different URL."
        )

    # YouTube-specific: n-parameter / anti-bot
    if 'n challenge solving failed' in lower or 'no video formats found' in lower:
        return Exception(
            "YouTube video extraction failed due to anti-bot measures.\n\n"
            "This is a known YouTube issue. Try:\n\n"
            "1. Wait a few minutes and try again\n"
            "2. Use a different video URL\n"
            "3. Make sure you're logged into YouTube in your browser\n\n"
            "Technical: yt-dlp's n-parameter challenge solver needs updating.\n"
            "This affects some YouTube videos currently."
        )

    # Only images available (YouTube premiere / unstarted stream)
    if 'only images are available' in lower:
        return Exception(
            "This video is not available for download.\n\n"
            "Possible reasons:\n"
            "• Video has been deleted or made private\n"
            "• Video is a premiere that hasn't started yet\n"
            "• Content is restricted in your region\n\n"
            "Please try a different video URL."
        )

    # Format not available
    if 'format is not available' in lower:
        return Exception(
            "This video cannot be downloaded.\n\n"
            "This usually means:\n"
            "• Video has been deleted or made private\n"
            "• Video is currently being processed\n"
            "• Content is age-restricted or region-locked\n"
            "• YouTube anti-bot protection is active\n\n"
            "Please verify the video works in your browser, or try a different URL."
        )

    # YouTube sign-in required
    if 'sign in' in error_msg or 'not a bot' in lower:
        return Exception(
            "YouTube authentication required.\n\n"
            "Please:\n"
            "1. Open YouTube in your browser\n"
            "2. Sign in to your account\n"
            "3. Try fetching the video again\n\n"
            "The app uses your browser's login cookies."
        )

    return Exception(
        f"Unable to fetch video information.\n\n{error_msg[:300]}\n\n"
        "Please verify:\n"
        "• The URL is correct and publicly accessible\n"
        "• Your internet connection is working\n"
        "• If the site requires login, set your browser in Tools > Preferences"
    )
