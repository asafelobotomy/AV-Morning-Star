"""
Generic extractor for all other platforms supported by yt-dlp
"""

from .base import BaseExtractor


class GenericExtractor(BaseExtractor):
    """Generic extractor for platforms without specific customization"""
    
    def __init__(self, url):
        """
        Initialize generic extractor
        
        Args:
            url: Video URL from any yt-dlp-supported site
        """
        super().__init__(url)
        self.platform_name = "Generic"
    
    def get_fetch_opts(self):
        """Get generic fetch options that work for most sites"""
        opts = super().get_fetch_opts()
        
        # Generic options that work across most platforms
        opts.update({
            'nocheckcertificate': False,  # Check SSL certificates
            'prefer_insecure': False,     # Use HTTPS when available
        })
        
        return opts
    
    def get_download_opts(self, output_path, filename_template, format_type, 
                         video_quality=None, audio_codec='mp3', audio_quality='192',
                         download_subs=False, embed_thumbnail=False, 
                         normalize_audio=False, denoise_audio=False,
                         dynamic_normalization=False, video_container='mp4',
                         denoise_video=False, stabilize_video=False,
                         sharpen_video=False, normalize_video_audio=False,
                         denoise_video_audio=False):
        """Get generic download options"""
        opts = super().get_download_opts(
            output_path, filename_template, format_type, video_quality,
            audio_codec, audio_quality, download_subs, embed_thumbnail,
            normalize_audio, denoise_audio, dynamic_normalization, video_container,
            denoise_video, stabilize_video, sharpen_video, normalize_video_audio,
            denoise_video_audio
        )
        
        # Generic tweaks for compatibility
        opts.update({
            'nocheckcertificate': False,
            'prefer_insecure': False,
        })
        
        return opts
