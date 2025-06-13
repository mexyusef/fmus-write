"""
Properties panel widget for the WriterGUI application.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QGroupBox, QFormLayout, QTabWidget,
    QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from writegui.controllers.app_controller import AppController


class PropertiesPanel(QWidget):
    """Panel for displaying and editing properties."""

    def __init__(self, controller: AppController, parent=None):
        """Initialize the properties panel."""
        super().__init__(parent)
        self.controller = controller

        # Set up the layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create a container widget for the scroll area
        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)

        # Setup initial widgets
        self._setup_project_properties()
        self._setup_story_description()
        self._setup_generation_properties()

        # Add stretch to push widgets to the top
        self.scroll_layout.addStretch()

        # Set the container as the scroll area's widget
        scroll_area.setWidget(self.container)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(scroll_area)

        # Available models for each provider
        self.provider_models = {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "gemini": ["gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash-exp"],
            "ollama": ["llama3", "mistral", "phi3"]
        }

        # Connect the provider combo box to update models
        self.provider_combo.currentTextChanged.connect(self._update_model_dropdown)

        # Initialize the model dropdown with default provider models
        self._update_model_dropdown(self.provider_combo.currentText())

        # Refresh the UI
        self.refresh()

    def refresh(self):
        """Refresh the panel with current data."""
        # Update project properties if a project is open
        if self.controller.current_project:
            self.project_group.setEnabled(True)
            self.story_description_group.setEnabled(True)

            self.title_edit.setText(self.controller.current_project.title)
            self.genre_edit.setText(self.controller.current_project.genre)

            # Set author if available
            if hasattr(self.controller.current_project, 'author'):
                self.author_edit.setText(self.controller.current_project.author)

            # Set story description if available
            if hasattr(self.controller.current_project, 'story_description'):
                self.story_description_text.setText(self.controller.current_project.story_description)

            # Enable generation properties
            self.generation_group.setEnabled(True)

            # Update generation settings
            settings = self.controller.get_settings()
            provider = settings.get('llm_provider', 'openai').lower()

            # Set provider and update models
            index = self.provider_combo.findText(provider, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)

            # This will trigger _update_model_dropdown which will set the model

            # Set temperature
            self.temperature_spinbox.setValue(settings.get('temperature', 0.7))

            # Set style if available
            style = settings.get('style', 'Descriptive')
            index = self.style_combo.findText(style, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.style_combo.setCurrentIndex(index)

            # Set themes if available
            themes = settings.get('themes', [])
            self.adventure_check.setChecked('adventure' in themes)
            self.romance_check.setChecked('romance' in themes)
            self.mystery_check.setChecked('mystery' in themes)
        else:
            # Disable all groups if no project is open
            self.project_group.setEnabled(False)
            self.story_description_group.setEnabled(False)
            self.generation_group.setEnabled(False)

            # Clear fields
            self.title_edit.clear()
            self.genre_edit.clear()
            self.author_edit.clear()
            self.story_description_text.clear()

    def _setup_project_properties(self):
        """Set up the project properties group."""
        self.project_group = QGroupBox("Project Properties")
        project_layout = QFormLayout()

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter project title")
        self.title_edit.textChanged.connect(self._on_title_changed)
        project_layout.addRow("Title:", self.title_edit)

        # Genre
        self.genre_edit = QLineEdit()
        self.genre_edit.setPlaceholderText("Enter project genre")
        self.genre_edit.textChanged.connect(self._on_genre_changed)
        project_layout.addRow("Genre:", self.genre_edit)

        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter author name")
        project_layout.addRow("Author:", self.author_edit)

        # Word count target
        self.word_count_spinbox = QSpinBox()
        self.word_count_spinbox.setRange(1000, 200000)
        self.word_count_spinbox.setSingleStep(1000)
        self.word_count_spinbox.setValue(50000)
        project_layout.addRow("Word Count Target:", self.word_count_spinbox)

        # Chapter count target
        self.chapter_count_spinbox = QSpinBox()
        self.chapter_count_spinbox.setRange(1, 100)
        self.chapter_count_spinbox.setValue(12)
        project_layout.addRow("Chapter Count:", self.chapter_count_spinbox)

        # Apply button
        self.apply_project_button = QPushButton("Apply Changes")
        self.apply_project_button.clicked.connect(self._on_apply_project)
        project_layout.addRow(self.apply_project_button)

        self.project_group.setLayout(project_layout)
        self.scroll_layout.addWidget(self.project_group)

    def _setup_story_description(self):
        """Set up the story description group."""
        self.story_description_group = QGroupBox("Story Description")
        story_layout = QVBoxLayout()

        # Description label
        description_label = QLabel(
            "Describe your story idea here. Include key elements like setting, main characters, "
            "or plot points you want to include. The AI will use this to guide the generation."
        )
        description_label.setWordWrap(True)
        story_layout.addWidget(description_label)

        # Story description text area
        self.story_description_text = QTextEdit()
        self.story_description_text.setMinimumHeight(100)
        story_layout.addWidget(self.story_description_text)

        # Advanced planning button
        self.advanced_planning_button = QPushButton("Advanced Planning...")
        self.advanced_planning_button.clicked.connect(self._show_advanced_planning)
        story_layout.addWidget(self.advanced_planning_button)

        self.story_description_group.setLayout(story_layout)
        self.scroll_layout.addWidget(self.story_description_group)

    def _setup_generation_properties(self):
        """Set up the generation properties group."""
        self.generation_group = QGroupBox("Generation Properties")
        generation_layout = QFormLayout()

        # LLM Provider
        self.provider_combo = QComboBox()
        # Available providers
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Gemini", "Ollama"])
        self.provider_combo.currentTextChanged.connect(self._update_model_dropdown)
        generation_layout.addRow("LLM Provider:", self.provider_combo)

        # Model
        self.model_combo = QComboBox()
        generation_layout.addRow("Model:", self.model_combo)

        # Temperature
        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.1, 2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        self.temperature_spinbox.setValue(0.7)
        generation_layout.addRow("Temperature:", self.temperature_spinbox)

        # Style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Descriptive", "Concise", "Formal", "Casual", "Poetic"])
        generation_layout.addRow("Style:", self.style_combo)

        # Themes
        themes_layout = QHBoxLayout()

        self.adventure_check = QCheckBox("Adventure")
        themes_layout.addWidget(self.adventure_check)

        self.romance_check = QCheckBox("Romance")
        themes_layout.addWidget(self.romance_check)

        self.mystery_check = QCheckBox("Mystery")
        themes_layout.addWidget(self.mystery_check)

        generation_layout.addRow("Themes:", themes_layout)

        # Apply button
        self.apply_generation_button = QPushButton("Apply Settings")
        self.apply_generation_button.clicked.connect(self._on_apply_generation)
        generation_layout.addRow(self.apply_generation_button)

        self.generation_group.setLayout(generation_layout)
        self.scroll_layout.addWidget(self.generation_group)

    def _on_title_changed(self, text):
        """Handle title changes."""
        # This is for immediate feedback only
        # Actual update happens when Apply is clicked
        pass

    def _on_genre_changed(self, text):
        """Handle genre changes."""
        # This is for immediate feedback only
        # Actual update happens when Apply is clicked
        pass

    def _update_model_dropdown(self, provider_text):
        """Update the model dropdown based on the selected provider."""
        self.model_combo.clear()

        provider = provider_text.lower()

        # Get models for the selected provider
        models = self.provider_models.get(provider, [])

        if models:
            self.model_combo.addItems(models)

            # Try to select the current model from settings
            settings = self.controller.get_settings()
            current_model = settings.get('model', '')

            # Try to find and select the current model
            index = self.model_combo.findText(current_model, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                # Select the first model if current not found
                self.model_combo.setCurrentIndex(0)
        else:
            self.model_combo.addItem("No models available")

    def _show_advanced_planning(self):
        """Show the advanced planning dialog."""
        # This will be implemented later when we create the StoryPlanningDialog
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Advanced Planning",
            "Advanced planning interface will be implemented in a future update.\n\n"
            "For now, please use the story description text area to describe your story."
        )

    def _on_apply_project(self):
        """Apply project property changes."""
        if not self.controller.current_project:
            return

        # Update project properties
        self.controller.current_project.title = self.title_edit.text()
        self.controller.current_project.genre = self.genre_edit.text()
        self.controller.current_project.author = self.author_edit.text()
        self.controller.current_project.story_description = self.story_description_text.toPlainText()
        self.controller.current_project.word_count_target = self.word_count_spinbox.value()
        self.controller.current_project.chapter_count = self.chapter_count_spinbox.value()

        # Save the project
        self.controller.save_project()

        # Update UI elements that might display project info
        self.controller.update_ui()

    def _on_apply_generation(self):
        """Apply generation settings."""
        if not self.controller.current_project:
            return

        # Collect values from form
        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText()
        temperature = self.temperature_spinbox.value()
        style = self.style_combo.currentText()

        # Collect themes
        themes = []
        if self.adventure_check.isChecked():
            themes.append("adventure")
        if self.romance_check.isChecked():
            themes.append("romance")
        if self.mystery_check.isChecked():
            themes.append("mystery")

        # Create settings dictionary
        generation_settings = {
            "llm_provider": provider,
            "model": model,
            "temperature": temperature,
            "style": style,
            "themes": themes
        }

        # Update settings in controller
        self.controller.update_settings(generation_settings)

        # If the project has a configure method, call it with generation settings
        if hasattr(self.controller.current_project, 'configure'):
            self.controller.current_project.configure(**generation_settings)

        # Show confirmation in status bar if available
        main_window = self.window()
        if hasattr(main_window, 'status_label'):
            main_window.status_label.setText("Generation settings updated")
