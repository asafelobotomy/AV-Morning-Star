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
# ===== FFMPEG FILTER CONFIGURATIONS =====
# These are researched best-practice settings from FFmpeg wiki, community guides,
# and professional workflows. See: https://trac.ffmpeg.org/wiki/DenoiseExamples

# --- Video Denoising Filters ---
# hqdn3d: High-quality 3D denoise - fast, good for light noise
# Parameters: luma_spatial:chroma_spatial:luma_tmp:chroma_tmp
# Weak (preserve detail): 2:1:2:3
# Medium (balanced): 4:3:6:4.5 (FFmpeg default)
# Strong (aggressive): 7:7:5:5
FFMPEG_DENOISE_VIDEO_LIGHT = 'hqdn3d=2:1:2:3'  # Weak - preserves detail
FFMPEG_DENOISE_VIDEO_MEDIUM = 'hqdn3d=4:3:6:4.5'  # Medium - balanced
FFMPEG_DENOISE_VIDEO_STRONG = 'hqdn3d=6:5:8:6'  # Strong - more aggressive

# nlmeans: Non-local means - highest quality but very slow (~160x slower than hqdn3d)
# Best for archival/quality-critical work. s=denoise strength, p=patch size, r=research size
FFMPEG_DENOISE_VIDEO_NLMEANS = 'nlmeans=s=3.5:p=7:r=15'  # High quality, slow

# --- Video Sharpening Filters ---
# unsharp: Classic unsharp mask
# Parameters: luma_msize_x:luma_msize_y:luma_amount:chroma_msize_x:chroma_msize_y:chroma_amount
# Light sharpening (subtle enhancement)
FFMPEG_SHARPEN_LIGHT = 'unsharp=3:3:0.5:3:3:0.25'
# Medium sharpening (noticeable but not harsh)
FFMPEG_SHARPEN_MEDIUM = 'unsharp=5:5:0.8:5:5:0.4'
# Strong sharpening (aggressive - may cause halos)
FFMPEG_SHARPEN_STRONG = 'unsharp=5:5:1.5:5:5:0.75'

# cas: Contrast Adaptive Sharpening (modern, edge-aware)
# strength 0.0-1.0 where 0 is no sharpening
FFMPEG_SHARPEN_CAS = 'cas=0.4'  # Balanced edge-aware sharpening

# --- Video Stabilization ---
# deshake: Single-pass stabilization (can be applied in yt-dlp workflow)
# rx/ry: search range in pixels (larger = more correction but slower)
# edge: 0=blank, 1=original, 2=clamp, 3=mirror
FFMPEG_STABILIZE_LIGHT = 'deshake=rx=16:ry=16:edge=1'  # Light correction
FFMPEG_STABILIZE_MEDIUM = 'deshake=rx=32:ry=32:edge=1'  # Medium correction
FFMPEG_STABILIZE_STRONG = 'deshake=rx=64:ry=64:edge=3:blocksize=8'  # Strong correction

# --- Video Color Correction ---
# eq filter: brightness, contrast, saturation, gamma
# brightness: -1.0 to 1.0 (0 = no change)
# contrast: 0 to 2.0 (1 = no change)
# saturation: 0 to 3.0 (1 = no change, 0 = grayscale)
# gamma: 0.1 to 10.0 (1 = no change)
FFMPEG_COLOR_BOOST = 'eq=saturation=1.2:contrast=1.1'  # Slight color boost
FFMPEG_COLOR_VIVID = 'eq=saturation=1.4:contrast=1.15:gamma=1.05'  # Vivid colors
FFMPEG_COLOR_CINEMATIC = 'eq=saturation=0.9:contrast=1.2:gamma=0.95'  # Cinematic look
FFMPEG_COLOR_BRIGHTEN = 'eq=brightness=0.06:gamma=1.1'  # Brighten dark videos

# --- Audio Denoising Filters ---
# afftdn: FFT-based denoising
# nr: noise reduction in dB (0.01-97, default 12)
# nf: noise floor in dB (range -80 to -20)
# tn: track noise (enable adaptive noise floor)
FFMPEG_DENOISE_AUDIO_LIGHT = 'afftdn=nf=-25:nr=10:tn=1'  # Light - preserves detail
FFMPEG_DENOISE_AUDIO_MEDIUM = 'afftdn=nf=-20:nr=15:tn=1'  # Medium - balanced
FFMPEG_DENOISE_AUDIO_STRONG = 'afftdn=nf=-15:nr=20:tn=1'  # Strong - aggressive

