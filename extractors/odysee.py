"""
Odysee/LBRY-specific extractor
"""

from .base import BaseExtractor


class OdyseeExtractor(BaseExtractor):
    """Odysee/LBRY-specific video extractor"""
    
    def __init__(self, url):
        """
        Initialize Odysee extractor
        
        Args:
            url: Odysee video/channel URL
        """
        super().__init__(url)
        self.platform_name = "Odysee"
    
    def get_fetch_opts(self):
        """Get Odysee-specific fetch options"""
        opts = super().get_fetch_opts()
        
        # Odysee generally works well without special auth
        # Add any Odysee-specific options here if needed
        
        return opts
    
    def get_download_opts(self, output_path, filename_template, format_type, 
                         video_quality=None, audio_codec='mp3', audio_quality='192',
                         download_subs=False, embed_thumbnail=False, 
                         normalize_audio=False, denoise_audio=False,
                         dynamic_normalization=False):
        """Get Odysee-specific download options"""
        opts = super().get_download_opts(
            output_path, filename_template, format_type, video_quality,
            audio_codec, audio_quality, download_subs, embed_thumbnail,
            normalize_audio, denoise_audio, dynamic_normalization
        )
        
        # Odysee-specific tweaks can go here
        # For now, base options work well
        
        return opts
