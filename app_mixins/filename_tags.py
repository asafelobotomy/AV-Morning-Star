"""Filename template tag selection UI."""

from PyQt5.QtWidgets import QPushButton

from .tag_buttons import create_tag_button


class FilenameTagsMixin:
    """Filename template tag chips and preview."""

    def init_filename_tags(self):
        self.all_tags = {
            'title': 'Title',
            'uploader': 'Uploader',
            'quality': 'Quality',
            'format': 'Format',
            'website': 'Website',
            'id': 'Video ID',
            'upload_date': 'Upload Date',
            'download_date': 'Timestamp',
            'duration': 'Duration',
            'ext': 'Extension',
        }
        self.selected_tag_buttons = []
        self.available_tag_buttons = []
        self.refresh_tag_buttons()
        self.update_filename_preview()

    def refresh_tag_buttons(self):
        self.selected_tags_layout.clear()
        self.available_tags_layout.clear()
        self.selected_tag_buttons.clear()
        self.available_tag_buttons.clear()

        col = 0
        max_cols = 4
        for tag in self.filename_template:
            if tag in self.all_tags:
                btn = create_tag_button(self, tag, is_selected=True)
                self.selected_tags_layout.addWidget(btn)
                self.selected_tag_buttons.append(btn)
                col += 1
                if col >= max_cols:
                    self.selected_tags_layout.newRow()
                    col = 0

        col = 0
        for tag in self.all_tags:
            if tag not in self.filename_template:
                btn = create_tag_button(self, tag, is_selected=False)
                self.available_tags_layout.addWidget(btn)
                self.available_tag_buttons.append(btn)
                col += 1
                if col >= max_cols:
                    self.available_tags_layout.newRow()
                    col = 0

    def add_tag_visual(self, tag):
        if tag and tag not in self.filename_template:
            self.filename_template.append(tag)
            self.refresh_tag_buttons()
            self.update_filename_preview()

    def remove_tag_visual(self, tag):
        if tag and tag in self.filename_template:
            self.filename_template.remove(tag)
            self.refresh_tag_buttons()
            self.update_filename_preview()

    def on_tags_reordered(self):
        pass

    def update_filename_preview(self):
        example_data = {
            'title': 'Example Video Title',
            'uploader': 'Channel Name',
            'quality': '1080p',
            'format': 'mp4',
            'website': 'YouTube',
            'id': 'dQw4w9WgXcQ',
            'upload_date': '20260115',
            'download_date': '1749000000',
            'duration': '03-45-20',
            'ext': 'mp4',
        }

        parts = [example_data[tag] for tag in self.filename_template if tag in example_data]
        self.filename_preview.setText(' - '.join(parts) + '.mp4')

    def build_filename_template(self):
        tag_mapping = {
            'title': '%(title)s',
            'uploader': '%(uploader)s',
            'quality': '%(height)sp' if self.format_combo.currentText() == 'Video' else '%(abr)skbps',
            'format': '%(format_id)s',
            'website': '%(extractor)s',
            'id': '%(id)s',
            'upload_date': '%(upload_date)s',
            'download_date': '%(epoch)s',
            'duration': '%(duration_string)s',
            'ext': '%(ext)s',
        }

        parts = [tag_mapping[tag] for tag in self.filename_template if tag in tag_mapping]
        if not parts:
            return '%(title)s.%(ext)s'

        template = ' - '.join(parts)
        if '%(ext)s' not in template:
            template += '.%(ext)s'
        return template
