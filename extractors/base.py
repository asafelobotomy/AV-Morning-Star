"""
Base extractor class defining the common interface for all platform extractors
"""

import os
import yt_dlp


class BaseExtractor:
    """Base class for platform-specific video extractors"""
    
    def __init__(self, url):
        """
        Initialize the extractor
        
        Args:
            url: Video/playlist/channel URL
        """
        self.url = url
        self.platform_name = "Generic"
    
    def get_base_ydl_opts(self):
        """
        Get base yt-dlp options that apply to all platforms
        
        Returns:
            dict: Base yt-dlp options
        """
        return {
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
        }
    
    def get_fetch_opts(self):
        """
        Get yt-dlp options for fetching video metadata (not downloading)
        
        Returns:
            dict: yt-dlp options for metadata extraction
        """
        opts = self.get_base_ydl_opts()
        opts['extract_flat'] = True
        # Don't specify format when extracting metadata - prevents "format not available" errors
        # Format selection only matters during actual downloads
        opts['ignoreerrors'] = False  # We want to catch real errors
        opts['skip_download'] = True  # Ensure we never download during metadata fetch
        return opts
    
    def get_download_opts(self, output_path, filename_template, format_type, 
                         video_quality=None, audio_codec='mp3', audio_quality='192',
                         download_subs=False, embed_thumbnail=False, 
                         normalize_audio=False, denoise_audio=False,
                         dynamic_normalization=False, video_container='mp4',
                         denoise_video=False, stabilize_video=False,
                         sharpen_video=False, normalize_video_audio=False,
                         denoise_video_audio=False):
        """
        Get yt-dlp options for downloading videos/audio
        
        Args:
            output_path: Directory to save files
            filename_template: Template for output filename
            format_type: 'video' or 'audio'
            video_quality: Video quality string (e.g., 'Best', '1080p')
            audio_codec: Audio codec (mp3, aac, flac, wav, alac, ogg, etc.)
            audio_quality: Audio bitrate (e.g., '192') or '0' for lossless
            download_subs: Whether to download subtitles
            embed_thumbnail: Whether to embed thumbnail in audio
            normalize_audio: Whether to normalize audio volume
            denoise_audio: Whether to denoise audio
            dynamic_normalization: Use dynamic normalization vs EBU R128
            video_container: Video container format (mp4, mkv, webm, avi, mov, flv)
            denoise_video: Whether to denoise video
            stabilize_video: Whether to stabilize video (reduce camera shake)
            sharpen_video: Whether to sharpen video
            normalize_video_audio: Whether to normalize audio in video
            denoise_video_audio: Whether to denoise audio in video
            
        Returns:
            dict: Complete yt-dlp options for downloading
        """
        opts = self.get_base_ydl_opts()
        opts.update({
            'outtmpl': os.path.join(output_path, filename_template),
            'noprogress': False,
            'quiet': False,
            'no_warnings': False,
            'ignore_no_formats_error': False,  # Fail gracefully if no formats available
            'ignoreerrors': False,  # Don't ignore errors - we want to catch them
        })
        
        # Subtitle options
        if download_subs:
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = ['en', 'en-US']
            if format_type == 'video':
                opts['embedsubtitles'] = True
        
        # Format selection
        if format_type == 'audio':
            opts.update(self._get_audio_opts(audio_codec, audio_quality, 
                                             embed_thumbnail, normalize_audio, 
                                             denoise_audio, dynamic_normalization))
        else:
            opts.update(self._get_video_opts(video_quality, video_container,
                                             denoise_video, stabilize_video,
                                             sharpen_video, normalize_video_audio,
                                             denoise_video_audio))
        
        return opts
    
    def _get_video_opts(self, video_quality, video_container='mp4',
                       denoise_video=False, stabilize_video=False,
                       sharpen_video=False, normalize_video_audio=False,
                       denoise_video_audio=False):
        """
        Get video-specific download options with enhanced FFmpeg filter configurations.
        
        Filter settings are based on FFmpeg wiki best practices and community recommendations.
        See: https://trac.ffmpeg.org/wiki/DenoiseExamples
        
        Args:
            video_quality: Quality string from UI
            video_container: Container format (mp4, mkv, webm, avi, mov, flv)
            denoise_video: Apply video denoising filter (hqdn3d - fast, quality balanced)
            stabilize_video: Apply video stabilization (deshake - single-pass)
            sharpen_video: Apply video sharpening filter (unsharp with edge-aware settings)
            normalize_video_audio: Normalize audio track volume (EBU R128 broadcast standard)
            denoise_video_audio: Denoise audio track (FFT-based with adaptive noise floor)
            
        Returns:
            dict: Video-specific yt-dlp options
        """
        quality_text = video_quality.lower() if video_quality else 'best'
        
        # Use more flexible format selectors with multiple fallbacks
        if 'best' in quality_text:
            format_str = 'bestvideo*+bestaudio/best'
        elif '2160' in quality_text or '4k' in quality_text:
            format_str = 'bestvideo[height<=2160]+bestaudio/bestvideo*+bestaudio/best'
        elif '1440' in quality_text:
            format_str = 'bestvideo[height<=1440]+bestaudio/bestvideo*+bestaudio/best'
        elif '1080' in quality_text:
            format_str = 'bestvideo[height<=1080]+bestaudio/bestvideo*+bestaudio/best'
        elif '720' in quality_text:
            format_str = 'bestvideo[height<=720]+bestaudio/bestvideo*+bestaudio/best'
        elif '480' in quality_text:
            format_str = 'bestvideo[height<=480]+bestaudio/bestvideo*+bestaudio/best'
        elif '360' in quality_text:
            format_str = 'bestvideo[height<=360]+bestaudio/bestvideo*+bestaudio/best'
        else:
            format_str = 'best'
        
        opts = {
            'format': format_str,
            'merge_output_format': video_container
        }
        
        # Build video and audio filter chains using researched best-practice settings
        video_filters = []
        audio_filters = []
        
        # === VIDEO FILTERS ===
        
        if denoise_video:
            # hqdn3d: High-quality 3D denoise filter
            # Using medium settings: balances noise reduction with detail preservation
            # Parameters: luma_spatial:chroma_spatial:luma_tmp:chroma_tmp
            # - luma_spatial (4.0): Spatial denoising strength for luma
            # - chroma_spatial (3.0): Spatial denoising for chroma (slightly less aggressive)
            # - luma_tmp (6.0): Temporal denoising for luma (uses adjacent frames)
            # - chroma_tmp (4.5): Temporal denoising for chroma
            # Source: FFmpeg wiki, Handbrake presets
            video_filters.append('hqdn3d=4:3:6:4.5')
        
        if stabilize_video:
            # deshake: Single-pass video stabilization
            # Note: vidstab (two-pass) would be better but requires temp file,
            # which yt-dlp's workflow doesn't support well.
            # Using simple deshake for maximum compatibility
            # Source: FFmpeg docs, video stabilization community guides
            video_filters.append('deshake')
        
        if sharpen_video:
            # unsharp: Unsharp mask filter for edge enhancement
            # Using light-medium settings to enhance without creating halos:
            # - luma_msize_x/y (5): 5x5 kernel for luma sharpening
            # - luma_amount (0.8): Moderate sharpening strength (1.0+ can cause artifacts)
            # - chroma_msize_x/y (5): 5x5 kernel for chroma
            # - chroma_amount (0.4): Less aggressive on color to prevent ringing
            # Source: FFmpeg wiki, video encoding best practices
            video_filters.append('unsharp=5:5:0.8:5:5:0.4')
        
        # === AUDIO FILTERS (for video's audio track) ===
        
        if denoise_video_audio:
            # afftdn: FFT-based audio denoising with enhanced settings
            # Using adaptive noise floor tracking for better results:
            # - nf (-20): Noise floor in dB (typical background noise level)
            # - nr (15): Noise reduction amount in dB
            # - tn (1): Enable adaptive noise floor tracking (adjusts to varying noise)
            # Source: FFmpeg audio filter docs, audio engineering guides
            audio_filters.append('afftdn=nf=-20:nr=15:tn=1')
        
        if normalize_video_audio:
            # loudnorm: EBU R128 loudness normalization (broadcast standard)
            # Followed by aresample to fix sample rate issues (FFmpeg wiki recommendation):
            # - I (-16): Integrated loudness target in LUFS (broadcast standard)
            # - LRA (11): Loudness range (allows natural dynamics)
            # - TP (-1.5): True peak maximum (prevents clipping on playback)
            # - aresample (48000): Fixes sample rate issues that loudnorm can introduce
            # Source: FFmpeg wiki, EBU R128 specification
            audio_filters.append('loudnorm=I=-16:LRA=11:TP=-1.5,aresample=48000')
        
        # Apply filters via FFmpegVideoConvertor postprocessor for re-encoding
        if video_filters or audio_filters:
            # Initialize postprocessors list
            opts['postprocessors'] = opts.get('postprocessors', [])
            
            # Determine codec based on container format
            container_lower = video_container.lower()
            
            # Container-specific codec settings
            if container_lower == 'webm':
                video_codec = 'libvpx-vp9'
                audio_codec_out = 'libopus'
                codec_args = ['-c:v', video_codec, '-crf', '30', '-b:v', '0',
                              '-c:a', audio_codec_out, '-b:a', '192k']
            elif container_lower == 'avi':
                video_codec = 'mpeg4'
                audio_codec_out = 'mp3'
                codec_args = ['-c:v', video_codec, '-q:v', '3',
                              '-c:a', audio_codec_out, '-b:a', '192k']
            elif container_lower == 'flv':
                video_codec = 'flv1'
                audio_codec_out = 'mp3'
                codec_args = ['-c:v', video_codec, '-q:v', '3',
                              '-c:a', audio_codec_out, '-b:a', '192k']
            elif container_lower == 'mov':
                video_codec = 'libx264'
                audio_codec_out = 'aac'
                codec_args = ['-c:v', video_codec, '-preset', 'medium', '-crf', '18',
                              '-c:a', audio_codec_out, '-b:a', '192k']
            else:  # mp4, mkv, and default
                video_codec = 'libx264'
                audio_codec_out = 'aac'
                codec_args = ['-c:v', video_codec, '-preset', 'medium', '-crf', '18',
                              '-c:a', audio_codec_out, '-b:a', '192k']
            
            # Add video convertor postprocessor
            opts['postprocessors'].append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': video_container.lower(),
            })
            
            # Build FFmpeg arguments
            ffmpeg_args = []
            
            if video_filters:
                ffmpeg_args.extend(['-vf', ','.join(video_filters)])
            
            if audio_filters:
                ffmpeg_args.extend(['-af', ','.join(audio_filters)])
            
            # Add codec-specific encoding settings
            ffmpeg_args.extend(codec_args)
            
            opts['postprocessor_args'] = {
                'videoconvertor': ffmpeg_args
            }
        
        return opts
    
    def _get_audio_opts(self, audio_codec, audio_quality, embed_thumbnail,
                       normalize_audio, denoise_audio, dynamic_normalization):
        """
        Get audio-specific download options with enhanced FFmpeg filter configurations.
        
        Filter settings are based on FFmpeg wiki best practices, EBU R128 standards,
        and audio engineering recommendations.
        
        Args:
            audio_codec: Codec name (mp3, aac, flac, opus, etc.)
            audio_quality: Bitrate string (e.g., '192', '320', '0' for lossless)
            embed_thumbnail: Whether to embed album art/thumbnail
            normalize_audio: Whether to normalize volume (EBU R128)
            denoise_audio: Whether to apply noise reduction
            dynamic_normalization: Use dynamic normalization (for varying volume levels)
                                   instead of EBU R128
            
        Returns:
            dict: Audio-specific yt-dlp options
        """
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': []
        }
        
        # Audio extraction
        opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_codec.lower(),
            'preferredquality': audio_quality,
        })
        
        # Build audio filter chain using researched best-practice settings
        audio_filters = []
        
        if denoise_audio:
            # afftdn: FFT-based audio denoising with adaptive noise tracking
            # Enhanced settings compared to basic afftdn:
            # - nf (-20): Noise floor at -20dB (typical background noise)
            # - nr (15): 15dB noise reduction (balanced - not too aggressive)
            # - tn (1): Enable adaptive noise floor tracking
            #   This makes the filter adapt to varying noise levels in the audio
            # Source: FFmpeg audio filter docs, audio restoration guides
            audio_filters.append('afftdn=nf=-20:nr=15:tn=1')
        
        if normalize_audio:
            if dynamic_normalization:
                # dynaudnorm: Dynamic audio normalizer for varying volume levels
                # Better for content with wide dynamic range (podcasts, lectures, etc.)
                # Enhanced settings:
                # - p (0.95): Target peak at 95% to prevent clipping
                # - m (10): Max gain of 10dB prevents extreme boosting of quiet parts
                # - s (12): Smoothing factor for natural-sounding transitions
                # - g (5): Gaussian filter size for temporal smoothing
                # Source: FFmpeg docs, podcast production guides
                audio_filters.append('dynaudnorm=p=0.95:m=10:s=12:g=5')
            else:
                # loudnorm: EBU R128 loudness normalization (broadcast standard)
                # This is the professional standard for audio normalization.
                # Enhanced with aresample to fix sample rate issues (FFmpeg wiki recommendation):
                # - I (-16): Integrated loudness at -16 LUFS (broadcast standard)
                # - LRA (11): Loudness range of 11 LU (preserves natural dynamics)
                # - TP (-1.5): True peak at -1.5 dBFS (prevents inter-sample clipping)
                # - aresample (48000): Fixes sample rate drift issues that loudnorm can cause
                # Source: FFmpeg wiki, EBU R128 specification, broadcast standards
                audio_filters.append('loudnorm=I=-16:LRA=11:TP=-1.5,aresample=48000')
        
        if audio_filters:
            opts['postprocessor_args'] = {
                'ffmpeg': ['-af', ','.join(audio_filters)]
            }
        
        # Thumbnail embedding
        if embed_thumbnail:
            opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            opts['writethumbnail'] = True
        
        # Metadata embedding
        opts['postprocessors'].append({'key': 'FFmpegMetadata'})
        
        return opts
    
    def extract_info(self):
        """
        Extract video information without downloading
        
        Returns:
            list: List of video info dicts with keys: url, title, duration, uploader
        """
        try:
            ydl_opts = self.get_fetch_opts()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info and 'entries' in info:
                    # Playlist/channel
                    return self._parse_playlist(info['entries'])
                else:
                    # Single video
                    return self._parse_single_video(info)
                    
        except Exception as e:
            error_msg = strip_ansi_codes(str(e))
            
            # Check for YouTube anti-bot / n-challenge issues
            if 'n challenge solving failed' in error_msg.lower() or 'no video formats found' in error_msg.lower():
                raise Exception(f"YouTube video extraction failed due to anti-bot measures.\n\nThis is a known YouTube issue. Try:\n\n1. Wait a few minutes and try again\n2. Use a different video URL\n3. Make sure you're logged into YouTube in Brave browser\n\nTechnical: yt-dlp's n-parameter challenge solver needs updating.\nThis affects many YouTube videos currently.")
            
            # Check for common YouTube errors
            elif 'Only images are available' in error_msg or 'only images are available' in error_msg.lower():
                raise Exception(f"This video is not available for download.\n\nPossible reasons:\n• Video has been deleted or made private\n• Video is a premiere that hasn't started\n• Content is restricted in your region\n\nPlease try a different video URL.")
            elif 'Requested format is not available' in error_msg or 'format is not available' in error_msg.lower():
                raise Exception(f"This video cannot be downloaded.\n\nThis usually means:\n• Video has been deleted or made private\n• Video is currently being processed\n• Content is age-restricted or region-locked\n• YouTube anti-bot protection is active\n\nPlease verify the video works in your browser, or try a different URL.")
            elif 'Sign in' in error_msg or 'not a bot' in error_msg.lower():
                raise Exception(f"YouTube authentication required.\n\nPlease:\n1. Open YouTube in your browser (Brave)\n2. Sign in to your account\n3. Try fetching the video again\n\nThe app uses your browser's login cookies.")
            elif 'private video' in error_msg.lower() or 'video unavailable' in error_msg.lower():
                raise Exception(f"Video is private or unavailable.\n\nThis video cannot be accessed. It may be:\n• Set to private by the uploader\n• Removed by YouTube\n• Not available in your region\n\nPlease try a different video URL.")
            else:
                # Generic error with cleaned message
                raise Exception(f"Unable to fetch video information.\n\n{error_msg[:300]}\n\nPlease verify:\n• The URL is correct\n• The video is publicly accessible\n• You're logged into YouTube in your browser")
    
    def _parse_playlist(self, entries):
        """Parse playlist entries into standardized format"""
        videos = []
        for entry in entries:
            if entry:
                uploader = self._get_uploader(entry)
                videos.append({
                    'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'title': entry.get('title', 'Unknown Title'),
                    'duration': entry.get('duration', 0),
                    'uploader': uploader
                })
        return videos
    
    def _parse_single_video(self, info):
        """Parse single video info into standardized format"""
        uploader = self._get_uploader(info)
        return [{
            'url': self.url,
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'uploader': uploader
        }]
    
    def _get_uploader(self, info):
        """
        Extract uploader name with fallbacks
        
        Args:
            info: Video info dict from yt-dlp
            
        Returns:
            str: Uploader name or 'Unknown'
        """
        return (info.get('uploader') or 
                info.get('channel') or 
                info.get('uploader_id') or 
                info.get('creator') or 
                'Unknown')
