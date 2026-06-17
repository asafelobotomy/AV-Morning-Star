"""Help, about, and confirmation copy."""

from .identity import APP_COPYRIGHT, APP_DESCRIPTION, APP_NAME, APP_TAGLINE, APP_VERSION
from .windows import MENU_PREFERENCES, MENU_TOOLS

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
