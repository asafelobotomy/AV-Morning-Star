"""Download options and progress UI for MediaDownloaderApp."""

from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from constants import (
    AUDIO_BITRATES,
    AUDIO_CODECS,
    BTN_BROWSE,
    BTN_DOWNLOAD_SELECTED,
    GROUP_DOWNLOAD_OPTIONS,
    GROUP_PROGRESS,
    STATUS_READY,
    VIDEO_CONTAINERS,
    VIDEO_QUALITIES,
)


class UIOptionsMixin:
    """Download options panel and progress footer."""

    def _setup_download_options(self, main_layout):
        options_group = QGroupBox(GROUP_DOWNLOAD_OPTIONS)
        options_layout = QVBoxLayout()

        # First row: Mode and Format in grid
        top_grid = QGridLayout()
        top_grid.setSpacing(10)

        top_grid.addWidget(QLabel("Mode:"), 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Basic (Auto-detect best quality)", "Advanced (Manual settings)"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        top_grid.addWidget(self.mode_combo, 0, 1)

        top_grid.addWidget(QLabel("Format:"), 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video", "Audio Only"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        top_grid.addWidget(self.format_combo, 0, 3)

        options_layout.addLayout(top_grid)

        # === VIDEO OPTIONS (shown when Video is selected) ===
        self.video_options_widget = QWidget()
        video_options_layout = QVBoxLayout(self.video_options_widget)
        video_options_layout.setContentsMargins(0, 5, 0, 5)
        video_options_layout.setSpacing(8)

        # Video format row
        video_format_layout = QGridLayout()
        video_format_layout.setSpacing(10)

        video_format_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(VIDEO_QUALITIES)
        video_format_layout.addWidget(self.quality_combo, 0, 1)

        video_format_layout.addWidget(QLabel("Video Format:"), 0, 2)
        self.video_container_combo = QComboBox()
        self.video_container_combo.addItems(VIDEO_CONTAINERS)
        self.video_container_combo.currentTextChanged.connect(self.on_video_format_changed)
        video_format_layout.addWidget(self.video_container_combo, 0, 3)

        self.subtitles_checkbox = QCheckBox("Download Subtitles")
        self.subtitles_checkbox.setChecked(False)
        video_format_layout.addWidget(self.subtitles_checkbox, 0, 4)

        video_options_layout.addLayout(video_format_layout)

        # Video enhancement options row
        video_enhance_layout = QHBoxLayout()
        video_enhance_layout.setSpacing(15)

        self.video_denoise_checkbox = QCheckBox("Denoise Video")
        self.video_denoise_checkbox.setChecked(False)
        self.video_denoise_checkbox.setToolTip(
            "Remove video noise/grain using hqdn3d 3D temporal denoiser.\n"
            "Uses balanced settings (4:3:6:4.5) for quality preservation.\n"
            "Best for: grainy footage, low-light recordings"
        )
        video_enhance_layout.addWidget(self.video_denoise_checkbox)

        self.video_stabilize_checkbox = QCheckBox("Stabilize Video")
        self.video_stabilize_checkbox.setChecked(False)
        self.video_stabilize_checkbox.setToolTip(
            "Reduce camera shake using deshake filter (single-pass).\n"
            "Uses 32px search range with edge mirroring.\n"
            "Best for: mild handheld shake; severe shake may need vidstab.\n"
            "Note: May add processing time"
        )
        video_enhance_layout.addWidget(self.video_stabilize_checkbox)

        self.video_sharpen_checkbox = QCheckBox("Sharpen")
        self.video_sharpen_checkbox.setChecked(False)
        self.video_sharpen_checkbox.setToolTip(
            "Enhance video sharpness using unsharp mask filter.\n"
            "Uses moderate settings (5x5 kernel, 0.8 strength).\n"
            "Best for: slightly soft footage, after denoising"
        )
        video_enhance_layout.addWidget(self.video_sharpen_checkbox)

        video_enhance_layout.addStretch()
        video_options_layout.addLayout(video_enhance_layout)

        # Video audio enhancement options row
        video_audio_layout = QHBoxLayout()
        video_audio_layout.setSpacing(15)

        self.video_normalize_audio_checkbox = QCheckBox("Normalize Audio")
        self.video_normalize_audio_checkbox.setChecked(False)
        self.video_normalize_audio_checkbox.setToolTip(
            "Normalize audio to EBU R128 broadcast standard.\n"
            "Target: -16 LUFS with -1.5 dB true peak limit.\n"
            "Includes sample rate correction (48kHz).\n"
            "Best for: consistent playback volume"
        )
        video_audio_layout.addWidget(self.video_normalize_audio_checkbox)

        self.video_denoise_audio_checkbox = QCheckBox("Denoise Audio")
        self.video_denoise_audio_checkbox.setChecked(False)
        self.video_denoise_audio_checkbox.setToolTip(
            "Remove background noise using FFT-based filter.\n"
            "Uses adaptive noise floor tracking (-20dB, 15dB reduction).\n"
            "Best for: recordings with hiss, hum, or ambient noise"
        )
        video_audio_layout.addWidget(self.video_denoise_audio_checkbox)

        video_audio_layout.addStretch()
        video_options_layout.addLayout(video_audio_layout)

        options_layout.addWidget(self.video_options_widget)

        # === AUDIO OPTIONS (shown when Audio Only is selected) ===
        self.audio_options_widget = QWidget()
        audio_options_layout = QVBoxLayout(self.audio_options_widget)
        audio_options_layout.setContentsMargins(0, 5, 0, 5)
        audio_options_layout.setSpacing(8)

        # Audio codec and quality row
        audio_format_layout = QGridLayout()
        audio_format_layout.setSpacing(10)

        audio_format_layout.addWidget(QLabel("Audio Codec:"), 0, 0)
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(AUDIO_CODECS)
        self.audio_codec_combo.currentTextChanged.connect(self.on_audio_codec_changed)
        audio_format_layout.addWidget(self.audio_codec_combo, 0, 1)

        audio_format_layout.addWidget(QLabel("Audio Quality:"), 0, 2)
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(AUDIO_BITRATES)
        self.audio_quality_combo.setCurrentIndex(3)  # Default to 192 kbps
        audio_format_layout.addWidget(self.audio_quality_combo, 0, 3)

        self.embed_thumbnail_checkbox = QCheckBox("Embed Thumbnail")
        self.embed_thumbnail_checkbox.setChecked(True)
        self.embed_thumbnail_checkbox.setToolTip("Embed album art/thumbnail in audio file")
        audio_format_layout.addWidget(self.embed_thumbnail_checkbox, 0, 4)

        audio_options_layout.addLayout(audio_format_layout)

        # Audio enhancement options row
        audio_enhance_layout = QHBoxLayout()
        audio_enhance_layout.setSpacing(15)

        self.normalize_audio_checkbox = QCheckBox("Normalize Audio (EBU R128)")
        self.normalize_audio_checkbox.setChecked(False)
        self.normalize_audio_checkbox.setToolTip(
            "Professional loudness normalization to EBU R128 standard.\n"
            "Target: -16 LUFS, loudness range 11 LU, true peak -1.5 dB.\n"
            "Includes sample rate correction to prevent drift.\n"
            "Best for: broadcast, streaming, consistent playback"
        )
        audio_enhance_layout.addWidget(self.normalize_audio_checkbox)

        self.dynamic_norm_checkbox = QCheckBox("Dynamic Normalization")
        self.dynamic_norm_checkbox.setChecked(False)
        self.dynamic_norm_checkbox.setToolTip(
            "Dynamic audio normalizer for varying volume levels.\n"
            "Uses: 95% peak target, 10dB max gain, smooth transitions.\n"
            "Alternative to EBU R128 for podcasts/lectures.\n"
            "Best for: speech with varying loudness"
        )
        audio_enhance_layout.addWidget(self.dynamic_norm_checkbox)

        self.denoise_checkbox = QCheckBox("Denoise Audio")
        self.denoise_checkbox.setChecked(False)
        self.denoise_checkbox.setToolTip(
            "Remove background noise using FFT-based filter.\n"
            "Uses adaptive noise floor tracking for best results.\n"
            "Settings: -20dB floor, 15dB reduction, adaptive tracking.\n"
            "Best for: recordings with hiss, hum, or ambient noise"
        )
        audio_enhance_layout.addWidget(self.denoise_checkbox)

        audio_enhance_layout.addStretch()
        audio_options_layout.addLayout(audio_enhance_layout)

        options_layout.addWidget(self.audio_options_widget)

        # Hide audio options initially (Video is default)
        self.audio_options_widget.setVisible(False)

        # Output path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save to:"))
        self.path_label = QLabel(self.output_path)
        path_layout.addWidget(self.path_label)

        self.browse_btn = QPushButton(BTN_BROWSE)
        self.browse_btn.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.browse_btn)

        options_layout.addLayout(path_layout)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Store advanced option widgets for show/hide
        self.advanced_widgets = [
            self.quality_combo, self.video_container_combo, self.audio_codec_combo, self.audio_quality_combo,
            self.embed_thumbnail_checkbox, self.normalize_audio_checkbox,
            self.dynamic_norm_checkbox, self.denoise_checkbox
        ]
        self.advanced_labels = []

        # Set initial mode to Basic (hide advanced options)
        self.on_mode_changed("Basic (Auto-detect best quality)")


    def _setup_progress_footer(self, main_layout):
        self.download_btn = QPushButton(BTN_DOWNLOAD_SELECTED)
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        main_layout.addWidget(self.download_btn)

        # Progress Section
        progress_group = QGroupBox(GROUP_PROGRESS)
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(STATUS_READY)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        self.statusBar().showMessage(STATUS_READY)
