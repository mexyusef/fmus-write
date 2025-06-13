"""
Content viewer components for the WriterGUI application.

These components are used to display different types of content in the editor area.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QLabel,
    QScrollArea, QFormLayout, QSplitter, QTabWidget, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

logger = logging.getLogger("WriterGUI.ContentViewers")

class ContentViewerBase(QWidget):
    """Base class for all content viewers."""

    content_changed = pyqtSignal(object)  # Signal emitted when content is changed

    def __init__(self, parent=None):
        """Initialize the content viewer."""
        super().__init__(parent)
        self.content = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def load_content(self, content):
        """Load content into the viewer."""
        self.content = content
        self._display_content()

    def _display_content(self):
        """Display the content in the viewer."""
        pass

    def get_title(self):
        """Get the title for this content."""
        return "Content"


class ChapterViewer(ContentViewerBase):
    """Viewer for chapter content."""

    def _setup_ui(self):
        """Set up the UI components."""
        super()._setup_ui()

        # Create the text browser for markdown rendering
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        # Use a readable font
        font = QFont("Segoe UI", 11)
        self.text_browser.setFont(font)

        # Add to layout
        self.layout.addWidget(self.text_browser)

    def _display_content(self):
        """Display the chapter content."""
        if not self.content:
            self.text_browser.setPlainText("No chapter content available.")
            return

        if isinstance(self.content, dict):
            # Extract chapter information
            title = self.content.get('title', 'Untitled Chapter')
            number = self.content.get('number', 0)
            content = self.content.get('content', '')

            # Format the content as markdown
            markdown_content = f"# {title}\n\n{content}"
            self.text_browser.setMarkdown(markdown_content)

            logger.debug(f"Displayed chapter: {title} ({len(content)} characters)")
        else:
            self.text_browser.setPlainText("Invalid chapter data format.")
            logger.warning(f"Invalid chapter data format: {type(self.content)}")

    def get_title(self):
        """Get the title for this chapter."""
        if isinstance(self.content, dict):
            return self.content.get('title', 'Chapter')
        return "Chapter"


class CharacterViewer(ContentViewerBase):
    """Viewer for character information."""

    def _setup_ui(self):
        """Set up the UI components."""
        super()._setup_ui()

        # Create a scroll area for the character info
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create the content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        # Set the content widget as the scroll area's widget
        self.scroll_area.setWidget(self.content_widget)

        # Add to layout
        self.layout.addWidget(self.scroll_area)

    def _display_content(self):
        """Display the character information."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.content:
            label = QLabel("No character information available.")
            self.content_layout.addWidget(label)
            return

        if isinstance(self.content, dict):
            # Character name and role
            name = self.content.get('name', 'Unknown Character')
            role = self.content.get('role', 'unknown')

            # Create header
            header = QLabel(f"<h1>{name}</h1><h3>{role.title()}</h3>")
            header.setTextFormat(Qt.TextFormat.RichText)
            self.content_layout.addWidget(header)

            # Character description
            if 'description' in self.content:
                self._add_section("Description", self.content['description'])

            # Character background
            if 'background' in self.content:
                self._add_section("Background", self.content['background'])

            # Character motivation
            if 'motivation' in self.content:
                self._add_section("Motivation", self.content['motivation'])

            # Character arc
            if 'arc' in self.content:
                self._add_section("Character Arc", self.content['arc'])

            # Add spacer at the end
            self.content_layout.addStretch()

            logger.debug(f"Displayed character: {name} ({role})")
        else:
            label = QLabel("Invalid character data format.")
            self.content_layout.addWidget(label)
            logger.warning(f"Invalid character data format: {type(self.content)}")

    def _add_section(self, title, content):
        """Add a section to the character display."""
        # Section title
        title_label = QLabel(f"<h2>{title}</h2>")
        title_label.setTextFormat(Qt.TextFormat.RichText)
        self.content_layout.addWidget(title_label)

        # Section content
        content_browser = QTextBrowser()
        content_browser.setOpenExternalLinks(True)
        content_browser.setMarkdown(content)
        content_browser.setMaximumHeight(200)
        self.content_layout.addWidget(content_browser)

    def get_title(self):
        """Get the title for this character."""
        if isinstance(self.content, dict):
            return self.content.get('name', 'Character')
        return "Character"


class OutlineViewer(ContentViewerBase):
    """Viewer for story outline."""

    def _setup_ui(self):
        """Set up the UI components."""
        super()._setup_ui()

        # Create the text browser for markdown rendering
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        # Add to layout
        self.layout.addWidget(self.text_browser)

    def _display_content(self):
        """Display the outline content."""
        if not self.content:
            self.text_browser.setPlainText("No outline available.")
            return

        if isinstance(self.content, dict):
            content_parts = []

            # Title and basic info
            title = self.content.get('title', 'Untitled Story')
            genre = self.content.get('genre', '')
            content_parts.append(f"# {title} Outline\n")

            if genre:
                content_parts.append(f"**Genre:** {genre}\n")

            # Premise
            premise = self.content.get('premise', '')
            if premise:
                content_parts.append(f"## Premise\n\n{premise}\n")

            # Theme
            theme = self.content.get('theme', '')
            if theme:
                content_parts.append(f"## Theme\n\n{theme}\n")

            # Sections
            sections = self.content.get('sections', [])
            if sections:
                content_parts.append("## Story Structure\n")

                for i, section in enumerate(sections):
                    if isinstance(section, dict):
                        section_title = section.get('title', f"Section {i+1}")
                        description = section.get('description', '')

                        content_parts.append(f"### {section_title}\n\n{description}\n")

                        # Events
                        events = section.get('events', [])
                        if events:
                            content_parts.append("#### Key Events\n")
                            for event in events:
                                content_parts.append(f"- {event}")
                            content_parts.append("\n")

            # Join all parts
            full_content = "\n".join(content_parts)
            self.text_browser.setMarkdown(full_content)

            logger.debug(f"Displayed outline for: {title} ({len(full_content)} characters)")
        elif isinstance(self.content, str):
            # Handle string format
            self.text_browser.setMarkdown(self.content)
            logger.debug(f"Displayed outline text ({len(self.content)} characters)")
        else:
            self.text_browser.setPlainText("Invalid outline data format.")
            logger.warning(f"Invalid outline data format: {type(self.content)}")

    def get_title(self):
        """Get the title for this outline."""
        if isinstance(self.content, dict):
            return f"{self.content.get('title', 'Story')} Outline"
        return "Outline"


class ContentViewerFactory:
    """Factory for creating content viewers."""

    @staticmethod
    def create_viewer(content_type, content=None):
        """
        Create a content viewer for the specified type.

        Args:
            content_type: Type of content ('chapter', 'character', 'outline')
            content: Content to display in the viewer

        Returns:
            ContentViewerBase: A content viewer instance
        """
        viewer = None

        if content_type == 'chapter':
            viewer = ChapterViewer()
        elif content_type == 'character':
            viewer = CharacterViewer()
        elif content_type == 'outline':
            viewer = OutlineViewer()
        else:
            # Default to base viewer
            viewer = ContentViewerBase()
            logger.warning(f"Unknown content type: {content_type}, using base viewer")

        # Load content if provided
        if content is not None:
            viewer.load_content(content)

        return viewer
