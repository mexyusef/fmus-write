"""
Content viewer widget for WriterGUI.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTextEdit, QSplitter, QPushButton,
    QScrollArea, QToolBar, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon

import markdown

class MarkdownViewer(QTextEdit):
    """Widget for rendering and displaying markdown content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setReadOnly(True)

        # Set default content
        self._set_default_content()

    def _set_default_content(self):
        """Set default empty content."""
        self.setHtml("""
        <h1>No Content</h1>
        <p>No content is currently available to display.</p>
        """)

    def set_markdown(self, content):
        """Set markdown content to display."""
        if not content:
            self._set_default_content()
            return

        # Convert markdown to HTML
        try:
            html = markdown.markdown(content)
            self.setHtml(html)
        except Exception as e:
            # Fallback to plain text if markdown conversion fails
            self.setPlainText(content)
            print(f"Error converting markdown: {e}")


class ChapterNavigator(QWidget):
    """Widget for navigating through chapters."""

    chapter_selected = pyqtSignal(int)  # Emitted when a chapter is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chapters = []
        self.current_chapter_index = -1

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Navigation controls
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous Chapter")
        self.prev_button.clicked.connect(self._on_prev_chapter)
        self.prev_button.setEnabled(False)

        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self._on_chapter_selected)

        self.next_button = QPushButton("Next Chapter")
        self.next_button.clicked.connect(self._on_next_chapter)
        self.next_button.setEnabled(False)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.chapter_combo)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        # Chapter content viewer
        self.content_viewer = MarkdownViewer()
        layout.addWidget(self.content_viewer)

        self.setLayout(layout)

    def set_chapters(self, chapters):
        """Set the chapters to navigate."""
        self.chapters = chapters
        self.chapter_combo.clear()

        if not chapters:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.content_viewer._set_default_content()
            return

        # Add chapters to combo box
        for i, chapter in enumerate(chapters):
            if isinstance(chapter, dict):
                title = chapter.get('title', f"Chapter {i+1}")
            else:
                title = f"Chapter {i+1}"

            self.chapter_combo.addItem(title)

        # Select first chapter
        if self.chapter_combo.count() > 0:
            self.chapter_combo.setCurrentIndex(0)

    def _on_chapter_selected(self, index):
        """Handle chapter selection from combo box."""
        if index < 0 or index >= len(self.chapters):
            return

        self.current_chapter_index = index
        self._update_navigation_buttons()
        self._display_current_chapter()
        self.chapter_selected.emit(index)

    def _on_prev_chapter(self):
        """Navigate to previous chapter."""
        if self.current_chapter_index > 0:
            self.chapter_combo.setCurrentIndex(self.current_chapter_index - 1)

    def _on_next_chapter(self):
        """Navigate to next chapter."""
        if self.current_chapter_index < len(self.chapters) - 1:
            self.chapter_combo.setCurrentIndex(self.current_chapter_index + 1)

    def _update_navigation_buttons(self):
        """Update the state of navigation buttons."""
        self.prev_button.setEnabled(self.current_chapter_index > 0)
        self.next_button.setEnabled(self.current_chapter_index < len(self.chapters) - 1)

    def _display_current_chapter(self):
        """Display the current chapter content."""
        if self.current_chapter_index < 0 or self.current_chapter_index >= len(self.chapters):
            self.content_viewer._set_default_content()
            return

        chapter = self.chapters[self.current_chapter_index]

        if isinstance(chapter, dict):
            title = chapter.get('title', f"Chapter {self.current_chapter_index+1}")
            content = chapter.get('content', '')
        else:
            title = f"Chapter {self.current_chapter_index+1}"
            content = str(chapter)

        # Format as markdown
        markdown_content = f"# {title}\n\n{content}"
        self.content_viewer.set_markdown(markdown_content)


class OutlineViewer(QWidget):
    """Widget for viewing the story outline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()

        # Outline viewer
        self.content_viewer = MarkdownViewer()
        layout.addWidget(self.content_viewer)

        self.setLayout(layout)

    def set_outline(self, outline):
        """Set the outline to display."""
        if not outline:
            self.content_viewer._set_default_content()
            return

        # Format as markdown
        if isinstance(outline, dict):
            title = outline.get('title', "Story Outline")
            content = outline.get('content', '')

            # Check if there are sections in the outline
            sections = outline.get('sections', [])
            if sections:
                content += "\n\n## Sections\n\n"
                for i, section in enumerate(sections):
                    if isinstance(section, dict):
                        section_title = section.get('title', f"Section {i+1}")
                        section_content = section.get('content', '')
                        content += f"### {section_title}\n\n{section_content}\n\n"
                    else:
                        content += f"### Section {i+1}\n\n{str(section)}\n\n"
        else:
            title = "Story Outline"
            content = str(outline)

        markdown_content = f"# {title}\n\n{content}"
        self.content_viewer.set_markdown(markdown_content)


class ContentViewerWidget(QWidget):
    """Widget for viewing generated content in different formats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tabs for different views
        self.tabs = QTabWidget()

        # Full view tab
        self.full_view = MarkdownViewer()
        self.tabs.addTab(self.full_view, "Full Book")

        # Chapter view tab
        self.chapter_view = ChapterNavigator()
        self.tabs.addTab(self.chapter_view, "Chapters")

        # Outline view tab
        self.outline_view = OutlineViewer()
        self.tabs.addTab(self.outline_view, "Outline")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def set_content(self, content):
        """Set the content to display in all views."""
        if not content:
            return

        # Extract book title and author
        title = content.get('title', "Untitled Book")
        author = content.get('author', "Anonymous")

        # Format full book content
        full_content = f"# {title}\n\n*By {author}*\n\n"

        # Add outline if available
        outline = content.get('outline', {})
        if outline:
            self.outline_view.set_outline(outline)

            # Add to full content
            if isinstance(outline, dict):
                outline_content = outline.get('content', '')
                if outline_content:
                    full_content += "## Outline\n\n" + outline_content + "\n\n---\n\n"

        # Add chapters if available
        chapters = content.get('chapters', [])
        if chapters:
            self.chapter_view.set_chapters(chapters)

            # Add to full content
            for i, chapter in enumerate(chapters):
                if isinstance(chapter, dict):
                    chapter_title = chapter.get('title', f"Chapter {i+1}")
                    chapter_content = chapter.get('content', '')
                    full_content += f"## {chapter_title}\n\n{chapter_content}\n\n---\n\n"
                else:
                    full_content += f"## Chapter {i+1}\n\n{str(chapter)}\n\n---\n\n"

        # Set full content
        self.full_view.set_markdown(full_content)

    def set_project(self, project):
        """Set content from a BookProject object."""
        if not project:
            return

        # Create a content dictionary from the project
        content = {
            'title': project.title,
            'author': getattr(project, 'author', 'Anonymous')
        }

        # Get generated content if available
        if hasattr(project, 'generated_content') and project.generated_content:
            # Add outline
            if 'outline' in project.generated_content:
                content['outline'] = project.generated_content['outline']

            # Add chapters
            if 'chapters' in project.generated_content:
                content['chapters'] = project.generated_content['chapters']

        # Set the content
        self.set_content(content)

    def get_current_view(self):
        """Get the currently active view."""
        index = self.tabs.currentIndex()
        if index == 0:
            return self.full_view
        elif index == 1:
            return self.chapter_view
        elif index == 2:
            return self.outline_view
        return None
