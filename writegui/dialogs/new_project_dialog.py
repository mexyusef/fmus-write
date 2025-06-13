"""
Dialog for creating a new project.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QDialogButtonBox,
    QGroupBox, QRadioButton, QTextEdit, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize

from writegui.controllers.app_controller import AppController


class NewProjectDialog(QDialog):
    """Dialog for creating a new project."""

    def __init__(self, parent=None, controller: AppController = None):
        """Initialize the dialog."""
        super().__init__(parent)

        self.setWindowTitle("Create New Project")
        self.resize(600, 600)  # Increased height for new field

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

        # Genre field with generate button
        genre_layout = QHBoxLayout()
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

        # Add generate button
        self.generate_button = QPushButton("Generate Idea")
        self.generate_button.setToolTip("Generate random title and description based on selected genre")
        self.generate_button.clicked.connect(self._on_generate_idea)

        # Add widgets to layout
        genre_layout.addWidget(self.genre_combo)
        genre_layout.addWidget(self.generate_button)
        details_layout.addRow("Genre:", genre_layout)

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

        # Story Description group
        story_group = QGroupBox("Story Description")
        story_layout = QVBoxLayout()

        # Description label
        description_label = QLabel(
            "Describe your story idea here. Include key elements like setting, main characters, "
            "or plot points you want to include. The AI will use this to guide the generation."
        )
        description_label.setWordWrap(True)
        story_layout.addWidget(description_label)

        # Story description text area
        self.story_description_edit = QTextEdit()
        self.story_description_edit.setPlaceholderText("Enter your story idea...")
        self.story_description_edit.setMinimumHeight(100)
        story_layout.addWidget(self.story_description_edit)

        # Set the story layout
        story_group.setLayout(story_layout)
        layout.addWidget(story_group)

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

    def get_story_description(self) -> str:
        """Get the story description."""
        return self.story_description_edit.toPlainText().strip()

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

    def _on_generate_idea(self):
        """Generate a random title and description based on the selected genre."""
        # Get the selected genre
        genre = self.genre_combo.currentText()

        # Check if a genre is selected
        if not genre:
            QMessageBox.warning(
                self,
                "Genre Required",
                "Please select a genre before generating an idea."
            )
            return

        # Show generating status
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")
        QApplication.processEvents()  # Update UI

        try:
            # Create prompt for the LLM
            prompt = f"""Generate a creative and original story idea for a {genre} story.

            Please provide:
            1. A catchy and unique title (maximum 10 words)
            2. A compelling story description (150-250 words) that includes:
               - The main character(s)
               - The setting
               - The central conflict or plot
               - Any unique elements or hooks

            Format your response exactly like this:
            TITLE: [Your title here]
            DESCRIPTION: [Your description here]

            Be creative and original. Avoid clichés and common tropes in the {genre} genre.
            """

            # Use the controller to query the LLM
            if self.controller:
                # Get current LLM settings
                provider = self.controller.settings_manager.get("llm_provider", "gemini")
                model = self.controller.settings_manager.get("model", "gemini-1.5-flash")
                temperature = self.controller.settings_manager.get("temperature", 0.7)

                # Query the LLM
                result = self.controller.query_llm(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    temperature=temperature
                )

                # Parse the result
                if result:
                    # Extract title and description
                    title = ""
                    description = ""

                    # Parse the response
                    lines = result.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("TITLE:"):
                            title = line[6:].strip()
                        elif line.startswith("DESCRIPTION:"):
                            # Get the description (could be multiple lines)
                            description_lines = []
                            j = i + 1
                            while j < len(lines) and not lines[j].startswith("TITLE:"):
                                description_lines.append(lines[j])
                                j += 1
                            description = "\n".join(description_lines).strip()

                    # If we couldn't parse properly, try a simpler approach
                    if not title or not description:
                        parts = result.split("DESCRIPTION:")
                        if len(parts) >= 2:
                            if "TITLE:" in parts[0]:
                                title = parts[0].replace("TITLE:", "").strip()
                            description = parts[1].strip()

                    # Update the UI with the generated content
                    if title:
                        self.title_edit.setText(title)
                    if description:
                        self.story_description_edit.setText(description)
                    else:
                        QMessageBox.warning(
                            self,
                            "Parsing Error",
                            "Generated content could not be parsed correctly. Please try again."
                        )
                else:
                    # Show a more detailed error message
                    QMessageBox.warning(
                        self,
                        "Generation Failed",
                        f"Failed to generate story idea using {provider} provider.\n\n"
                        f"Possible reasons:\n"
                        f"- API key for {provider} may be missing or invalid\n"
                        f"- Selected model ({model}) may not be available\n"
                        f"- Network connection issues\n\n"
                        f"You can change the LLM provider in Settings."
                    )
            else:
                QMessageBox.warning(self, "Error", "Controller not available for idea generation.")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()

            # Log the full error
            if self.controller and hasattr(self.controller, 'logger'):
                self.controller.logger.error(f"Error generating idea: {str(e)}")
                self.controller.logger.error(error_details)

            # Show a user-friendly error message
            QMessageBox.critical(
                self,
                "Error",
                f"Error generating idea: {str(e)}\n\n"
                f"Please check your network connection and LLM provider settings."
            )
        finally:
            # Reset button state
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Generate Idea")
