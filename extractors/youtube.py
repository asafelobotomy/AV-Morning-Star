"""
YouTube-specific extractor using InnerTube API (YouTube's internal API)
This bypasses yt-dlp's anti-bot detection issues by using YouTube's official client API.

NOTE: As of February 2026, YouTube has extended anti-bot protection to InnerTube API as well.
This implementation provides the foundation for when the innertube library is updated
to bypass the new protections, or can work with videos that don't trigger bot detection.

AUTHENTICATION: Now supports browser cookie extraction to bypass login requirements.
Use YouTubeExtractor(url, cookies_from_browser='firefox') to use authenticated requests.
"""

import re
import os
import http.cookiejar
from urllib.parse import urlparse, parse_qs
from innertube import InnerTube, InnerTubeAdaptor
from innertube.models import ClientContext
import httpx
import yt_dlp


class YouTubeExtractor:
    """YouTube video extractor using InnerTube API - YouTube's internal API used by official clients"""
    
    def __init__(self, url, cookies_from_browser=None):
        """
        Initialize YouTube extractor with InnerTube API
        
        Args:
            url: YouTube video/playlist/channel URL
            cookies_from_browser: Browser name to extract cookies from (e.g., 'firefox', 'chrome', 'brave')
                                 or path to cookies.txt file. If None, uses unauthenticated access.
        """
        self.url = url
        self.platform_name = "YouTube"
        self.cookies_from_browser = cookies_from_browser
        
        # Try multiple InnerTube clients - some may work better than others
        # ANDROID client seems to have best compatibility currently
        self.client_types = [
            ('ANDROID', '19.17.34'),  # Android mobile client
            ('TVHTML5', None),  # TV web client
            ('IOS', '19.16.3'),  # iOS client
            ('WEB', None),  # Standard web client
        ]
        
        self.client = None
        self._init_client()
        
        # Parse video/playlist ID from URL
        self.video_id = None
        self.playlist_id = None
        self.channel_id = None
        self._parse_url()
    
    def _init_client(self):
        """Initialize InnerTube client with optional cookie authentication"""
        cookies = None
        
        # Extract browser cookies if specified
        if self.cookies_from_browser:
            try:
                cookies = self._extract_browser_cookies()
            except Exception as e:
                print(f"Warning: Failed to extract cookies from {self.cookies_from_browser}: {e}")
                print("Continuing with unauthenticated access...")
        
        # Try to create client with cookies
        for client_name, client_version in self.client_types:
            try:
                self.client = self._create_innertube_with_cookies(
                    client_name, client_version, cookies
                )
                return  # Successfully created client
            except Exception as e:
                continue
        
        # Fallback to basic WEB client
        self.client = InnerTube('WEB')
    
    def _extract_browser_cookies(self):
        """Extract cookies from browser using yt-dlp's cookie extraction"""
        # Use yt-dlp's robust cookie extraction
        from yt_dlp.cookies import extract_cookies_from_browser
        
        # Create a cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        
        # Extract cookies for YouTube domain
        extract_cookies_from_browser(
            browser_name=self.cookies_from_browser,
            container=None,  # Auto-detect container
            logger=None,
            keyring=None
        ).extract_cookies(cookie_jar, ['https://www.youtube.com'])
        
        return cookie_jar
    
    def _create_innertube_with_cookies(self, client_name, client_version, cookies):
        """Create InnerTube client with custom httpx session that includes cookies"""
        if cookies is None:
            # No cookies - use standard initialization
            if client_version:
                return InnerTube(client_name, client_version)
            else:
                return InnerTube(client_name)
        
        # Create custom httpx client with cookies
        from innertube import api
        from innertube.config import config
        
        # Convert cookie jar to httpx cookies
        httpx_cookies = {}
        if cookies:
            for cookie in cookies:
                if cookie.domain.endswith('.youtube.com') or cookie.domain == 'youtube.com':
                    httpx_cookies[cookie.name] = cookie.value
        
        # Create httpx session with cookies
        session = httpx.Client(
            base_url=config.base_url,
            cookies=httpx_cookies,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/'
            }
        )
        
        # Get client context
        if client_version:
            context = api.get_context(client_name)
            if context:
                import dataclasses
                context = dataclasses.replace(context, client_version=client_version)
            else:
                context = ClientContext(client_name, client_version)
        else:
            context = api.get_context(client_name)
            if not context:
                context = ClientContext(client_name, "1.0")
        
        # Create custom adaptor with authenticated session
        from innertube.clients import Client
        adaptor = InnerTubeAdaptor(context=context, session=session)
        return Client(adaptor=adaptor)
    
    def _parse_url(self):
        """Extract video ID, playlist ID, or channel ID from YouTube URL"""
        parsed = urlparse(self.url)
        
        # Handle different URL formats
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # youtu.be/VIDEO_ID format
            if 'youtu.be' in parsed.netloc:
                self.video_id = parsed.path.lstrip('/')
                return
            
            # Query parameters
            query_params = parse_qs(parsed.query)
            
            # Video ID
            if 'v' in query_params:
                self.video_id = query_params['v'][0]
            
            # Playlist ID
            if 'list' in query_params:
                self.playlist_id = query_params['list'][0]
            
            # Channel/user URL patterns
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                if path_parts[0] == 'channel':
                    self.channel_id = path_parts[1]
                elif path_parts[0] in ('c', 'user', '@'):
                    # Need to resolve username to channel ID
                    # For now, store as channel identifier
                    self.channel_id = path_parts[1]
    
    def extract_info(self):
        """
        Extract video information from YouTube using InnerTube API
        
        Returns:
            list: List of dictionaries containing video info
        """
        try:
            # Handle single video
            if self.video_id and not self.playlist_id:
                return [self._extract_video_info(self.video_id)]
            
            # Handle playlist
            elif self.playlist_id:
                return self._extract_playlist_info()
            
            # Handle channel
            elif self.channel_id:
                return self._extract_channel_videos()
            
            else:
                raise Exception("Could not determine video, playlist, or channel from URL")
        
        except Exception as e:
            raise Exception(f"Failed to extract YouTube info using InnerTube API: {str(e)}")
    
    def _extract_video_info(self, video_id):
        """Extract info for a single video"""
        try:
            # Get video details from InnerTube API
            player_data = self.client.player(video_id)
            
            # Check playability status
            playability = player_data.get('playabilityStatus', {})
            status = playability.get('status', 'UNKNOWN')
            
            # Handle different status codes
            if status == 'LOGIN_REQUIRED':
                # YouTube is requiring login - this is bot detection
                reason = playability.get('reason', 'Unknown reason')
                raise Exception(f"YouTube bot detection active: {reason}.\n\n"
                              f"This is a temporary YouTube restriction affecting the InnerTube API.\n"
                              f"Possible workarounds:\n"
                              f"1. Try using yt-dlp with updated cookies\n"
                              f"2. Wait for innertube library update\n"
                              f"3. Use alternative platforms like Odysee")
            
            elif status == 'ERROR':
                error_reason = playability.get('reason', 'Unknown error')
                raise Exception(f"YouTube playability error: {error_reason}")
            
            elif status != 'OK':
                raise Exception(f"Unexpected playability status: {status}")
            
            # Extract video details
            video_details = player_data.get('videoDetails', {})
            
            if not video_details:
                raise Exception("No video details in InnerTube response - video may be unavailable")
            
            # Build video info dict
            info = {
                'id': video_id,
                'title': video_details.get('title', 'Unknown Title'),
                'uploader': video_details.get('author', 'Unknown'),
                'duration': int(video_details.get('lengthSeconds', 0)),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': video_details.get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url', ''),
                'view_count': int(video_details.get('viewCount', 0)),
                'description': video_details.get('shortDescription', ''),
            }
            
            return info
            
        except Exception as e:
            error_msg = str(e)
            # Re-raise with context
            if 'bot detection' in error_msg.lower() or 'login' in error_msg.lower():
                raise  # Already formatted
            else:
                raise Exception(f"Failed to extract video info for {video_id}: {error_msg}")
    
    def _extract_playlist_info(self):
        """Extract all videos from a playlist"""
        try:
            videos = []
            
            # Get playlist data using browse endpoint
            browse_data = self.client.browse(f'VL{self.playlist_id}')
            
            # Extract video renderers from playlist
            # This is a simplified version - full implementation would handle continuation tokens
            contents = browse_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [{}])[0].get('tabRenderer', {}).get('content', {}).get('sectionListRenderer', {}).get('contents', [])
            
            for content in contents:
                if 'itemSectionRenderer' in content:
                    for item in content['itemSectionRenderer'].get('contents', []):
                        if 'playlistVideoListRenderer' in item:
                            for video_item in item['playlistVideoListRenderer'].get('contents', []):
                                if 'playlistVideoRenderer' in video_item:
                                    video_renderer = video_item['playlistVideoRenderer']
                                    video_id = video_renderer.get('videoId')
                                    if video_id:
                                        videos.append(self._extract_video_info(video_id))
            
            return videos if videos else [{'title': 'Playlist extraction not fully implemented', 'url': self.url, 'duration': 0, 'uploader': 'Unknown'}]
            
        except Exception as e:
            # Fallback: just return the playlist URL for yt-dlp to handle
            return [{
                'title': f'Playlist {self.playlist_id}',
                'url': self.url,
                'duration': 0,
                'uploader': 'Unknown'
            }]
    
    def _extract_channel_videos(self):
        """Extract videos from a channel"""
        # Simplified implementation - return channel URL for yt-dlp to handle
        return [{
            'title': f'Channel {self.channel_id}',
            'url': self.url,
            'duration': 0,
            'uploader': self.channel_id
        }]
    
    def get_download_opts(self, output_path, filename_template, format_type, video_quality=None,
                          audio_codec='mp3', audio_quality='192', download_subs=False,
                          embed_thumbnail=False, normalize_audio=False, denoise_audio=False,
                          dynamic_normalization=False):
        """
        Get yt-dlp download options
        
        Returns:
            dict: yt-dlp options dictionary
        """
        ydl_opts = {
            'outtmpl': os.path.join(output_path, filename_template),
            'quiet': False,
            'no_warnings': False,
        }
        
        # Add browser cookies if specified
        if self.cookies_from_browser:
            ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)
        
        # Format selection
        if format_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            
            # Audio postprocessing
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_codec,
                'preferredquality': audio_quality,
            }]
            
            # Thumbnail embedding
            if embed_thumbnail:
                postprocessors.append({
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                })
                ydl_opts['writethumbnail'] = True
            
            # Audio normalization
            if normalize_audio or dynamic_normalization:
                audio_filter = []
                if normalize_audio:
                    audio_filter.append('loudnorm=I=-16:TP=-1.5:LRA=11')
                if dynamic_normalization:
                    audio_filter.append('dynaudnorm=f=150:g=15')
                if denoise_audio:
                    audio_filter.append('afftdn=nf=-25')
                
                if audio_filter:
                    postprocessors.append({
                        'key': 'FFmpegAudioFilter',
                        'audio_filter': ','.join(audio_filter),
                    })
            
            ydl_opts['postprocessors'] = postprocessors
            
        else:  # video
            if video_quality and video_quality != 'Best':
                ydl_opts['format'] = self._get_format_string(video_quality)
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
        
        # Subtitles
        if download_subs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
        
        return ydl_opts
    
    def _get_format_string(self, quality):
        """Convert quality string to yt-dlp format selector"""
        quality_map = {
            '4K (2160p)': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
            '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        }
        return quality_map.get(quality, 'bestvideo+bestaudio/best')
