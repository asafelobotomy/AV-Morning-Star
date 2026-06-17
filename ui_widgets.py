"""Reusable PyQt5 widgets and pixmap helpers."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath


class FlowLayout(QVBoxLayout):
    """Custom layout that flows items left-to-right and wraps to new rows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(10)
        self.rows = []

    def addWidget(self, widget):
        if not self.rows or not hasattr(self, '_current_row'):
            self._current_row = QHBoxLayout()
            self._current_row.setSpacing(10)
            self._current_row.setAlignment(Qt.AlignLeft)
            super().addLayout(self._current_row)
            self.rows.append(self._current_row)

        self._current_row.addWidget(widget)

    def newRow(self):
        self._current_row = QHBoxLayout()
        self._current_row.setSpacing(10)
        self._current_row.setAlignment(Qt.AlignLeft)
        super().addLayout(self._current_row)
        self.rows.append(self._current_row)

    def clear(self):
        while self.count():
            item = self.takeAt(0)
            if item.layout():
                while item.layout().count():
                    widget_item = item.layout().takeAt(0)
                    if widget_item.widget():
                        widget_item.widget().deleteLater()
                item.layout().deleteLater()
        self.rows = []


class VideoCheckbox(QWidget):
    """Checkbox with a word-wrapping label."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        layout.addWidget(self.checkbox, 0, Qt.AlignTop)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.mousePressEvent = self._on_label_click
        layout.addWidget(self.label, 1)

    def _on_label_click(self, event):
        self.checkbox.setChecked(not self.checkbox.isChecked())

    def isChecked(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked):
        self.checkbox.setChecked(checked)


def make_circular_pixmap(pixmap):
    """Create a circular version of a pixmap."""
    size = min(pixmap.width(), pixmap.height())
    circular = QPixmap(size, size)
    circular.fill(Qt.transparent)

    painter = QPainter(circular)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()

    return circular
