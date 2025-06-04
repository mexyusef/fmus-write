"""
Dialog for refining generated content.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QFormLayout, QGroupBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt


class RefineContentDialog(QDialog):
    """Dialog for refining content with LLM assistance."""

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)

        self.setWindowTitle("Refine Content")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Add instructions
        instructions = QLabel(
            "Provide instructions on how you'd like to refine the generated content. "
            "Select what aspect to focus on and provide details in the text area below."
        )
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions)

        # Refinement options
        options_group = QGroupBox("Refinement Options")
        options_layout = QFormLayout()

        # Target selection
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Entire Content", "Selected Chapter", "Current Scene"])
        options_layout.addRow("Target:", self.target_combo)

        # Aspect selection
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems([
            "Overall Quality",
            "Plot/Structure",
            "Character Development",
            "Dialogue",
            "Descriptions",
            "Language/Style",
            "Pacing",
            "Theme/Tone"
        ])
        options_layout.addRow("Aspect to Refine:", self.aspect_combo)

        # Direction selection
        self.direction_combo = QComboBox()
        self.direction_combo.addItems([
            "Expand/Elaborate",
            "Condense/Simplify",
            "Improve/Enhance",
            "Rewrite Completely",
            "Add More Details",
            "Make More Consistent"
        ])
        options_layout.addRow("Direction:", self.direction_combo)

        options_group.setLayout(options_layout)
        self.layout.addWidget(options_group)

        # Detailed instructions
        instructions_label = QLabel("Detailed Instructions:")
        self.layout.addWidget(instructions_label)

        self.instructions_text = QTextEdit()
        self.instructions_text.setPlaceholderText(
            "Enter specific details about what you want to change or improve. "
            "For example: 'Make the dialogue more natural' or 'Add more descriptive details about the setting'."
        )
        self.layout.addWidget(self.instructions_text)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def get_target(self) -> str:
        """Get the selected target."""
        return self.target_combo.currentText()

    def get_aspect(self) -> str:
        """Get the selected aspect to refine."""
        return self.aspect_combo.currentText()

    def get_direction(self) -> str:
        """Get the selected refinement direction."""
        return self.direction_combo.currentText()

    def get_instructions(self) -> str:
        """Get the detailed instructions."""
        return self.instructions_text.toPlainText()

    def get_refinement_prompt(self) -> str:
        """Get a formatted refinement prompt based on user selections."""
        target = self.get_target()
        aspect = self.get_aspect()
        direction = self.get_direction()
        instructions = self.get_instructions()

        prompt = f"Please {direction.lower()} the {aspect.lower()} of the {target.lower()}."

        if instructions:
            prompt += f"\n\nSpecific instructions: {instructions}"

        return prompt
