"""
Editor tab widget for the WriterGUI application.
"""
import logging
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QPlainTextEdit, QSplitter, QTextEdit, QMessageBox, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from writegui.controllers.app_controller import AppController
from writegui.ui.content_viewers import ContentViewerFactory

# Set up logging
logger = logging.getLogger("WriterGUI.EditorTab")

class EditorTabWidget(QTabWidget):
    """Tab widget for editing content."""

    def __init__(self, controller: AppController, parent=None):
        """Initialize the editor tab widget."""
        super().__init__(parent)
        self.controller = controller

        # Set up tab appearance
        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)

        # Set up initial tabs
        self._setup_initial_tabs()

        # Track open content tabs
        self.content_tabs = {}  # {content_id: tab_index}

        logger.debug("EditorTabWidget initialized")

    def _setup_initial_tabs(self):
        """Set up the initial tabs."""
        # Welcome tab
        self._add_welcome_tab()

        # If a project is already open, add project tabs
        if self.controller.current_project:
            self._add_project_tabs()

        logger.debug(f"Initial tabs created: {self.count()} tabs")

    def _add_welcome_tab(self):
        """Add the welcome tab."""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)

        # Welcome message
        welcome_label = QLabel("Welcome to WriterGUI")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        # Instructions
        instructions = QLabel(
            "Create a new project using File > New Project or open an existing project using File > Open Project."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        welcome_layout.addWidget(instructions)

        # Add the tab
        self.addTab(welcome_widget, "Welcome")
        logger.debug("Welcome tab created")

    def _add_project_tabs(self):
        """Add tabs for the current project."""
        if not self.controller.current_project:
            return

        logger.debug(f"Adding tabs for project: {self.controller.current_project.title}")

        # Outline tab
        self._add_outline_tab()

        # Check if we have chapters to display
        if hasattr(self.controller.current_project, 'chapters') and self.controller.current_project.chapters:
            chapters = self.controller.current_project.chapters
            logger.debug(f"Found {len(chapters)} chapters to display")
            for i, chapter in enumerate(chapters):
                self._add_chapter_tab(i, chapter)
        else:
            logger.debug("No chapters found in project")

        logger.debug(f"Project tabs created: {self.count() - 1} project-related tabs")

    def _add_outline_tab(self):
        """Add the outline tab."""
        editor = QTextEdit()
        editor.setReadOnly(True)

        # Try to get outline data
        if hasattr(self.controller.current_project, 'outline'):
            outline = self.controller.current_project.outline
            if outline:
                logger.debug(f"Found outline data: {type(outline)}")

                content = []
                # Add title
                content.append(f"# {self.controller.current_project.title} - Outline\n")

                # Format based on outline type
                if isinstance(outline, dict):
                    # Handle dictionary format
                    if 'premise' in outline:
                        content.append(f"## Premise\n{outline['premise']}\n")

                    if 'theme' in outline:
                        content.append(f"## Theme\n{outline['theme']}\n")

                    if 'sections' in outline and isinstance(outline['sections'], list):
                        content.append("## Sections\n")
                        for i, section in enumerate(outline['sections']):
                            if isinstance(section, dict):
                                title = section.get('title', f"Section {i+1}")
                                description = section.get('description', '')
                                content.append(f"### {title}\n{description}\n")

                                # Add events if available
                                events = section.get('events', [])
                                if events:
                                    content.append("#### Events")
                                    for event in events:
                                        content.append(f"- {event}")
                                    content.append("")
                elif isinstance(outline, str):
                    # Handle string format
                    content.append(outline)
                else:
                    # Unknown format
                    content.append(f"Outline data is in an unexpected format: {type(outline)}")

                editor.setMarkdown("\n".join(content))
            else:
                editor.setPlainText("No outline data available.")
        else:
            logger.debug("No outline data found in project")
            editor.setPlainText("No outline has been generated yet. Use the Generate menu to create an outline.")

        # Add the tab
        self.addTab(editor, "Outline")

    def _add_chapter_tab(self, index, chapter):
        """Add a tab for a chapter."""
        editor = QTextEdit()
        editor.setReadOnly(True)

        # Format the chapter content
        if isinstance(chapter, dict):
            title = chapter.get('title', f"Chapter {index+1}")
            content = chapter.get('content', '')

            if content:
                logger.debug(f"Adding chapter tab: {title} ({len(content)} characters)")
                editor.setMarkdown(f"# {title}\n\n{content}")
            else:
                logger.debug(f"Adding empty chapter tab: {title}")
                editor.setPlainText(f"# {title}\n\nNo content has been generated for this chapter yet.")
        else:
            logger.debug(f"Chapter {index+1} has unexpected format: {type(chapter)}")
            editor.setPlainText(f"Chapter {index+1} data is not in the expected format.")

        # Add the tab
        self.addTab(editor, f"Chapter {index+1}")

    def refresh(self):
        """Refresh the tabs with current data."""
        logger.debug("Refreshing editor tabs")

        # Remember the current tab
        current_index = self.currentIndex()

        # Clear all tabs
        while self.count() > 0:
            self.removeTab(0)

        # Reset content tabs tracking
        self.content_tabs = {}

        # Setup tabs again
        self._setup_initial_tabs()

        # Restore current tab if possible
        if current_index < self.count():
            self.setCurrentIndex(current_index)

        logger.debug(f"Tabs refreshed: {self.count()} tabs")

    def next_tab(self):
        """Switch to the next tab."""
        count = self.count()
        if count > 1:
            current = self.currentIndex()
            self.setCurrentIndex((current + 1) % count)

    def previous_tab(self):
        """Switch to the previous tab."""
        count = self.count()
        if count > 1:
            current = self.currentIndex()
            self.setCurrentIndex((current - 1) % count)

    def close_tab(self, index):
        """Close the tab at the given index."""
        # Don't close the last tab
        if self.count() > 1:
            # Get the widget to check if it's a content tab
            widget = self.widget(index)

            # Update content_tabs tracking if this was a content tab
            content_id = None
            for cid, tab_idx in list(self.content_tabs.items()):
                if tab_idx == index:
                    content_id = cid
                    break

            if content_id:
                del self.content_tabs[content_id]

                # Adjust indices for tabs that come after the closed tab
                for cid, tab_idx in self.content_tabs.items():
                    if tab_idx > index:
                        self.content_tabs[cid] = tab_idx - 1

            # Remove the tab
            self.removeTab(index)

        logger.debug(f"Tab closed, remaining tabs: {self.count()}")

    def open_content_tab(self, content_type: str, content: object):
        """
        Open a tab for the specified content.

        Args:
            content_type: Type of content ('chapter', 'character', 'outline')
            content: The content object to display
        """
        # Create a unique ID for this content
        content_id = None

        if content_type == 'chapter' and isinstance(content, dict):
            content_id = f"chapter_{content.get('number', 0)}"
        elif content_type == 'character' and isinstance(content, dict):
            content_id = f"character_{content.get('name', 'unknown').lower().replace(' ', '_')}"
        elif content_type == 'outline':
            content_id = "outline"

        # If no valid ID could be created, generate a unique one
        if not content_id:
            import uuid
            content_id = f"{content_type}_{uuid.uuid4().hex[:8]}"

        logger.debug(f"Opening content tab for {content_type} with ID {content_id}")

        # Check if this content is already open in a tab
        if content_id in self.content_tabs:
            # Switch to the existing tab
            self.setCurrentIndex(self.content_tabs[content_id])
            logger.debug(f"Switched to existing tab for {content_id}")
            return

        # Create a new content viewer
        viewer = ContentViewerFactory.create_viewer(content_type, content)

        # Get a title for the tab
        tab_title = viewer.get_title()

        # Add the tab
        tab_index = self.addTab(viewer, tab_title)

        # Store the tab index for this content
        self.content_tabs[content_id] = tab_index

        # Switch to the new tab
        self.setCurrentIndex(tab_index)

        logger.debug(f"Created new tab for {content_type}: {tab_title}")

    def open_tab(self, tab_type: str, tab_id: str):
        """Open a tab for the specified item."""
        # Check if the tab is already open
        for i in range(self.count()):
            tab_data = self.widget(i).property("tab_data")
            if tab_data and tab_data.get("type") == tab_type and tab_data.get("id") == tab_id:
                self.setCurrentIndex(i)
                return

        # Open a new tab based on the type
        if tab_type == "outline":
            self._add_outline_tab()
        elif tab_type == "chapter":
            self._add_chapter_tab(tab_id)
        elif tab_type == "character":
            self._add_character_tab(tab_id)
        elif tab_type == "setting":
            self._add_setting_tab(tab_id)

    def _add_character_tab(self, character_id: str):
        """Add a character tab."""
        # Convert ID to readable name
        character_name = character_id.replace("_", " ").title()

        character_widget = QWidget()
        character_widget.setProperty("tab_data", {"type": "character", "id": character_id})

        layout = QVBoxLayout(character_widget)

        # Create a splitter for editor and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Editor part
        editor = QPlainTextEdit()
        editor.setPlaceholderText(f"Enter details for {character_name} here...")

        # Set a fixed-width font for the editor
        font = QFont("Consolas", 10)
        editor.setFont(font)

        # Preview part
        preview = QTextEdit()
        preview.setReadOnly(True)

        # Add editor and preview to splitter
        splitter.addWidget(editor)
        splitter.addWidget(preview)

        # Set initial sizes
        splitter.setSizes([int(splitter.width() * 0.5), int(splitter.width() * 0.5)])

        # Add splitter to layout
        layout.addWidget(splitter)

        # Connect editor to preview
        editor.textChanged.connect(lambda: self._update_preview(editor, preview))

        # Add the tab
        self.addTab(character_widget, character_name)

    def _add_setting_tab(self, setting_id: str):
        """Add a setting tab."""
        # Convert ID to readable name
        setting_name = setting_id.replace("_", " ").title()

        setting_widget = QWidget()
        setting_widget.setProperty("tab_data", {"type": "setting", "id": setting_id})

        layout = QVBoxLayout(setting_widget)

        # Create a splitter for editor and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Editor part
        editor = QPlainTextEdit()
        editor.setPlaceholderText(f"Enter details for {setting_name} here...")

        # Set a fixed-width font for the editor
        font = QFont("Consolas", 10)
        editor.setFont(font)

        # Preview part
        preview = QTextEdit()
        preview.setReadOnly(True)

        # Add editor and preview to splitter
        splitter.addWidget(editor)
        splitter.addWidget(preview)

        # Set initial sizes
        splitter.setSizes([int(splitter.width() * 0.5), int(splitter.width() * 0.5)])

        # Add splitter to layout
        layout.addWidget(splitter)

        # Connect editor to preview
        editor.textChanged.connect(lambda: self._update_preview(editor, preview))

        # Add the tab
        self.addTab(setting_widget, setting_name)

    def _update_preview(self, editor: QPlainTextEdit, preview: QTextEdit):
        """Update the preview with the editor content."""
        markdown = editor.toPlainText()
        preview.setMarkdown(markdown)

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML."""
        # This is a placeholder. In a real implementation, you would use a proper markdown library.
        return markdown.replace("\n", "<br>")
