"""Background worker threads for metadata fetching and downloads."""

import os

import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

from extractors import get_extractor


class URLScraperThread(QThread):
    """Thread for scraping video URLs from a page using platform-specific extractors."""

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url, cookies_from_browser=None):
        super().__init__()
        self.url = url
        self.cookies_from_browser = cookies_from_browser

    def run(self):
        try:
            if self.isInterruptionRequested():
                return

            extractor = get_extractor(
                self.url,
                cookies_from_browser=self.cookies_from_browser,
            )

            if self.isInterruptionRequested():
                return

            videos = extractor.extract_info()

            if not self.isInterruptionRequested():
                self.finished.emit(videos)

        except Exception as e:
            if not self.isInterruptionRequested():
                self.error.emit(f"Error scraping URL: {str(e)}")


class DownloadThread(QThread):
    """Thread for downloading videos/audio using platform-specific extractors."""

    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        urls,
        output_path,
        format_type,
        video_quality=None,
        audio_codec='mp3',
        audio_quality='192',
        download_subs=False,
        embed_thumbnail=False,
        normalize_audio=False,
        denoise_audio=False,
        dynamic_normalization=False,
        filename_template=None,
        cookies_from_browser=None,
        video_container='mp4',
        denoise_video=False,
        stabilize_video=False,
        sharpen_video=False,
        normalize_video_audio=False,
        denoise_video_audio=False,
    ):
        super().__init__()
        self.urls = urls
        self.output_path = output_path
        self.format_type = format_type
        self.video_quality = video_quality
        self.video_container = video_container
        self.audio_codec = audio_codec
        self.audio_quality = audio_quality
        self.download_subs = download_subs
        self.embed_thumbnail = embed_thumbnail
        self.normalize_audio = normalize_audio
        self.denoise_audio = denoise_audio
        self.dynamic_normalization = dynamic_normalization
        self.filename_template = filename_template or '%(title)s.%(ext)s'
        self.cookies_from_browser = cookies_from_browser
        self.denoise_video = denoise_video
        self.stabilize_video = stabilize_video
        self.sharpen_video = sharpen_video
        self.normalize_video_audio = normalize_video_audio
        self.denoise_video_audio = denoise_video_audio

    def progress_hook(self, d):
        if self.isInterruptionRequested():
            raise Exception("Download cancelled")

        if d['status'] == 'downloading':
            percent = 0

            if '_percent_str' in d:
                try:
                    percent_str = d['_percent_str'].strip().replace('%', '')
                    percent = float(percent_str)
                except (ValueError, AttributeError):
                    pass

            if percent == 0 and 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
                try:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                except (ZeroDivisionError, TypeError):
                    pass

            if percent == 0 and 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                try:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                except (ZeroDivisionError, TypeError):
                    pass

            filename = d.get('filename', d.get('_filename', 'Downloading...'))
            if filename and len(filename) > 50:
                filename = '...' + filename[-47:]

            self.progress.emit(filename, max(0, min(100, int(percent))))

        elif d['status'] == 'finished':
            self.progress.emit('Post-processing...', 100)

    def run(self):
        successful = 0
        failed = 0
        failed_urls = []

        for idx, url in enumerate(self.urls, 1):
            if self.isInterruptionRequested():
                break
            try:
                extractor = get_extractor(url, cookies_from_browser=self.cookies_from_browser)

                ydl_opts = extractor.get_download_opts(
                    self.output_path,
                    self.filename_template,
                    self.format_type,
                    self.video_quality,
                    self.audio_codec,
                    self.audio_quality,
                    self.download_subs,
                    self.embed_thumbnail,
                    self.normalize_audio,
                    self.denoise_audio,
                    self.dynamic_normalization,
                    self.video_container,
                    self.denoise_video,
                    self.stabilize_video,
                    self.sharpen_video,
                    self.normalize_video_audio,
                    self.denoise_video_audio,
                )

                ydl_opts['progress_hooks'] = [self.progress_hook]

                self.progress.emit(f'Downloading {idx}/{len(self.urls)}...', 0)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                successful += 1

            except Exception as e:
                if self.isInterruptionRequested():
                    break
                failed += 1
                failed_urls.append((url, str(e)))
                self.progress.emit(f'Failed {idx}/{len(self.urls)}, continuing...', 0)
                continue

        if self.isInterruptionRequested():
            self.finished.emit(
                f"Download cancelled. "
                f"{successful} completed before cancellation."
                if successful else "Download cancelled."
            )
            return

        if failed == 0:
            self.finished.emit(f"All {successful} downloads completed successfully!")
        elif successful == 0:
            error_msg = f"All {failed} downloads failed.\n\nErrors:\n"
            for url, err in failed_urls[:3]:
                error_msg += f"- {err[:100]}...\n"
            self.error.emit(error_msg)
        else:
            message = f"Completed with mixed results:\n✓ {successful} succeeded\n✗ {failed} failed"
            if failed_urls:
                message += f"\n\nFirst error: {failed_urls[0][1][:150]}"
            self.finished.emit(message)
