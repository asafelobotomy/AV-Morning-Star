"""Download options and progress UI for MediaDownloaderApp."""

from PyQt5.QtWidgets import (
    QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QVBoxLayout,
)

from constants import (
    BTN_BROWSE,
    BTN_DOWNLOAD_SELECTED,
    GROUP_DOWNLOAD_OPTIONS,
    GROUP_PROGRESS,
    STATUS_READY,
)

from .ui_option_panels import build_audio_options, build_video_options


class UIOptionsMixin:
    """Download options panel and progress footer."""

    def _setup_download_options(self, main_layout):
        options_group = QGroupBox(GROUP_DOWNLOAD_OPTIONS)
        options_layout = QVBoxLayout()

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

        build_video_options(self, options_layout)
        build_audio_options(self, options_layout)

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

        self.advanced_widgets = [
            self.quality_combo, self.video_container_combo, self.audio_codec_combo,
            self.audio_quality_combo, self.embed_thumbnail_checkbox,
            self.normalize_audio_checkbox, self.dynamic_norm_checkbox, self.denoise_checkbox,
        ]
        self.advanced_labels = []
        self.on_mode_changed("Basic (Auto-detect best quality)")

    def _setup_progress_footer(self, main_layout):
        self.download_btn = QPushButton(BTN_DOWNLOAD_SELECTED)
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        main_layout.addWidget(self.download_btn)

        progress_group = QGroupBox(GROUP_PROGRESS)
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel(STATUS_READY)
        progress_layout.addWidget(self.status_label)
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        self.statusBar().showMessage(STATUS_READY)
