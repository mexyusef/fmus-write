"""
Progress visualization widget for WriterGUI.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


class ProgressStep(QFrame):
    """Widget representing a single step in a multi-step process."""

    def __init__(self, step_name, parent=None):
        super().__init__(parent)
        self.step_name = step_name
        self.is_active = False
        self.is_completed = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Step label
        self.label = QLabel(self.step_name)
        layout.addWidget(self.label)

        # Status indicator
        self.status = QLabel("⬜")  # Empty square
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 4px;")

    def set_active(self, active=True):
        """Set this step as the active step."""
        self.is_active = active
        if active:
            self.status.setText("🔄")  # Processing
            self.setStyleSheet("background-color: #e3f2fd; border-radius: 4px; border: 1px solid #2196f3;")
        else:
            if self.is_completed:
                self.status.setText("✅")  # Completed
                self.setStyleSheet("background-color: #e8f5e9; border-radius: 4px; border: 1px solid #4caf50;")
            else:
                self.status.setText("⬜")  # Empty square
                self.setStyleSheet("background-color: #f0f0f0; border-radius: 4px;")

    def set_completed(self, completed=True):
        """Mark this step as completed."""
        self.is_completed = completed
        if completed:
            self.is_active = False
            self.status.setText("✅")  # Completed
            self.setStyleSheet("background-color: #e8f5e9; border-radius: 4px; border: 1px solid #4caf50;")
        else:
            self.status.setText("⬜")  # Empty square
            self.setStyleSheet("background-color: #f0f0f0; border-radius: 4px;")


class ProgressWidget(QWidget):
    """Widget for visualizing progress of multi-step processes."""

    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps = []
        self.current_step_index = -1
        self.is_running = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Generation Progress")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status message
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Steps container
        self.steps_layout = QVBoxLayout()
        layout.addLayout(self.steps_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        self.cancel_button.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_steps(self, step_names):
        """Set the steps to display."""
        # Clear existing steps
        for i in reversed(range(self.steps_layout.count())):
            self.steps_layout.itemAt(i).widget().setParent(None)

        self.steps = []
        self.current_step_index = -1

        # Add new steps
        for name in step_names:
            step = ProgressStep(name)
            self.steps.append(step)
            self.steps_layout.addWidget(step)

    def start_process(self):
        """Start the progress visualization."""
        self.is_running = True
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting...")

        # Reset all steps
        for step in self.steps:
            step.set_active(False)
            step.set_completed(False)

        # Move to first step
        self.advance_to_step(0)

    def advance_to_step(self, step_index):
        """Advance to the specified step."""
        if step_index < 0 or step_index >= len(self.steps):
            return

        # Mark previous step as completed if moving forward
        if step_index > self.current_step_index and self.current_step_index >= 0:
            self.steps[self.current_step_index].set_completed(True)

        # Update current step
        self.current_step_index = step_index

        # Update progress bar
        progress = int((step_index / len(self.steps)) * 100)
        self.progress_bar.setValue(progress)

        # Update step status
        for i, step in enumerate(self.steps):
            if i < step_index:
                step.set_completed(True)
                step.set_active(False)
            elif i == step_index:
                step.set_active(True)
            else:
                step.set_active(False)
                step.set_completed(False)

        # Update status message
        self.status_label.setText(f"Processing: {self.steps[step_index].step_name}")

    def set_step_progress(self, progress):
        """Set the progress within the current step (0-100)."""
        if self.current_step_index < 0:
            return

        # Calculate overall progress
        step_size = 100 / len(self.steps)
        base_progress = (self.current_step_index / len(self.steps)) * 100
        step_progress = (progress / 100) * step_size

        total_progress = int(base_progress + step_progress)
        self.progress_bar.setValue(total_progress)

    def complete_process(self):
        """Mark the process as completed."""
        # Mark all steps as completed
        for step in self.steps:
            step.set_completed(True)

        self.progress_bar.setValue(100)
        self.status_label.setText("Process completed successfully")
        self.is_running = False
        self.cancel_button.setEnabled(False)

    def fail_process(self, message="Process failed"):
        """Mark the process as failed."""
        self.status_label.setText(message)
        self.is_running = False
        self.cancel_button.setEnabled(False)

    def _on_cancel(self):
        """Handle cancel button click."""
        if self.is_running:
            self.is_running = False
            self.status_label.setText("Cancelling...")
            self.cancelled.emit()
            self.cancel_button.setEnabled(False)
