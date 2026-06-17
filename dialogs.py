"""Application dialog windows."""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from constants import (
    BTN_CANCEL,
    BTN_SAVE,
    GROUP_AUTHENTICATION,
    PREFERENCES_WINDOW_MIN_HEIGHT,
    PREFERENCES_WINDOW_MIN_WIDTH,
    PREFERENCES_WINDOW_TITLE,
)
from settings import save_browser_preference


class PreferencesDialog(QDialog):
    """Preferences dialog for application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(PREFERENCES_WINDOW_TITLE)
        self.setMinimumSize(PREFERENCES_WINDOW_MIN_WIDTH, PREFERENCES_WINDOW_MIN_HEIGHT)
        self.setModal(True)

        self.parent_app = parent

        layout = QVBoxLayout(self)

        title = QLabel("Preferences")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        layout.addSpacing(20)

        auth_group = QGroupBox(GROUP_AUTHENTICATION)
        auth_layout = QVBoxLayout()

        main_desc = QLabel(
            "To download YouTube videos, AV Morning Star can use your browser's login session.\n"
            "Simply select the browser where you're logged into YouTube."
        )
        main_desc.setWordWrap(True)
        auth_layout.addWidget(main_desc)

        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Authentication:"))

        self.browser_combo = QComboBox()
        self.browser_combo.addItems([
            "Auto (Recommended)",
            "None (No authentication)",
            "Firefox",
            "Chrome",
            "Brave",
            "Edge",
            "Chromium",
            "Opera",
            "Vivaldi",
        ])
        self.browser_combo.setToolTip(
            "Auto mode tries without cookies first and asks before reading browser cookies"
        )
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addStretch()

        auth_layout.addLayout(browser_layout)

        instructions = QLabel(
            "<b>Important:</b> Make sure you're logged into YouTube in the selected browser before downloading."
        )
        instructions.setWordWrap(True)
        instructions.setObjectName("auth_instructions")
        auth_layout.addWidget(instructions)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(BTN_CANCEL)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(BTN_SAVE)
        save_btn.clicked.connect(self.save_preferences)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        if parent:
            current_browser = getattr(parent, 'browser_preference', 'auto')
            browser_map = {
                'auto': 0,
                'none': 1,
                'firefox': 2,
                'chrome': 3,
                'brave': 4,
                'edge': 5,
                'chromium': 6,
                'opera': 7,
                'vivaldi': 8,
            }
            self.browser_combo.setCurrentIndex(browser_map.get(current_browser, 0))

    def save_preferences(self):
        """Save preferences and close dialog."""
        if self.parent_app:
            browser_text = self.browser_combo.currentText()
            if "Auto" in browser_text:
                preference = 'auto'
            elif "None" in browser_text:
                preference = 'none'
            else:
                preference = browser_text.lower()

            self.parent_app.browser_preference = preference
            save_browser_preference(preference)
        self.close()
