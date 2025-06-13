"""
Theme selection dialog for WriterGUI.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QGroupBox, QRadioButton,
    QButtonGroup, QFrame, QCheckBox
)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from ..utils.theme_manager import ThemeManager


class ColorPreview(QFrame):
    """A widget to preview theme colors."""

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")


class ThemeDialog(QDialog):
    """Dialog for selecting and customizing themes."""

    theme_selected = pyqtSignal(str)

    def __init__(self, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.resize(400, 300)
        self.theme_manager = ThemeManager()
        self.current_theme = current_theme

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Theme selection group
        theme_group = QGroupBox("Select Theme")
        theme_layout = QVBoxLayout()

        # Theme radio buttons
        self.theme_buttons = QButtonGroup(self)

        # Get available themes
        themes = self.theme_manager.get_available_themes()

        # Theme descriptions
        descriptions = {
            "dark": "Dark theme with deep blue accents",
            "light": "Light theme with blue accents",
            "sepia": "Warm sepia theme for comfortable reading",
            "blue": "Cool blue theme for professional work"
        }

        # Create a preview for each theme
        for i, theme in enumerate(themes):
            theme_row = QHBoxLayout()

            # Radio button
            radio = QRadioButton(theme.capitalize())
            radio.setChecked(theme == self.current_theme)
            self.theme_buttons.addButton(radio, i)
            theme_row.addWidget(radio)

            # Description
            if theme in descriptions:
                desc = QLabel(descriptions[theme])
                desc.setStyleSheet("color: #666; font-style: italic;")
                theme_row.addWidget(desc)

            # Add to layout
            theme_layout.addLayout(theme_row)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QHBoxLayout()

        # Create color previews for the selected theme
        self.preview_frames = []

        # Add color previews
        colors = self._get_theme_colors(self.current_theme)
        for color in colors:
            preview = ColorPreview(color)
            preview_layout.addWidget(preview)
            self.preview_frames.append(preview)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Remember preference checkbox
        self.remember_checkbox = QCheckBox("Remember as default theme")
        self.remember_checkbox.setChecked(True)
        layout.addWidget(self.remember_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._on_apply)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Connect signals
        self.theme_buttons.buttonClicked.connect(self._on_theme_selected)

        self.setLayout(layout)

    def _on_theme_selected(self, button):
        """Handle theme selection."""
        theme_name = button.text().lower()
        self._update_preview(theme_name)

    def _update_preview(self, theme_name):
        """Update the color preview based on the selected theme."""
        colors = self._get_theme_colors(theme_name)

        # Update preview frames
        for i, frame in enumerate(self.preview_frames):
            if i < len(colors):
                frame.setStyleSheet(f"background-color: {colors[i]}; border: 1px solid #888;")

    def _get_theme_colors(self, theme_name):
        """Get representative colors for a theme."""
        if theme_name == "dark":
            return ["#121212", "#1a237e", "#00bfa5", "#0091ea", "#e0e0e0"]
        elif theme_name == "light":
            return ["#f0f0f0", "#e1f5fe", "#00897b", "#03a9f4", "#333333"]
        elif theme_name == "sepia":
            return ["#f9f1e4", "#f5ebe0", "#c17d11", "#5b3c11", "#d8c3a5"]
        elif theme_name == "blue":
            return ["#ebf5fb", "#f5fafd", "#2979ff", "#1e375a", "#c5d9e8"]
        else:
            return ["#ffffff", "#eeeeee", "#cccccc", "#999999", "#666666"]

    def _on_apply(self):
        """Apply the selected theme."""
        selected_button = self.theme_buttons.checkedButton()
        if selected_button:
            theme_name = selected_button.text().lower()

            # The parent window will handle saving to settings if remember checkbox is checked
            self.theme_selected.emit(theme_name)
            self.accept()
        else:
            self.reject()

    def is_remember_checked(self):
        """Return whether the remember checkbox is checked."""
        return self.remember_checkbox.isChecked()
