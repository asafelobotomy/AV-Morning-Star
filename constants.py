"""
Application constants and commonly used terms for AV Morning Star
Centralizes strings, paths, and configuration values for easy maintenance and future-proofing
"""

# ===== APPLICATION IDENTITY =====
APP_NAME = "AV Morning Star"
APP_SUBTITLE = "Video & Audio Downloader"
APP_FULL_TITLE = f"{APP_NAME} - {APP_SUBTITLE}"
APP_VERSION = "0.3.0"
APP_COPYRIGHT = "© 2026 AV Morning Star Project"
APP_DESCRIPTION = "A powerful video and audio downloader supporting 1000+ websites."
APP_TAGLINE = "Built with PyQt5, yt-dlp, and smart browser authentication."

# ===== FILE PATHS =====
ICON_FILENAME = "av-morning-star.png"
DESKTOP_ENTRY_FILENAME = "av-morning-star.desktop"
VERSION_FILE = "VERSION"
REQUIREMENTS_FILE = "requirements.txt"

# ===== WINDOW TITLES =====
MAIN_WINDOW_TITLE = f"{APP_NAME} - {APP_SUBTITLE}"
ABOUT_WINDOW_TITLE = f"About {APP_NAME}"
HELP_WINDOW_TITLE = f"Help - {APP_NAME}"
PREFERENCES_WINDOW_TITLE = f"Preferences - {APP_NAME}"
ERROR_DIALOG_TITLE = "Error"
SUCCESS_DIALOG_TITLE = "Success"
CONFIRMATION_DIALOG_TITLE = "Confirmation"

# ===== MENU ITEMS =====
MENU_TOOLS = "Tools"
MENU_PREFERENCES = "Preferences"
MENU_ABOUT = "About"
MENU_HELP = "Help"

# ===== KEYBOARD SHORTCUTS =====
SHORTCUT_PREFERENCES = "Ctrl+,"
SHORTCUT_HELP = "F1"

# ===== BUTTON LABELS =====
BTN_FETCH = "Fetch"
BTN_DOWNLOAD_SELECTED = "Download Selected"
BTN_SELECT_ALL = "Select All"
BTN_SELECT_NONE = "Select None"
BTN_BROWSE = "Browse"
BTN_OK = "OK"
BTN_CANCEL = "Cancel"
BTN_SAVE = "Save"
BTN_CLOSE = "Close"
BTN_YES = "Yes"
BTN_NO = "No"

# ===== GROUP BOX TITLES =====
GROUP_ENTER_URL = "Enter URL"
GROUP_AVAILABLE_VIDEOS = "Available Videos/Audio"
GROUP_FILENAME_TEMPLATE = "Filename Template"
GROUP_DOWNLOAD_OPTIONS = "Download Options"
GROUP_PROGRESS = "Progress"

# ===== INPUT PLACEHOLDERS =====
PLACEHOLDER_URL = "Enter video URL or channel/playlist URL..."

# ===== STATUS MESSAGES =====
STATUS_READY = "Ready"
STATUS_CONNECTING = "Connecting to URL..."
STATUS_FETCHING = "Fetching video information..."
STATUS_FETCHING_WITH_AUTH = "Fetching with {} authentication..."
STATUS_AUTO_DETECTED = "Auto-detected {}, fetching..."
STATUS_FETCHING_NO_AUTH = "Fetching (no authentication)..."
STATUS_STARTING_DOWNLOAD = "Starting download of {} item(s)..."
STATUS_DOWNLOADING = "Downloading: {}"
STATUS_POST_PROCESSING = "Post-processing..."
STATUS_RETRYING_WITH_AUTH = "Retrying with {} authentication..."
STATUS_ERROR_FETCHING = "Error fetching videos"
STATUS_FAILED_TO_FETCH = "Failed to fetch videos"
STATUS_AUTH_DECLINED = "Authentication declined"
STATUS_AUTH_REQUIRED = "YouTube authentication required"
STATUS_NO_VIDEOS_FOUND = "No videos found"
STATUS_DOWNLOAD_FAILED = "Download failed"
STATUS_COMPLETE = "All downloads completed!"

# ===== ERROR MESSAGES =====
ERROR_NO_URL = "Please enter a URL"
ERROR_INVALID_URL = "Please enter a valid URL starting with http:// or https://"
ERROR_NO_SELECTION = "Please select at least one video to download"
ERROR_SCRAPING_URL = "Error scraping URL: {}"
ERROR_DOWNLOAD = "Error downloading: {}"

# ===== AUTHENTICATION =====
AUTH_MODE_AUTO = "Auto (Recommended)"
AUTH_MODE_NONE = "None (No authentication)"
AUTH_BROWSER_FIREFOX = "Firefox"
AUTH_BROWSER_CHROME = "Chrome"
AUTH_BROWSER_BRAVE = "Brave"
AUTH_BROWSER_EDGE = "Edge"
AUTH_BROWSER_CHROMIUM = "Chromium"
AUTH_BROWSER_OPERA = "Opera"
AUTH_BROWSER_VIVALDI = "Vivaldi"
AUTH_BROWSER_SAFARI = "Safari"

