"""Hostname-to-display-name mapping for known media platforms.

Used to show friendly status messages like "Fetching from Vimeo..." instead of
the raw URL hostname.
"""

from urllib.parse import urlparse

# Maps exact lowercased hostname → friendly display name.
# Strip leading "www." when checking (see platform_name_for_url).
_HOST_MAP: dict[str, str] = {
    # Video platforms
    'youtube.com': 'YouTube',
    'youtu.be': 'YouTube',
    'm.youtube.com': 'YouTube',
    'vimeo.com': 'Vimeo',
    'player.vimeo.com': 'Vimeo',
    'twitch.tv': 'Twitch',
    'clips.twitch.tv': 'Twitch',
    'tiktok.com': 'TikTok',
    'vm.tiktok.com': 'TikTok',
    'dailymotion.com': 'Dailymotion',
    'dai.ly': 'Dailymotion',
    'rumble.com': 'Rumble',
    'odysee.com': 'Odysee',
    'lbry.tv': 'Odysee',
    'kick.com': 'Kick',
    'streamable.com': 'Streamable',
    'floatplane.com': 'Floatplane',
    'bitchute.com': 'BitChute',
    'loom.com': 'Loom',
    'imgur.com': 'Imgur',
    'nicovideo.jp': 'Niconico',
    'nico.ms': 'Niconico',
    'vk.com': 'VK',
    'vkvideo.ru': 'VK',
    'weibo.com': 'Weibo',
    '9gag.com': '9GAG',
    'bilibili.com': 'Bilibili',
    'b23.tv': 'Bilibili',
    # Audio / music
    'soundcloud.com': 'SoundCloud',
    'bandcamp.com': 'Bandcamp',
    'mixcloud.com': 'Mixcloud',
    'audius.co': 'Audius',
    'iheart.com': 'iHeartRadio',
    'spreaker.com': 'Spreaker',
    'audiomack.com': 'Audiomack',
    # Social / creator
    'twitter.com': 'Twitter/X',
    'x.com': 'Twitter/X',
    't.co': 'Twitter/X',
    'bsky.app': 'Bluesky',
    'instagram.com': 'Instagram',
    'facebook.com': 'Facebook',
    'fb.watch': 'Facebook',
    'reddit.com': 'Reddit',
    'v.redd.it': 'Reddit',
    'tumblr.com': 'Tumblr',
    'substack.com': 'Substack',
    'linkedin.com': 'LinkedIn',
    'pinterest.com': 'Pinterest',
    # Alt / independent video
    'peertube.social': 'PeerTube',
    'tube.tchncs.de': 'PeerTube',
    # Creators / membership / subscription
    'patreon.com': 'Patreon',
    'watchnebula.com': 'Nebula',
    'nebula.tv': 'Nebula',
    'dropout.tv': 'Dropout',
    'curiositystream.com': 'CuriosityStream',
    'roosterteeth.com': 'Rooster Teeth',
    # Education
    'khanacademy.org': 'Khan Academy',
    'ocw.mit.edu': 'MIT OpenCourseWare',
    'udemy.com': 'Udemy',
    'coursera.org': 'Coursera',
    'pbs.org': 'PBS',
    'npr.org': 'NPR',
    # Knowledge / media
    'archive.org': 'Internet Archive',
    'loc.gov': 'Library of Congress',
    'wikimedia.org': 'Wikimedia',
    'commons.wikimedia.org': 'Wikimedia Commons',
    'ted.com': 'TED',
    'c-span.org': 'C-SPAN',
    'cspan.org': 'C-SPAN',
    'nhk.or.jp': 'NHK',
    'nhk.jp': 'NHK',
    'bbc.co.uk': 'BBC',
    'bbc.com': 'BBC',
    'dw.com': 'DW',
    'aljazeera.com': 'Al Jazeera',
    'espn.com': 'ESPN',
    'nfl.com': 'NFL',
    # News
    'nytimes.com': 'NY Times',
    'theguardian.com': 'The Guardian',
    'reuters.com': 'Reuters',
    'cnn.com': 'CNN',
    'foxnews.com': 'Fox News',
    'nbcnews.com': 'NBC News',
    'bloomberg.com': 'Bloomberg',
    'washingtonpost.com': 'Washington Post',
    'wsj.com': 'Wall Street Journal',
    # Communication / productivity
    'zoom.us': 'Zoom',
    'sharepoint.com': 'SharePoint',
    # Podcast
    'fat-pie.com': 'Fat Pie Podcast',
    'anchor.fm': 'Anchor/Spotify',
    'simplecast.com': 'Simplecast',
    'megaphone.fm': 'Megaphone',
    'podbean.com': 'Podbean',
    'libsyn.com': 'Libsyn',
    # Cloud / file hosts
    'drive.google.com': 'Google Drive',
    'dropbox.com': 'Dropbox',
    'dl.dropboxusercontent.com': 'Dropbox',
    # Gaming
    'medal.tv': 'Medal.TV',
    'xbox.com': 'Xbox Clips',
}


def platform_name_for_url(url: str) -> str:
    """Return a human-readable platform name for *url*.

    Falls back to the bare hostname if no mapping is found, or "Unknown"
    if the URL cannot be parsed.

    Examples:
        platform_name_for_url("https://vimeo.com/123")  -> "Vimeo"
        platform_name_for_url("https://example.com/v")  -> "example.com"
    """
    try:
        hostname = (urlparse(url).hostname or '').lower()
    except Exception:
        return 'Unknown'

    if not hostname:
        return 'Unknown'

    # Direct lookup
    if hostname in _HOST_MAP:
        return _HOST_MAP[hostname]

    # Strip leading www. and retry
    bare = hostname.removeprefix('www.')
    if bare in _HOST_MAP:
        return _HOST_MAP[bare]

    # Subdomain fallback: try the last two labels (e.g. foo.vimeo.com → vimeo.com)
    parts = hostname.split('.')
    if len(parts) >= 2:
        root = '.'.join(parts[-2:])
        if root in _HOST_MAP:
            return _HOST_MAP[root]

    return hostname or 'Unknown'
