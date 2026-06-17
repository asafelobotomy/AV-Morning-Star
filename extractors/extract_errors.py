"""User-facing yt-dlp metadata extraction error messages."""


def format_extract_error(error_msg):
    lower = error_msg.lower()
    if 'n challenge solving failed' in lower or 'no video formats found' in lower:
        return Exception(
            "YouTube video extraction failed due to anti-bot measures.\n\n"
            "This is a known YouTube issue. Try:\n\n"
            "1. Wait a few minutes and try again\n"
            "2. Use a different video URL\n"
            "3. Make sure you're logged into YouTube in Brave browser\n\n"
            "Technical: yt-dlp's n-parameter challenge solver needs updating.\n"
            "This affects many YouTube videos currently."
        )
    if 'only images are available' in lower:
        return Exception(
            "This video is not available for download.\n\n"
            "Possible reasons:\n"
            "• Video has been deleted or made private\n"
            "• Video is a premiere that hasn't started\n"
            "• Content is restricted in your region\n\n"
            "Please try a different video URL."
        )
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
    if 'sign in' in error_msg or 'not a bot' in lower:
        return Exception(
            "YouTube authentication required.\n\n"
            "Please:\n"
            "1. Open YouTube in your browser (Brave)\n"
            "2. Sign in to your account\n"
            "3. Try fetching the video again\n\n"
            "The app uses your browser's login cookies."
        )
    if 'private video' in lower or 'video unavailable' in lower:
        return Exception(
            "Video is private or unavailable.\n\n"
            "This video cannot be accessed. It may be:\n"
            "• Set to private by the uploader\n"
            "• Removed by YouTube\n"
            "• Not available in your region\n\n"
            "Please try a different video URL."
        )
    return Exception(
        f"Unable to fetch video information.\n\n{error_msg[:300]}\n\n"
        "Please verify:\n"
        "• The URL is correct\n"
        "• The video is publicly accessible\n"
        "• You're logged into YouTube in your browser"
    )
