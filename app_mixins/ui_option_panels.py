"""Video and audio download option panel builders."""

from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from constants import AUDIO_BITRATES, AUDIO_CODECS, VIDEO_CONTAINERS, VIDEO_QUALITIES


def build_video_options(app, options_layout):
    app.video_options_widget = QWidget()
    video_options_layout = QVBoxLayout(app.video_options_widget)
    video_options_layout.setContentsMargins(0, 5, 0, 5)
    video_options_layout.setSpacing(8)

    video_format_layout = QGridLayout()
    video_format_layout.setSpacing(10)
    video_format_layout.addWidget(QLabel("Video Quality:"), 0, 0)
    app.quality_combo = QComboBox()
    app.quality_combo.addItems(VIDEO_QUALITIES)
    video_format_layout.addWidget(app.quality_combo, 0, 1)

    video_format_layout.addWidget(QLabel("Video Format:"), 0, 2)
    app.video_container_combo = QComboBox()
    app.video_container_combo.addItems(VIDEO_CONTAINERS)
    app.video_container_combo.currentTextChanged.connect(app.on_video_format_changed)
    video_format_layout.addWidget(app.video_container_combo, 0, 3)

    app.subtitles_checkbox = QCheckBox("Download Subtitles")
    app.subtitles_checkbox.setChecked(False)
    video_format_layout.addWidget(app.subtitles_checkbox, 0, 4)
    video_options_layout.addLayout(video_format_layout)

    video_enhance_layout = QHBoxLayout()
    video_enhance_layout.setSpacing(15)
    app.video_denoise_checkbox = QCheckBox("Denoise Video")
    app.video_denoise_checkbox.setToolTip(
        "Remove video noise/grain using hqdn3d 3D temporal denoiser.\n"
        "Uses balanced settings (4:3:6:4.5) for quality preservation.\n"
        "Best for: grainy footage, low-light recordings"
    )
    video_enhance_layout.addWidget(app.video_denoise_checkbox)

    app.video_stabilize_checkbox = QCheckBox("Stabilize Video")
    app.video_stabilize_checkbox.setToolTip(
        "Reduce camera shake using deshake filter (single-pass).\n"
        "Uses 32px search range with edge mirroring.\n"
        "Best for: mild handheld shake; severe shake may need vidstab.\n"
        "Note: May add processing time"
    )
    video_enhance_layout.addWidget(app.video_stabilize_checkbox)

    app.video_sharpen_checkbox = QCheckBox("Sharpen")
    app.video_sharpen_checkbox.setToolTip(
        "Enhance video sharpness using unsharp mask filter.\n"
        "Uses moderate settings (5x5 kernel, 0.8 strength).\n"
        "Best for: slightly soft footage, after denoising"
    )
    video_enhance_layout.addWidget(app.video_sharpen_checkbox)
    video_enhance_layout.addStretch()
    video_options_layout.addLayout(video_enhance_layout)

    video_audio_layout = QHBoxLayout()
    video_audio_layout.setSpacing(15)
    app.video_normalize_audio_checkbox = QCheckBox("Normalize Audio")
    app.video_normalize_audio_checkbox.setToolTip(
        "Normalize audio to EBU R128 broadcast standard.\n"
        "Target: -16 LUFS with -1.5 dB true peak limit.\n"
        "Includes sample rate correction (48kHz).\n"
        "Best for: consistent playback volume"
    )
    video_audio_layout.addWidget(app.video_normalize_audio_checkbox)

    app.video_denoise_audio_checkbox = QCheckBox("Denoise Audio")
    app.video_denoise_audio_checkbox.setToolTip(
        "Remove background noise using FFT-based filter.\n"
        "Uses adaptive noise floor tracking (-20dB, 15dB reduction).\n"
        "Best for: recordings with hiss, hum, or ambient noise"
    )
    video_audio_layout.addWidget(app.video_denoise_audio_checkbox)
    video_audio_layout.addStretch()
    video_options_layout.addLayout(video_audio_layout)

    options_layout.addWidget(app.video_options_widget)


def build_audio_options(app, options_layout):
    app.audio_options_widget = QWidget()
    audio_options_layout = QVBoxLayout(app.audio_options_widget)
    audio_options_layout.setContentsMargins(0, 5, 0, 5)
    audio_options_layout.setSpacing(8)

    audio_format_layout = QGridLayout()
    audio_format_layout.setSpacing(10)
    audio_format_layout.addWidget(QLabel("Audio Codec:"), 0, 0)
    app.audio_codec_combo = QComboBox()
    app.audio_codec_combo.addItems(AUDIO_CODECS)
    app.audio_codec_combo.currentTextChanged.connect(app.on_audio_codec_changed)
    audio_format_layout.addWidget(app.audio_codec_combo, 0, 1)

    audio_format_layout.addWidget(QLabel("Audio Quality:"), 0, 2)
    app.audio_quality_combo = QComboBox()
    app.audio_quality_combo.addItems(AUDIO_BITRATES)
    app.audio_quality_combo.setCurrentIndex(3)
    audio_format_layout.addWidget(app.audio_quality_combo, 0, 3)

    app.embed_thumbnail_checkbox = QCheckBox("Embed Thumbnail")
    app.embed_thumbnail_checkbox.setChecked(True)
    app.embed_thumbnail_checkbox.setToolTip("Embed album art/thumbnail in audio file")
    audio_format_layout.addWidget(app.embed_thumbnail_checkbox, 0, 4)
    audio_options_layout.addLayout(audio_format_layout)

    audio_enhance_layout = QHBoxLayout()
    audio_enhance_layout.setSpacing(15)
    app.normalize_audio_checkbox = QCheckBox("Normalize Audio (EBU R128)")
    app.normalize_audio_checkbox.setToolTip(
        "Professional loudness normalization to EBU R128 standard.\n"
        "Target: -16 LUFS, loudness range 11 LU, true peak -1.5 dB.\n"
        "Includes sample rate correction to prevent drift.\n"
        "Best for: broadcast, streaming, consistent playback"
    )
    audio_enhance_layout.addWidget(app.normalize_audio_checkbox)

    app.dynamic_norm_checkbox = QCheckBox("Dynamic Normalization")
    app.dynamic_norm_checkbox.setToolTip(
        "Dynamic audio normalizer for varying volume levels.\n"
        "Uses: 95% peak target, 10dB max gain, smooth transitions.\n"
        "Alternative to EBU R128 for podcasts/lectures.\n"
        "Best for: speech with varying loudness"
    )
    audio_enhance_layout.addWidget(app.dynamic_norm_checkbox)

    app.denoise_checkbox = QCheckBox("Denoise Audio")
    app.denoise_checkbox.setToolTip(
        "Remove background noise using FFT-based filter.\n"
        "Uses adaptive noise floor tracking for best results.\n"
        "Settings: -20dB floor, 15dB reduction, adaptive tracking.\n"
        "Best for: recordings with hiss, hum, or ambient noise"
    )
    audio_enhance_layout.addWidget(app.denoise_checkbox)
    audio_enhance_layout.addStretch()
    audio_options_layout.addLayout(audio_enhance_layout)

    options_layout.addWidget(app.audio_options_widget)
    app.audio_options_widget.setVisible(False)
