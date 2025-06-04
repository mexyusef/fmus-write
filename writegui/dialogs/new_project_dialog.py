"""
Dialog for creating a new project.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QDialogButtonBox,
    QGroupBox, QRadioButton, QTextEdit
)
from PyQt6.QtCore import Qt, QSize

from writegui.controllers.app_controller import AppController


class NewProjectDialog(QDialog):
    """Dialog for creating a new project."""

    def __init__(self, parent=None, controller: AppController = None):
        """Initialize the dialog."""
        super().__init__(parent)

        self.setWindowTitle("Create New Project")
        self.resize(600, 500)

        self.controller = controller

        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI."""
        # Main layout
        layout = QVBoxLayout(self)

        # Project details group
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout()

        # Title field
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter project title")
        details_layout.addRow("Title:", self.title_edit)

        # Genre field
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setPlaceholderText("Select or enter genre")

        # Load genres from configuration if controller is available
        if self.controller:
            self.genre_combo.addItems(self.controller.get_available_genres())
        else:
            self.genre_combo.addItems([
                "Fantasy", "Science Fiction", "Mystery", "Thriller",
                "Romance", "Historical Fiction", "Literary Fiction",
                "Horror", "Western", "Young Adult", "Children's"
            ])

        details_layout.addRow("Genre:", self.genre_combo)

        # Genre description (shows when a genre is selected)
        self.genre_description = QTextEdit()
        self.genre_description.setReadOnly(True)
        self.genre_description.setMaximumHeight(80)
        details_layout.addRow("Genre Description:", self.genre_description)

        # Connect the genre combo to update the description
        self.genre_combo.currentTextChanged.connect(self._update_genre_description)

        # Author field
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter author name")
        details_layout.addRow("Author:", self.author_edit)

        # Set the details layout
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Structure group
        structure_group = QGroupBox("Project Structure")
        structure_layout = QVBoxLayout()

        # Structure combo
        self.structure_combo = QComboBox()

        # Load structures from configuration if controller is available
        if self.controller:
            self.structure_combo.addItems(self.controller.get_available_structures())
        else:
            self.structure_combo.addItems(["novel", "novella", "short_story"])

        structure_layout.addWidget(self.structure_combo)

        # Structure description
        self.structure_description = QTextEdit()
        self.structure_description.setReadOnly(True)
        self.structure_description.setMaximumHeight(80)
        structure_layout.addWidget(self.structure_description)

        # Connect the structure combo to update the description
        self.structure_combo.currentTextChanged.connect(self._update_structure_description)

        # Set the structure layout
        structure_group.setLayout(structure_layout)
        layout.addWidget(structure_group)

        # Template group
        template_group = QGroupBox("Template")
        template_layout = QVBoxLayout()

        # Template combo
        self.template_combo = QComboBox()

        # Load templates from configuration if controller is available
        if self.controller:
            self.template_combo.addItems(self.controller.get_available_templates())
        else:
            self.template_combo.addItems([
                "Blank Project",
                "Three-Act Structure",
                "Hero's Journey",
                "Save the Cat"
            ])

        template_layout.addWidget(self.template_combo)

        # Template description
        self.template_description = QTextEdit()
        self.template_description.setReadOnly(True)
        self.template_description.setMaximumHeight(80)
        template_layout.addWidget(self.template_description)

        # Connect the template combo to update the description
        self.template_combo.currentTextChanged.connect(self._update_template_description)

        # Set the template layout
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initialize descriptions
        self._update_genre_description(self.genre_combo.currentText())
        self._update_structure_description(self.structure_combo.currentText())
        self._update_template_description(self.template_combo.currentText())

    def _update_genre_description(self, genre: str) -> None:
        """Update the genre description when a genre is selected."""
        if not self.controller or not genre:
            self.genre_description.clear()
            return

        genre_info = self.controller.get_genre_info(genre)
        if genre_info:
            description = genre_info.get('description', '')
            elements = genre_info.get('common_elements', [])

            text = f"{description}\n\nCommon elements: {', '.join(elements)}"
            self.genre_description.setText(text)
        else:
            self.genre_description.clear()

    def _update_structure_description(self, structure: str) -> None:
        """Update the structure description when a structure is selected."""
        if not self.controller or not structure:
            self.structure_description.clear()
            return

        structure_info = self.controller.get_structure_info(structure)
        if structure_info:
            description = structure_info.get('description', '')
            word_count = structure_info.get('word_count_range', [0, 0])
            chapters = structure_info.get('default_chapters', 0)

            text = f"{description}\n\nTypical word count: {word_count[0]} - {word_count[1]}\nDefault chapters: {chapters}"
            self.structure_description.setText(text)
        else:
            self.structure_description.clear()

    def _update_template_description(self, template: str) -> None:
        """Update the template description when a template is selected."""
        if not self.controller or not template:
            self.template_description.clear()
            return

        template_info = self.controller.get_template_info(template)
        if template_info:
            description = template_info.get('description', '')
            components = template_info.get('components', [])

            text = f"{description}\n\nComponents: {', '.join(components)}"
            self.template_description.setText(text)
        else:
            self.template_description.clear()

    def get_title(self) -> str:
        """Get the project title."""
        return self.title_edit.text().strip()

    def get_genre(self) -> str:
        """Get the project genre."""
        return self.genre_combo.currentText().strip()

    def get_author(self) -> str:
        """Get the author name."""
        return self.author_edit.text().strip()

    def get_structure_type(self) -> str:
        """Get the selected structure type."""
        return self.structure_combo.currentText().strip()

    def get_template(self) -> str:
        """Get the selected template."""
        return self.template_combo.currentText()

    def accept(self):
        """Override accept to validate input."""
        if not self.get_title():
            # Show error or handle empty title
            self.title_edit.setFocus()
            return

        # Call the parent accept method
        super().accept()