# Browser preference values (lowercase for internal use)
BROWSER_AUTO = "auto"
BROWSER_NONE = "none"
BROWSER_FIREFOX = "firefox"
BROWSER_CHROME = "chrome"
BROWSER_BRAVE = "brave"
BROWSER_EDGE = "edge"
BROWSER_CHROMIUM = "chromium"
BROWSER_OPERA = "opera"
BROWSER_VIVALDI = "vivaldi"
BROWSER_SAFARI = "safari"

# ===== DOWNLOAD MODES =====
MODE_BASIC = "basic"
MODE_ADVANCED = "advanced"
MODE_BASIC_LABEL = "Basic (Auto-detect best quality)"
MODE_ADVANCED_LABEL = "Advanced (Manual settings)"

# ===== FORMAT TYPES =====
FORMAT_VIDEO = "Video"
FORMAT_AUDIO_ONLY = "Audio Only"
FORMAT_TYPE_VIDEO = "video"
FORMAT_TYPE_AUDIO = "audio"

# ===== VIDEO QUALITIES =====
QUALITY_BEST = "Best"
QUALITY_4K = "4K (2160p)"
QUALITY_1440P = "1440p"
QUALITY_1080P = "1080p"
QUALITY_720P = "720p"
QUALITY_480P = "480p"
QUALITY_360P = "360p"

VIDEO_QUALITIES = [
    QUALITY_BEST,
    QUALITY_4K,
    QUALITY_1440P,
    QUALITY_1080P,
    QUALITY_720P,
    QUALITY_480P,
    QUALITY_360P
]

# ===== AUDIO CODECS =====
CODEC_MP3 = "MP3"
CODEC_AAC = "AAC"
CODEC_FLAC = "FLAC"
CODEC_OPUS = "Opus"
CODEC_M4A = "M4A"
CODEC_WAV = "WAV"
CODEC_ALAC = "ALAC"
CODEC_OGG = "OGG Vorbis"

AUDIO_CODECS = [CODEC_MP3, CODEC_AAC, CODEC_FLAC, CODEC_OPUS, CODEC_M4A, CODEC_WAV, CODEC_ALAC, CODEC_OGG]

# ===== AUDIO QUALITY BITRATES =====
BITRATE_320 = "320 kbps"
BITRATE_256 = "256 kbps"
BITRATE_192 = "192 kbps"
BITRATE_128 = "128 kbps"
BITRATE_96 = "96 kbps"
BITRATE_LOSSLESS = "Lossless"

AUDIO_BITRATES = [BITRATE_LOSSLESS, BITRATE_320, BITRATE_256, BITRATE_192, BITRATE_128, BITRATE_96]

# ===== VIDEO CONTAINER FORMATS =====
CONTAINER_MP4 = "MP4"
CONTAINER_MKV = "MKV"
CONTAINER_WEBM = "WebM"
CONTAINER_AVI = "AVI"
CONTAINER_MOV = "MOV"
CONTAINER_FLV = "FLV"

VIDEO_CONTAINERS = [CONTAINER_MP4, CONTAINER_MKV, CONTAINER_WEBM, CONTAINER_AVI, CONTAINER_MOV, CONTAINER_FLV]

# ===== FILENAME TEMPLATE TAGS =====
TAG_TITLE = "title"
TAG_UPLOADER = "uploader"
TAG_QUALITY = "quality"
TAG_FORMAT = "format"
TAG_WEBSITE = "website"
TAG_ID = "id"
TAG_UPLOAD_DATE = "upload_date"
TAG_DOWNLOAD_DATE = "download_date"
TAG_DURATION = "duration"
TAG_EXT = "ext"

FILENAME_TAGS = {
    TAG_TITLE: 'Title',
    TAG_UPLOADER: 'Uploader',
    TAG_QUALITY: 'Quality',
    TAG_FORMAT: 'Format',
    TAG_WEBSITE: 'Website',
    TAG_ID: 'Video ID',
    TAG_UPLOAD_DATE: 'Upload Date',
    TAG_DOWNLOAD_DATE: 'Download Date',
    TAG_DURATION: 'Duration',
    TAG_EXT: 'Extension'
}

# Default filename template tags
DEFAULT_FILENAME_TAGS = [TAG_TITLE, TAG_QUALITY, TAG_UPLOADER]

# ===== UI LABELS =====
LABEL_MODE = "Mode:"
LABEL_FORMAT = "Format:"
LABEL_VIDEO_QUALITY = "Video Quality:"
LABEL_AUDIO_CODEC = "Audio Codec:"
LABEL_AUDIO_QUALITY = "Audio Quality:"
LABEL_SAVE_TO = "Save to:"
LABEL_AUTHENTICATION = "Authentication:"
LABEL_BROWSER = "Select browser:"

