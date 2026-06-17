"""Collect download settings from the UI and validate output paths."""

import os
import pathlib

from PyQt5.QtWidgets import QMessageBox

_CODEC_MAP = {
    'MP3': 'mp3',
    'AAC': 'aac',
    'FLAC': 'flac',
    'Opus': 'opus',
    'M4A': 'm4a',
    'WAV': 'wav',
    'ALAC': 'alac',
    'OGG Vorbis': 'vorbis',
}


def collect_download_settings(app, format_type):
    """Return yt-dlp download kwargs derived from the current UI state."""
    if app.mode == 'basic':
        return {
            'video_quality': 'Best',
            'video_container': 'mp4',
            'audio_codec': 'mp3',
            'audio_quality': '320',
            'download_subs': False,
            'embed_thumbnail': format_type == 'audio',
            'normalize_audio': False,
            'dynamic_normalization': False,
            'denoise_audio': False,
            'denoise_video': False,
            'stabilize_video': False,
            'sharpen_video': False,
            'normalize_video_audio': False,
            'denoise_video_audio': False,
        }

    audio_codec_label = app.audio_codec_combo.currentText()
    audio_quality_text = app.audio_quality_combo.currentText()
    if 'lossless' in audio_quality_text.lower():
        audio_quality = '0'
    else:
        audio_quality = audio_quality_text.split()[0]

    is_video = format_type == 'video'
    return {
        'video_quality': app.quality_combo.currentText() if is_video else None,
        'video_container': app.video_container_combo.currentText().lower() if is_video else None,
        'audio_codec': _CODEC_MAP.get(audio_codec_label, audio_codec_label.lower()),
        'audio_quality': audio_quality,
        'download_subs': app.subtitles_checkbox.isChecked(),
        'embed_thumbnail': app.embed_thumbnail_checkbox.isChecked() if not is_video else False,
        'normalize_audio': app.normalize_audio_checkbox.isChecked() if not is_video else False,
        'dynamic_normalization': app.dynamic_norm_checkbox.isChecked() if not is_video else False,
        'denoise_audio': app.denoise_checkbox.isChecked() if not is_video else False,
        'denoise_video': app.video_denoise_checkbox.isChecked() if is_video else False,
        'stabilize_video': app.video_stabilize_checkbox.isChecked() if is_video else False,
        'sharpen_video': app.video_sharpen_checkbox.isChecked() if is_video else False,
        'normalize_video_audio': app.video_normalize_audio_checkbox.isChecked() if is_video else False,
        'denoise_video_audio': app.video_denoise_audio_checkbox.isChecked() if is_video else False,
    }


def validate_output_path(app, output_path):
    """Validate output directory; show a dialog and return False on failure."""
    if not os.path.exists(output_path):
        QMessageBox.critical(
            app, "Invalid Output Directory",
            f"The output directory does not exist:\n{output_path}\n\n"
            "Please choose a valid directory in the path selector.",
        )
        return False
    if not os.path.isdir(output_path):
        QMessageBox.critical(app, "Invalid Output Directory", f"The selected path is not a directory:\n{output_path}")
        return False
    if not os.access(output_path, os.W_OK):
        QMessageBox.critical(
            app, "Output Directory Not Writable",
            f"Cannot write to the output directory:\n{output_path}\n\n"
            "Check file permissions and try again.",
        )
        return False
    return True


def resolve_output_path(raw_path):
    return str(pathlib.Path(raw_path).resolve())
