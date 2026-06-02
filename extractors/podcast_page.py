"""
Generic extractor for podcast pages that link to direct audio files.

Parses HTML pages to discover direct-download audio links (mp3, m4a, ogg, etc.)
and returns them as a list of standardised media-info dicts compatible with the
rest of the extractor pipeline.
"""

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .base import BaseExtractor


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = None
        for key, value in attrs:
            if key.lower() == "href":
                href = value
                break
        if href:
            self.links.append(href)


class PodcastPageExtractor(BaseExtractor):
    """Extractor for pages that list direct-download podcast audio files."""

    def __init__(self, url):
        super().__init__(url)
        self.platform_name = "Podcast Page"

    def extract_info(self):
        if self._is_audio_url(self.url):
            return [self._build_item(self.url)]

        html = self._fetch_html(self.url)
        parser = _LinkParser()
        parser.feed(html)

        audio_urls = []
        for link in parser.links:
            if not self._is_audio_url(link):
                continue
            audio_urls.append(urljoin(self.url, link))

        # Deduplicate while preserving order
        seen = set()
        unique_audio_urls = []
        for audio_url in audio_urls:
            if audio_url in seen:
                continue
            seen.add(audio_url)
            unique_audio_urls.append(audio_url)

        return [self._build_item(audio_url) for audio_url in unique_audio_urls]

    def _fetch_html(self, url):
        """Fetch the HTML content of *url* and return it as a decoded string.

        Args:
            url: The page URL to fetch.

        Returns:
            str: Decoded HTML content of the response.

        Raises:
            urllib.error.URLError: If the request fails.
        """
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    def _is_audio_url(self, url):
        """Return True if *url* points directly to an audio file.

        Detection is based on the file extension of the URL path only;
        no network request is made.
        """
        path = urlparse(url).path.lower()
        return path.endswith(
            (".mp3", ".m4a", ".aac", ".ogg", ".opus", ".wav", ".flac")
        )

    def _build_item(self, audio_url):
        """Build a standardised media-info dict for a single audio URL.

        Args:
            audio_url: Absolute URL of the audio file.

        Returns:
            dict: Keys ``url``, ``title``, ``duration``, ``uploader``.
        """
        title = self._title_from_url(audio_url)
        return {
            "url": audio_url,
            "title": title,
            "duration": 0,
            "uploader": "Podcast Page",
        }

    def _title_from_url(self, audio_url):
        """Derive a human-readable title from an audio file URL.

        Strips the file extension and replaces underscores/hyphens with
        spaces.  Returns ``'Podcast Audio'`` if no meaningful name can be
        derived.
        """
        path = urlparse(audio_url).path
        filename = path.rsplit("/", 1)[-1]
        if "." in filename:
            filename = filename.rsplit(".", 1)[0]
        filename = filename.replace("_", " ").replace("-", " ").strip()
        return filename or "Podcast Audio"
