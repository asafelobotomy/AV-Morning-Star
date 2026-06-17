"""RSS / Atom feed extractor.

yt-dlp's generic extractor already handles RSS enclosure items natively.
This thin subclass adds:
  - A descriptive platform_name ("Podcast RSS") for status messages
  - Improved playlist result handling so episode titles and uploaders are
    derived from the feed title rather than from the enclosure URL

Detection is URL-based and handled by _is_rss_url() in __init__.py.
"""


from .generic import GenericExtractor


class RSSExtractor(GenericExtractor):
    """Extractor for podcast RSS / Atom feeds."""

    def __init__(self, url, cookies_from_browser=None):
        super().__init__(url, cookies_from_browser=cookies_from_browser)
        self.platform_name = "Podcast RSS"

    def get_fetch_opts(self):
        opts = super().get_fetch_opts()
        # Don't flatten playlists for RSS so individual episode info is returned.
        opts['extract_flat'] = False
        return opts

    def _parse_playlist(self, entries):
        """Build episode list from RSS feed entries.

        yt-dlp returns enclosure URLs as the 'url' field for each item.  We
        fall back to the entry id/webpage_url when the direct enclosure URL is
        absent (e.g. YouTube channel feeds).
        """
        videos = []
        for entry in entries:
            if not entry:
                continue
            url = (
                entry.get('url')
                or entry.get('webpage_url')
                or entry.get('id', '')
            )
            if not url:
                continue
            videos.append({
                'url': url,
                'title': entry.get('title', 'Unknown Episode'),
                'duration': entry.get('duration', 0),
                'uploader': self._get_uploader(entry) or 'Podcast Feed',
            })
        return videos