# Speech enhancement: highpass + lowpass + denoise
# Cuts sub-bass rumble (<200Hz) and high-frequency hiss (>3000Hz)
FFMPEG_SPEECH_ENHANCE = 'highpass=f=200,lowpass=f=3000,afftdn=nf=-20'

# --- Audio Normalization ---
# loudnorm: EBU R128 loudness normalization
# I: integrated loudness target (-24 to 0, -16 is broadcast standard)
# LRA: loudness range (1-20, 11 is typical)
# TP: true peak max (-9.0 to 0, -1.5 prevents clipping)
FFMPEG_NORMALIZE_BROADCAST = 'loudnorm=I=-16:LRA=11:TP=-1.5'  # EBU R128 broadcast
FFMPEG_NORMALIZE_PODCAST = 'loudnorm=I=-16:LRA=7:TP=-1'  # Tighter range for podcasts
FFMPEG_NORMALIZE_MUSIC = 'loudnorm=I=-14:LRA=11:TP=-1'  # Slightly louder for music
FFMPEG_NORMALIZE_STREAMING = 'loudnorm=I=-14:LRA=11:TP=-2'  # Streaming platforms

# Add aresample after loudnorm to fix sample rate issues (recommended by FFmpeg wiki)
FFMPEG_NORMALIZE_WITH_RESAMPLE = 'loudnorm=I=-16:LRA=11:TP=-1.5,aresample=48000'

# dynaudnorm: Dynamic audio normalization (for varying volume levels)
# p: peak target (0-1, 0.95 is safe)
# m: max gain (1-100, 10 prevents extreme boosting)
# s: smoothing (1-30, higher = smoother transitions)
# g: Gaussian filter size (3-301, higher = more temporal smoothing)
FFMPEG_DYNAUDNORM_GENTLE = 'dynaudnorm=p=0.9:m=5:s=15:g=7'  # Gentle leveling
FFMPEG_DYNAUDNORM_BALANCED = 'dynaudnorm=p=0.95:m=10:s=12:g=5'  # Balanced
FFMPEG_DYNAUDNORM_AGGRESSIVE = 'dynaudnorm=p=0.98:m=15:s=8:g=3'  # Aggressive leveling

# --- Audio Compression/Limiting ---
# compand: Dynamic range compressor
# For dialogue (reduces loud peaks, boosts quiet parts)
FFMPEG_COMPRESS_DIALOGUE = 'compand=attacks=0.1:decays=0.3:points=-80/-80|-45/-35|-27/-25|0/-10:gain=3'
# For podcast/voiceover (tighter compression)
FFMPEG_COMPRESS_PODCAST = 'compand=attacks=0.05:decays=0.2:points=-80/-80|-50/-40|-30/-25|-10/-10|0/-5:gain=4'

# --- Audio Bass/Treble Enhancement ---
# equalizer: Parametric EQ for bass boost or treble clarity
FFMPEG_BASS_BOOST = 'bass=g=5:f=100:w=0.6'  # +5dB bass boost at 100Hz
FFMPEG_TREBLE_BOOST = 'treble=g=3:f=4000:w=0.5'  # +3dB treble at 4kHz
FFMPEG_VOICE_CLARITY = 'equalizer=f=2500:width_type=o:width=1:g=3'  # Boost vocal presence

# --- Combined Filter Chains (recommended combinations) ---
# Video: Light enhancement (denoise + mild sharpen)
FFMPEG_VIDEO_ENHANCE_LIGHT = 'hqdn3d=2:1:2:3,unsharp=3:3:0.3:3:3:0.15'
# Video: Medium enhancement (denoise + sharpen + color)
FFMPEG_VIDEO_ENHANCE_MEDIUM = 'hqdn3d=4:3:6:4.5,unsharp=5:5:0.6:5:5:0.3,eq=saturation=1.1:contrast=1.05'
# Audio: Speech/podcast cleanup
FFMPEG_AUDIO_SPEECH_FULL = 'highpass=f=80,afftdn=nf=-20:tn=1,loudnorm=I=-16:LRA=7:TP=-1'
# Audio: Music enhancement
FFMPEG_AUDIO_MUSIC_FULL = 'afftdn=nf=-25:nr=8,loudnorm=I=-14:LRA=11:TP=-1'