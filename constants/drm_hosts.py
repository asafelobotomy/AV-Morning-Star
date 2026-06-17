"""Known DRM-protected hostnames for pre-flight checking.

Mirrors the KnownDRMIE list in yt-dlp with a few additions for EU services
(e.g. www.rakuten.tv) not yet blocklisted upstream.  Only add a host here when
you are certain ALL content on that domain is DRM-protected.
"""

# Exact hostnames (lowercased, no leading www. except where intentional).
DRM_HOSTS: frozenset[str] = frozenset({
    # US streaming SVODs
    'play.hbomax.com',
    'www.hbomax.com',
    'hbomax.com',
    'www.peacocktv.com',
    'peacocktv.com',
    'www.hulu.com',
    'hulu.com',
    'www.disneyplus.com',
    'disneyplus.com',
    'www.primevideo.com',
    'primevideo.com',
    'tv.apple.com',
    'www.paramountplus.com',
    'paramountplus.com',
    'www.philo.com',
    'philo.com',
    'www.crunchyroll.com',
    'beta.crunchyroll.com',
    'crunchyroll.com',
    # Music / audio
    'open.spotify.com',
    'spotify.com',
    'www.deezer.com',
    'deezer.com',
    # International SVOD
    'www.viki.com',
    'viki.com',
    'www.mubi.com',
    'mubi.com',
    'www.zee5.com',
    'zee5.com',
    # Rakuten
    'tv.rakuten.co.jp',
    'www.rakuten.tv',         # EU — Widevine DASH, not yet in upstream KnownDRMIE
    'rakuten.tv',
    # UK/EU
    'www.channel4.com',
    'channel4.com',
    'www.channel5.com',
    'channel5.com',
    'www.6play.fr',
    '6play.fr',
    'www.rtlplay.be',
    'rtlplay.be',
    'play.rtl.hr',
    'www.rtlmost.hu',
    'rtlmost.hu',
    'plus.rtl.de',
    'www.mediasetinfinity.es',
    'www.tv5mondeplus.com',
    'tv5mondeplus.com',
    # Canada
    'www.ctv.ca',
    'ctv.ca',
    'www.noovo.ca',
    'noovo.ca',
    'www.tsn.ca',
    'tsn.ca',
    # Other
    'www.nowtv.it',
    'nowtv.it',
    'www.joyn.de',
    'joyn.de',
    'www.b-ch.com',
    'b-ch.com',
    'video.unext.jp',
    'fod.fujitv.co.jp',
    'watch.telusoriginals.com',
    'www.crackle.com',
    'www.sonycrackle.com',
    'm.sonycrackle.com',
    'www.cwtv.com',
    'cwtv.com',
    'www.cwseed.com',
    'cwseed.com',
})

# User-readable service names for pre-flight error messages
_DRM_DISPLAY_NAMES: dict[str, str] = {
    'open.spotify.com': 'Spotify',
    'spotify.com': 'Spotify',
    'www.disneyplus.com': 'Disney+',
    'disneyplus.com': 'Disney+',
    'www.peacocktv.com': 'Peacock',
    'peacocktv.com': 'Peacock',
    'www.hulu.com': 'Hulu',
    'hulu.com': 'Hulu',
    'play.hbomax.com': 'HBO Max',
    'hbomax.com': 'HBO Max',
    'www.hbomax.com': 'HBO Max',
    'www.primevideo.com': 'Amazon Prime Video',
    'primevideo.com': 'Amazon Prime Video',
    'tv.apple.com': 'Apple TV+',
    'www.paramountplus.com': 'Paramount+',
    'paramountplus.com': 'Paramount+',
    'www.crunchyroll.com': 'Crunchyroll',
    'beta.crunchyroll.com': 'Crunchyroll',
    'crunchyroll.com': 'Crunchyroll',
    'tv.rakuten.co.jp': 'Rakuten TV',
    'www.rakuten.tv': 'Rakuten TV',
    'rakuten.tv': 'Rakuten TV',
    'www.netflix.com': 'Netflix',
    'netflix.com': 'Netflix',
    'www.deezer.com': 'Deezer',
    'deezer.com': 'Deezer',
}

# Netflix isn't in KnownDRMIE (no extractor at all) but we should block it.
DRM_HOSTS = DRM_HOSTS | {'www.netflix.com', 'netflix.com'}


def is_drm_host(hostname: str) -> bool:
    """Return True if *hostname* is known to use DRM for all content."""
    return hostname.lower() in DRM_HOSTS


def drm_display_name(hostname: str) -> str:
    """Return a human-readable service name for a DRM hostname, or the hostname itself."""
    return _DRM_DISPLAY_NAMES.get(hostname.lower(), hostname)
