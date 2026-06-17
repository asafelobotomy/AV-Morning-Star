"""Mixin methods for MediaDownloaderApp."""






class FormatHandlersMixin:
    """Behaviour mixed into MediaDownloaderApp."""

    def on_mode_changed(self, text):
        """Toggle between Basic and Advanced modes"""
        if "Basic" in text:
            self.mode = 'basic'
            # Hide both video and audio options in basic mode
            self.video_options_widget.setVisible(False)
            self.audio_options_widget.setVisible(False)
        else:
            self.mode = 'advanced'
            # Show appropriate options based on format selection
            self.on_format_changed(self.format_combo.currentText())

    def on_format_changed(self, text):
        """Show/hide relevant options based on format selection"""
        if text == "Audio Only":
            # Show audio options, hide video options
            self.video_options_widget.setVisible(False)
            if self.mode == 'advanced':
                self.audio_options_widget.setVisible(True)
        else:
            # Show video options, hide audio options
            self.audio_options_widget.setVisible(False)
            if self.mode == 'advanced':
                self.video_options_widget.setVisible(True)

    def on_video_format_changed(self, text):
        """Enable/disable video enhancement options based on container format compatibility"""
        # Formats that support video enhancement (re-encoding with filters)
        # MP4, MKV, MOV, WebM support modern codecs and filter chains
        # AVI, FLV are legacy formats with limited codec support - filters cause errors
        supported_formats = ['MP4', 'MKV', 'MOV', 'WebM']
        format_supports_enhancement = text in supported_formats

        # Video enhancement checkboxes
        video_enhancement_checkboxes = [
            self.video_denoise_checkbox,
            self.video_stabilize_checkbox,
            self.video_sharpen_checkbox,
            self.video_normalize_audio_checkbox,
            self.video_denoise_audio_checkbox,
        ]

        # Original tooltips for when enabled
        original_tooltips = {
            self.video_denoise_checkbox: (
                "Remove video noise/grain using hqdn3d 3D temporal denoiser.\n"
                "Uses balanced settings (4:3:6:4.5) for quality preservation.\n"
                "Best for: grainy footage, low-light recordings"
            ),
            self.video_stabilize_checkbox: (
                "Reduce camera shake using deshake filter (single-pass).\n"
                "Uses 32px search range with edge mirroring.\n"
                "Best for: mild handheld shake; severe shake may need vidstab.\n"
                "Note: May add processing time"
            ),
            self.video_sharpen_checkbox: (
                "Enhance video sharpness using unsharp mask filter.\n"
                "Uses moderate settings (5x5 kernel, 0.8 strength).\n"
                "Best for: slightly soft footage, after denoising"
            ),
            self.video_normalize_audio_checkbox: (
                "Normalize audio to EBU R128 broadcast standard.\n"
                "Target: -16 LUFS with -1.5 dB true peak limit.\n"
                "Includes sample rate correction (48kHz).\n"
                "Best for: consistent playback volume"
            ),
            self.video_denoise_audio_checkbox: (
                "Remove background noise using FFT-based filter.\n"
                "Uses adaptive noise floor tracking (-20dB, 15dB reduction).\n"
                "Best for: recordings with hiss, hum, or ambient noise"
            ),
        }

        for checkbox in video_enhancement_checkboxes:
            checkbox.setEnabled(format_supports_enhancement)
            if format_supports_enhancement:
                # Restore original tooltip
                checkbox.setToolTip(original_tooltips[checkbox])
            else:
                # Uncheck and show disabled tooltip
                checkbox.setChecked(False)
                checkbox.setToolTip(
                    f"Not available for {text} format.\n\n"
                    f"{text} is a legacy format with limited codec support.\n"
                    f"Video enhancement requires re-encoding which isn't\n"
                    f"compatible with {text}.\n\n"
                    f"Use MP4, MKV, MOV, or WebM for video enhancement."
                )

    def on_audio_codec_changed(self, text):
        """Enable/disable audio options based on codec compatibility"""
        # Codecs that support thumbnail embedding (have metadata containers)
        # WAV is raw audio with no metadata support
        # FLAC supports metadata but thumbnail embedding can be problematic
        thumbnail_supported_codecs = ['MP3', 'AAC', 'M4A', 'Opus', 'OGG Vorbis', 'FLAC', 'ALAC']
        codec_supports_thumbnail = text in thumbnail_supported_codecs

        # Handle thumbnail embedding
        self.embed_thumbnail_checkbox.setEnabled(codec_supports_thumbnail)
        if codec_supports_thumbnail:
            self.embed_thumbnail_checkbox.setToolTip("Embed album art/thumbnail in audio file")
        else:
            self.embed_thumbnail_checkbox.setChecked(False)
            self.embed_thumbnail_checkbox.setToolTip(
                f"Not available for {text} format.\n\n"
                f"{text} is a raw audio format without metadata support.\n"
                f"Thumbnails cannot be embedded in this format.\n\n"
                f"Use MP3, AAC, M4A, FLAC, or OGG for thumbnail embedding."
            )

        # Lossless codecs should disable bitrate selection (use quality 0)
        lossless_codecs = ['FLAC', 'WAV', 'ALAC']
        is_lossless = text in lossless_codecs

        # When lossless codec is selected, show only Lossless quality option meaningfully
        # Other codecs can use bitrate selection
        if is_lossless:
            # For lossless, bitrate doesn't apply - select Lossless if available
            lossless_index = self.audio_quality_combo.findText("Lossless")
            if lossless_index >= 0:
                self.audio_quality_combo.setCurrentIndex(lossless_index)
            self.audio_quality_combo.setToolTip(
                f"{text} is a lossless codec.\n"
                f"Quality setting doesn't affect file size or quality.\n"
                f"Audio will be stored at full quality."
            )
        else:
            self.audio_quality_combo.setToolTip(
                "Select audio bitrate (higher = better quality, larger file)"
            )