# ===== CHECKBOX LABELS =====
CHECK_DOWNLOAD_SUBS = "Download Subtitles"
CHECK_EMBED_THUMBNAIL = "Embed Thumbnail (Audio)"
CHECK_NORMALIZE_AUDIO = "Normalize Audio (EBU R128)"
CHECK_DYNAMIC_NORM = "Dynamic Normalization"
CHECK_DENOISE_AUDIO = "Denoise Audio"

# ===== TOOLTIP TEXTS =====
TOOLTIP_AUTO_MODE = "Auto mode automatically finds the best browser with YouTube login"
TOOLTIP_NORMALIZE_AUDIO = "Professional loudness normalization to -16 LUFS"
TOOLTIP_DYNAMIC_NORM = "Better for varying volume levels (alternative to EBU R128)"
TOOLTIP_DENOISE = "Remove background noise using FFT-based filtering"

# ===== HELP TEXT =====
HELP_GETTING_STARTED = """
<h3>Getting Started</h3>
<ol>
<li>Enter a video URL in the input field</li>
<li>Click 'Fetch' to retrieve available videos</li>
<li>Select the videos you want to download</li>
<li>Choose your download options (format, quality, etc.)</li>
<li>Click 'Download Selected' to start</li>
</ol>
"""

HELP_YOUTUBE_AUTH = f"""
<h3>YouTube Authentication</h3>
<p>For YouTube downloads, go to <b>{MENU_TOOLS} > {MENU_PREFERENCES}</b> and select your browser. 
Make sure you're logged into YouTube in that browser.</p>
"""

HELP_SUPPORTED_SITES = """
<h3>Supported Sites</h3>
<p>YouTube, Odysee, and 1000+ other sites supported by yt-dlp.</p>
"""

HELP_MORE_INFO = """
<h3>Need More Help?</h3>
<p>Check the <b>docs/</b> folder for comprehensive guides:</p>
<ul>
<li>Getting Started Guide</li>
<li>Authentication Guide</li>
<li>Security & Privacy Guide</li>
</ul>
"""

# ===== ABOUT TEXT =====
ABOUT_TEXT = f"""
<h2>{APP_NAME}</h2>
<p>Version {APP_VERSION}</p>
<p>{APP_DESCRIPTION}</p>
<p>{APP_TAGLINE}</p>
<p>{APP_COPYRIGHT}</p>
"""

# ===== CONFIRMATION MESSAGES =====
CONFIRM_YOUTUBE_AUTH = """YouTube is requesting authentication to prevent bot access.

Good news! I detected you're logged into YouTube in {}.

Would you like to retry using your {} login?"""

# ===== PLATFORM NAMES =====
PLATFORM_YOUTUBE = "YouTube"
PLATFORM_ODYSEE = "Odysee"
PLATFORM_GENERIC = "Generic"

# ===== DEFAULT VALUES =====
DEFAULT_AUDIO_CODEC = "mp3"
DEFAULT_AUDIO_QUALITY = "192"
DEFAULT_VIDEO_QUALITY = QUALITY_BEST
DEFAULT_BROWSER_PREFERENCE = BROWSER_AUTO
DEFAULT_OUTPUT_DIR = "~/Downloads"

# ===== WINDOW SIZES =====
MAIN_WINDOW_MIN_WIDTH = 900
MAIN_WINDOW_MIN_HEIGHT = 850
PREFERENCES_WINDOW_MIN_WIDTH = 550
PREFERENCES_WINDOW_MIN_HEIGHT = 350

# ===== ICON SIZES =====
ICON_BANNER_SIZE = 60
ICON_SPLASH_SIZE = 400

# ===== DOCUMENTATION PATHS =====
DOCS_FOLDER = "docs"
DOC_README = f"{DOCS_FOLDER}/README.md"
DOC_GETTING_STARTED = f"{DOCS_FOLDER}/GETTING_STARTED.md"
DOC_AUTHENTICATION = f"{DOCS_FOLDER}/AUTHENTICATION_GUIDE.md"
DOC_SECURITY = f"{DOCS_FOLDER}/SECURITY_AND_PRIVACY.md"
DOC_ARCHITECTURE = f"{DOCS_FOLDER}/ARCHITECTURE.md"
DOC_CHANGELOG = "CHANGELOG.md"

# ===== URLs =====
URL_YOUTUBE = "https://www.youtube.com"
URL_GITHUB_REPO = "https://github.com/asafelobotomy/AV-Morning-Star"

# ===== REGEX PATTERNS =====
PATTERN_YOUTUBE_URL = r'(youtube\.com|youtu\.be)'
PATTERN_ODYSEE_URL = r'(odysee\.com|lbry\.tv)'

# ===== EMOJI/SYMBOLS (for consistency) =====
SYMBOL_CHECK = "✓"
SYMBOL_CROSS = "✗"
SYMBOL_WARNING = "⚠"
SYMBOL_INFO = "ℹ"
SYMBOL_SUCCESS = "✅"
SYMBOL_ERROR = "❌"
SYMBOL_QUESTION = "❓"
SYMBOL_LIGHTBULB = "💡"
