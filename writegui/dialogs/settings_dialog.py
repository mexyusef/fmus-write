"""
Settings dialog for WriterGUI.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QTabWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QLineEdit,
    QCheckBox, QSlider, QListWidget, QListWidgetItem,
    QStackedWidget, QScrollArea, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from ..utils.settings_manager import SettingsManager
from ..utils.theme_manager import ThemeManager


class SettingsDialog(QDialog):
    """Dialog for managing application settings."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(600, 450)
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()
        
        self._init_ui()
        self._load_settings()
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([t.capitalize() for t in self.theme_manager.get_available_themes()])
        general_layout.addRow("Theme:", self.theme_combo)
        
        # Autosave interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(0, 60)
        self.autosave_spin.setSuffix(" minutes")
        self.autosave_spin.setSpecialValueText("Disabled")
        general_layout.addRow("Autosave Interval:", self.autosave_spin)
        
        # Max recent projects
        self.recent_projects_spin = QSpinBox()
        self.recent_projects_spin.setRange(0, 20)
        self.recent_projects_spin.setSpecialValueText("Disabled")
        general_layout.addRow("Max Recent Projects:", self.recent_projects_spin)
        
        general_tab.setLayout(general_layout)
        self.tab_widget.addTab(general_tab, "General")
        
        # Editor settings tab
        editor_tab = QWidget()
        editor_layout = QFormLayout()
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        editor_layout.addRow("Font Size:", self.font_size_spin)
        
        # Line spacing
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems(["Single", "1.15", "1.5", "Double"])
        editor_layout.addRow("Line Spacing:", self.line_spacing_combo)
        
        # Show line numbers
        self.line_numbers_check = QCheckBox("Show Line Numbers")
        editor_layout.addRow("", self.line_numbers_check)
        
        # Word wrap
        self.word_wrap_check = QCheckBox("Word Wrap")
        editor_layout.addRow("", self.word_wrap_check)
        
        editor_tab.setLayout(editor_layout)
        self.tab_widget.addTab(editor_tab, "Editor")
        
        # LLM settings tab
        llm_tab = QWidget()
        llm_layout = QFormLayout()
        
        # LLM provider
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Gemini", "Anthropic", "Local"])
        llm_layout.addRow("LLM Provider:", self.provider_combo)
        
        # Model selection
        self.model_combo = QComboBox()
        llm_layout.addRow("Model:", self.model_combo)
        
        # Temperature
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 1.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(1)
        llm_layout.addRow("Temperature:", self.temperature_spin)
        
        # API key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter API key")
        llm_layout.addRow("API Key:", self.api_key_edit)
        
        llm_tab.setLayout(llm_layout)
        self.tab_widget.addTab(llm_tab, "AI Model")
        
        # Export settings tab
        export_tab = QWidget()
        export_layout = QFormLayout()
        
        # Default export format
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Markdown", "HTML", "PDF", "EPUB", "DOCX", "TXT"])
        export_layout.addRow("Default Format:", self.export_format_combo)
        
        # Include metadata
        self.include_metadata_check = QCheckBox("Include Metadata")
        export_layout.addRow("", self.include_metadata_check)
        
        # Include table of contents
        self.include_toc_check = QCheckBox("Include Table of Contents")
        export_layout.addRow("", self.include_toc_check)
        
        export_tab.setLayout(export_layout)
        self.tab_widget.addTab(export_tab, "Export")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.provider_combo.currentTextChanged.connect(self._update_model_list)
        
        self.setLayout(layout)
        
    def _load_settings(self):
        """Load settings from the settings manager."""
        # General settings
        theme = self.settings_manager.get("theme", "dark")
        theme_index = self.theme_combo.findText(theme.capitalize())
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
            
        self.autosave_spin.setValue(self.settings_manager.get("autosave_interval", 5))
        self.recent_projects_spin.setValue(self.settings_manager.get("max_recent_projects", 10))
        
        # Editor settings
        self.font_size_spin.setValue(self.settings_manager.get("editor.font_size", 12))
        
        line_spacing = self.settings_manager.get("editor.line_spacing", "1.15")
        line_spacing_index = self.line_spacing_combo.findText(line_spacing)
        if line_spacing_index >= 0:
            self.line_spacing_combo.setCurrentIndex(line_spacing_index)
            
        self.line_numbers_check.setChecked(self.settings_manager.get("editor.show_line_numbers", True))
        self.word_wrap_check.setChecked(self.settings_manager.get("editor.word_wrap", True))
        
        # LLM settings
        provider = self.settings_manager.get("llm_provider", "openai").capitalize()
        provider_index = self.provider_combo.findText(provider)
        if provider_index >= 0:
            self.provider_combo.setCurrentIndex(provider_index)
            
        self._update_model_list()
        
        model = self.settings_manager.get("model", "")
        model_index = self.model_combo.findText(model)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)
            
        self.temperature_spin.setValue(self.settings_manager.get("temperature", 0.7))
        self.api_key_edit.setText(self.settings_manager.get("api_key", ""))
        
        # Export settings
        export_format = self.settings_manager.get("default_export_format", "markdown").capitalize()
        format_index = self.export_format_combo.findText(export_format)
        if format_index >= 0:
            self.export_format_combo.setCurrentIndex(format_index)
            
        self.include_metadata_check.setChecked(self.settings_manager.get("export.include_metadata", True))
        self.include_toc_check.setChecked(self.settings_manager.get("export.include_toc", True))
        
    def _update_model_list(self):
        """Update the model list based on the selected provider."""
        self.model_combo.clear()
        provider = self.provider_combo.currentText().lower()
        
        if provider == "openai":
            self.model_combo.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"])
        elif provider == "gemini":
            self.model_combo.addItems(["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"])
        elif provider == "anthropic":
            self.model_combo.addItems(["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"])
        elif provider == "local":
            self.model_combo.addItems(["llama-3-8b", "llama-3-70b", "mistral-7b", "mixtral-8x7b"])
        
    def _on_save(self):
        """Save settings and close the dialog."""
        # General settings
        self.settings_manager.set("theme", self.theme_combo.currentText().lower())
        self.settings_manager.set("autosave_interval", self.autosave_spin.value())
        self.settings_manager.set("max_recent_projects", self.recent_projects_spin.value())
        
        # Editor settings
        self.settings_manager.set("editor.font_size", self.font_size_spin.value())
        self.settings_manager.set("editor.line_spacing", self.line_spacing_combo.currentText())
        self.settings_manager.set("editor.show_line_numbers", self.line_numbers_check.isChecked())
        self.settings_manager.set("editor.word_wrap", self.word_wrap_check.isChecked())
        
        # LLM settings
        self.settings_manager.set("llm_provider", self.provider_combo.currentText().lower())
        self.settings_manager.set("model", self.model_combo.currentText())
        self.settings_manager.set("temperature", self.temperature_spin.value())
        self.settings_manager.set("api_key", self.api_key_edit.text())
        
        # Export settings
        self.settings_manager.set("default_export_format", self.export_format_combo.currentText().lower())
        self.settings_manager.set("export.include_metadata", self.include_metadata_check.isChecked())
        self.settings_manager.set("export.include_toc", self.include_toc_check.isChecked())
        
        # Emit signal
        self.settings_changed.emit()
        
        # Close dialog
        self.accept() 