"""
Editor tab widget for the WriterGUI application.
"""
import logging
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QPlainTextEdit, QSplitter, QTextEdit, QMessageBox, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from writegui.controllers.app_controller import AppController

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
            self.removeTab(index)

        logger.debug(f"Tab closed, remaining tabs: {self.count()}")

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

        # Connect editor to preview
        editor.textChanged.connect(lambda: self._update_preview(editor, preview))

        # Add to splitter
        splitter.addWidget(editor)
        splitter.addWidget(preview)
        splitter.setSizes([int(splitter.width() * 0.6), int(splitter.width() * 0.4)])

        layout.addWidget(splitter)

        # Add an initial character template
        editor.setPlainText(f"# {character_name}\n\n## Basic Information\n\n- **Full Name**: {character_name}\n- **Age**: \n- **Occupation**: \n- **Physical Description**: \n\n## Background\n\n[Character background here]\n\n## Personality\n\n- **Traits**: \n- **Strengths**: \n- **Weaknesses**: \n- **Motivations**: \n\n## Role in Story\n\n[Character's role and arc in the story]")

        self.addTab(character_widget, character_name)
        self.setCurrentWidget(character_widget)

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

        # Connect editor to preview
        editor.textChanged.connect(lambda: self._update_preview(editor, preview))

        # Add to splitter
        splitter.addWidget(editor)
        splitter.addWidget(preview)
        splitter.setSizes([int(splitter.width() * 0.6), int(splitter.width() * 0.4)])

        layout.addWidget(splitter)

        # Add an initial setting template
        editor.setPlainText(f"# {setting_name}\n\n## Description\n\n[General description of the setting]\n\n## Physical Characteristics\n\n- **Location**: \n- **Climate**: \n- **Geography**: \n- **Notable Features**: \n\n## Cultural Elements\n\n- **Inhabitants**: \n- **Customs**: \n- **History**: \n- **Economy**: \n\n## Role in Story\n\n[How this setting impacts the story and characters]")

        self.addTab(setting_widget, setting_name)
        self.setCurrentWidget(setting_widget)

    def _update_preview(self, editor: QPlainTextEdit, preview: QTextEdit):
        """Update the preview based on the editor content."""
        # Get the content from the editor
        content = editor.toPlainText()

        # Convert Markdown to HTML (basic implementation)
        html_content = self._markdown_to_html(content)

        # Set the HTML content to the preview
        preview.setHtml(html_content)

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert Markdown to HTML (basic implementation)."""
        # This is a very basic implementation
        # A real implementation would use a library like markdown or commonmark

        # Wrap the content in a styled HTML document
        html = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #e0e0e0;
                    background-color: #1a237e;
                    padding: 10px;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #00bfa5;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                h1 {
                    font-size: 24px;
                    border-bottom: 1px solid #303F9F;
                    padding-bottom: 5px;
                }
                h2 {
                    font-size: 20px;
                }
                h3 {
                    font-size: 16px;
                }
                p {
                    margin: 10px 0;
                }
                ul, ol {
                    margin: 10px 0;
                    padding-left: 20px;
                }
                li {
                    margin: 5px 0;
                }
                code {
                    background-color: #0a0a2e;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: Consolas, monospace;
                }
                pre {
                    background-color: #0a0a2e;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    font-family: Consolas, monospace;
                }
                blockquote {
                    margin: 10px 0;
                    padding: 10px 20px;
                    border-left: 5px solid #00bfa5;
                    background-color: rgba(0, 191, 165, 0.1);
                }
                strong {
                    color: #ffffff;
                }
            </style>
        </head>
        <body>
        """

        # Process Markdown syntax
        lines = markdown.split("\n")
        in_code_block = False
        in_list = False

        for line in lines:
            # Code blocks
            if line.startswith("```"):
                if in_code_block:
                    html += "</pre>\n"
                    in_code_block = False
                else:
                    html += "<pre><code>"
                    in_code_block = True
                continue

            if in_code_block:
                html += line.replace("<", "&lt;").replace(">", "&gt;") + "\n"
                continue

            # Empty line
            if not line.strip():
                if in_list:
                    html += "</ul>\n" if in_list == "ul" else "</ol>\n"
                    in_list = False
                html += "<p></p>\n"
                continue

            # Headings
            if line.startswith("# "):
                html += f"<h1>{line[2:]}</h1>\n"
            elif line.startswith("## "):
                html += f"<h2>{line[3:]}</h2>\n"
            elif line.startswith("### "):
                html += f"<h3>{line[4:]}</h3>\n"
            elif line.startswith("#### "):
                html += f"<h4>{line[5:]}</h4>\n"
            elif line.startswith("##### "):
                html += f"<h5>{line[6:]}</h5>\n"
            elif line.startswith("###### "):
                html += f"<h6>{line[7:]}</h6>\n"

            # Lists
            elif line.strip().startswith("- "):
                if in_list != "ul":
                    if in_list:
                        html += "</ol>\n" if in_list == "ol" else "</ul>\n"
                    html += "<ul>\n"
                    in_list = "ul"
                html += f"<li>{line.strip()[2:]}</li>\n"
            elif line.strip().startswith("* "):
                if in_list != "ul":
                    if in_list:
                        html += "</ol>\n" if in_list == "ol" else "</ul>\n"
                    html += "<ul>\n"
                    in_list = "ul"
                html += f"<li>{line.strip()[2:]}</li>\n"
            elif line.strip().startswith("1. ") or line.strip().startswith("1) "):
                if in_list != "ol":
                    if in_list:
                        html += "</ul>\n" if in_list == "ul" else "</ol>\n"
                    html += "<ol>\n"
                    in_list = "ol"
                html += f"<li>{line.strip()[3:]}</li>\n"

            # Blockquotes
            elif line.startswith("> "):
                html += f"<blockquote>{line[2:]}</blockquote>\n"

            # Regular paragraph
            else:
                # Process inline formatting
                text = line
                # Bold
                text = text.replace("**", "<strong>", 1).replace("**", "</strong>", 1) if "**" in text else text
                # Italic
                text = text.replace("*", "<em>", 1).replace("*", "</em>", 1) if "*" in text else text
                # Inline code
                text = text.replace("`", "<code>", 1).replace("`", "</code>", 1) if "`" in text else text

                html += f"<p>{text}</p>\n"

        # Close any open lists
        if in_list:
            html += "</ul>\n" if in_list == "ul" else "</ol>\n"

        html += """
        </body>
        </html>
        """

        return html
