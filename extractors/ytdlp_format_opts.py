"""yt-dlp format and postprocessor option builders for downloads."""

from .ffmpeg_filters import (
    AUDIO_DENOISE_FILTER,
    AUDIO_DYNAUDNORM_FILTER,
    AUDIO_LOUDNORM_FILTER,
    VIDEO_DENOISE_FILTER,
    VIDEO_SHARPEN_FILTER,
)


def build_video_opts(
    video_quality,
    video_container='mp4',
    denoise_video=False,
    stabilize_video=False,
    sharpen_video=False,
    normalize_video_audio=False,
    denoise_video_audio=False,
):
    """Build video-specific yt-dlp options with optional FFmpeg filters."""
    quality_text = video_quality.lower() if video_quality else 'best'

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
        'merge_output_format': video_container,
    }

    video_filters = []
    audio_filters = []

    if denoise_video:
        video_filters.append(VIDEO_DENOISE_FILTER)
    if stabilize_video:
        video_filters.append('deshake')
    if sharpen_video:
        video_filters.append(VIDEO_SHARPEN_FILTER)
    if denoise_video_audio:
        audio_filters.append(AUDIO_DENOISE_FILTER)
    if normalize_video_audio:
        audio_filters.append(AUDIO_LOUDNORM_FILTER)

    if not video_filters and not audio_filters:
        return opts

    opts['postprocessors'] = opts.get('postprocessors', [])
    container_lower = video_container.lower()

    if container_lower == 'webm':
        codec_args = ['-c:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0',
                      '-c:a', 'libopus', '-b:a', '192k']
    elif container_lower == 'avi':
        codec_args = ['-c:v', 'mpeg4', '-q:v', '3', '-c:a', 'mp3', '-b:a', '192k']
    elif container_lower == 'flv':
        codec_args = ['-c:v', 'flv1', '-q:v', '3', '-c:a', 'mp3', '-b:a', '192k']
    elif container_lower == 'mov':
        codec_args = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
                      '-c:a', 'aac', '-b:a', '192k']
    else:
        codec_args = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
                      '-c:a', 'aac', '-b:a', '192k']

    opts['postprocessors'].append({
        'key': 'FFmpegVideoConvertor',
        'preferedformat': video_container.lower(),
    })

    ffmpeg_args = []
    if video_filters:
        ffmpeg_args.extend(['-vf', ','.join(video_filters)])
    if audio_filters:
        ffmpeg_args.extend(['-af', ','.join(audio_filters)])
    ffmpeg_args.extend(codec_args)

    opts['postprocessor_args'] = {'videoconvertor': ffmpeg_args}
    return opts


def build_audio_opts(
    audio_codec,
    audio_quality,
    embed_thumbnail,
    normalize_audio,
    denoise_audio,
    dynamic_normalization,
):
    """Build audio-specific yt-dlp options with optional FFmpeg filters."""
    opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_codec.lower(),
            'preferredquality': audio_quality,
        }],
    }

    audio_filters = []
    if denoise_audio:
        audio_filters.append(AUDIO_DENOISE_FILTER)
    if normalize_audio:
        if dynamic_normalization:
            audio_filters.append(AUDIO_DYNAUDNORM_FILTER)
        else:
            audio_filters.append(AUDIO_LOUDNORM_FILTER)

    if audio_filters:
        opts['postprocessor_args'] = {
            'extractaudio+ffmpeg_o': ['-af', ','.join(audio_filters)],
        }

    if embed_thumbnail:
        opts['postprocessors'].append({'key': 'EmbedThumbnail'})
        opts['writethumbnail'] = True

    opts['postprocessors'].append({'key': 'FFmpegMetadata'})
    return opts
