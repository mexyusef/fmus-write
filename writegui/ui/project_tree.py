"""
Project tree widget for the WriterGUI application.
"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QCursor

from writegui.controllers.app_controller import AppController


class ProjectTreeWidget(QTreeWidget):
    """Tree widget for displaying the project structure."""

    item_activated = pyqtSignal(str, str)  # Item type, item id/path
    content_selected = pyqtSignal(str, object)  # Content type, content object

    def __init__(self, controller: AppController, parent=None):
        """Initialize the project tree widget."""
        super().__init__(parent)
        self.controller = controller

        # Setup tree widget properties
        self.setHeaderLabel("Project")
        self.setColumnCount(1)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemClicked.connect(self._on_item_clicked)

        # Initialize the tree with default structure
        self._init_tree()

    def refresh(self):
        """Refresh the tree with current project data."""
        print("ProjectTreeWidget.refresh called")

        # Check if a project is actually open
        if not self.controller.current_project:
            print("No current project found in controller")
        else:
            print(f"Current project: {self.controller.current_project.title}")

        # Clear the tree
        self.clear()
        print("Tree cleared")

        # Initialize the tree structure
        self._init_tree()
        print("Tree initialized")

        # Force a visual refresh
        self.update()
        print("Tree updated in UI")

    def _init_tree(self):
        """Initialize the tree with default structure."""
        # Check if a project is open
        if not self.controller.current_project:
            # No project is open, show a placeholder item
            placeholder = QTreeWidgetItem(self)
            placeholder.setText(0, "No Project Open")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            return

        # A project is open, create the structure
        project = self.controller.current_project

        # Debug log
        print(f"Initializing project tree for project: {project.title}")

        # Project root item
        project_item = QTreeWidgetItem(self)
        project_item.setText(0, project.title)
        project_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "id": "root"})

        # Outline section
        outline_item = QTreeWidgetItem(project_item)
        outline_item.setText(0, "Outline")
        outline_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "id": "outline"})

        # Add outline content if available
        outline_content = None
        if hasattr(project, 'generated_content') and project.generated_content:
            if 'outline' in project.generated_content:
                outline_content = project.generated_content['outline']
                outline_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "outline",
                    "id": "outline",
                    "content": outline_content
                })
                print(f"Found outline content: {type(outline_content)}")

        # Chapters section
        chapters_item = QTreeWidgetItem(project_item)
        chapters_item.setText(0, "Chapters")
        chapters_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "id": "chapters"})

        # Add actual chapters from the project if available
        has_chapters = False
        if hasattr(project, 'generated_content') and project.generated_content:
            if 'chapters' in project.generated_content and isinstance(project.generated_content['chapters'], list):
                chapters = project.generated_content['chapters']
                has_chapters = True
                print(f"Found {len(chapters)} chapters in generated_content")

                for i, chapter in enumerate(chapters):
                    chapter_item = QTreeWidgetItem(chapters_item)

                    # Get chapter title
                    if isinstance(chapter, dict):
                        title = chapter.get('title', f"Chapter {i+1}")
                    else:
                        title = f"Chapter {i+1}"

                    chapter_item.setText(0, title)
                    chapter_item.setData(0, Qt.ItemDataRole.UserRole, {
                        "type": "chapter",
                        "id": f"chapter_{i+1}",
                        "content": chapter
                    })

        # If no chapters in generated_content, check story.chapters
        if not has_chapters and hasattr(project, 'story') and hasattr(project.story, 'chapters'):
            chapters = project.story.chapters
            if chapters and isinstance(chapters, list):
                has_chapters = True
                print(f"Found {len(chapters)} chapters in story.chapters")

                for i, chapter in enumerate(chapters):
                    chapter_item = QTreeWidgetItem(chapters_item)

                    # Get chapter title
                    if isinstance(chapter, dict):
                        title = chapter.get('title', f"Chapter {i+1}")
                    else:
                        title = f"Chapter {i+1}"

                    chapter_item.setText(0, title)
                    chapter_item.setData(0, Qt.ItemDataRole.UserRole, {
                        "type": "chapter",
                        "id": f"chapter_{i+1}",
                        "content": chapter
                    })

        # If still no chapters, add placeholders
        if not has_chapters:
            print("No chapters found, adding placeholders")
            for i in range(1, 4):  # Default to 3 placeholder chapters
                chapter_item = QTreeWidgetItem(chapters_item)
                chapter_item.setText(0, f"Chapter {i}")
                chapter_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "chapter",
                    "id": f"chapter_{i}"
                })

        # Characters section
        characters_item = QTreeWidgetItem(project_item)
        characters_item.setText(0, "Characters")
        characters_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "id": "characters"})

        # Add actual characters from the project if available
        has_characters = False
        if hasattr(project, 'generated_content') and project.generated_content:
            if 'characters' in project.generated_content:
                characters_data = project.generated_content['characters']
                if isinstance(characters_data, dict) and 'characters' in characters_data:
                    character_list = characters_data['characters']
                    if isinstance(character_list, list):
                        has_characters = True
                        print(f"Found {len(character_list)} characters in generated_content")

                        for i, character in enumerate(character_list):
                            character_item = QTreeWidgetItem(characters_item)

                            # Get character name
                            if isinstance(character, dict):
                                name = character.get('name', f"Character {i+1}")
                            else:
                                name = f"Character {i+1}"

                            character_item.setText(0, name)
                            character_item.setData(0, Qt.ItemDataRole.UserRole, {
                                "type": "character",
                                "id": f"character_{i+1}",
                                "content": character
                            })

        # If no characters in generated_content, check project.characters
        if not has_characters and hasattr(project, 'characters'):
            character_list = project.characters
            if character_list and isinstance(character_list, list):
                has_characters = True
                print(f"Found {len(character_list)} characters in project.characters")

                for i, character in enumerate(character_list):
                    character_item = QTreeWidgetItem(characters_item)

                    # Get character name
                    if hasattr(character, 'name'):
                        name = character.name
                    elif isinstance(character, dict):
                        name = character.get('name', f"Character {i+1}")
                    else:
                        name = f"Character {i+1}"

                    character_item.setText(0, name)
                    character_item.setData(0, Qt.ItemDataRole.UserRole, {
                        "type": "character",
                        "id": f"character_{i+1}",
                        "content": character
                    })

        # If still no characters, add placeholders
        if not has_characters:
            print("No characters found, adding placeholders")
            character_names = ["Protagonist", "Antagonist", "Supporting Character"]
            for name in character_names:
                character_item = QTreeWidgetItem(characters_item)
                character_item.setText(0, name)
                character_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "character",
                    "id": name.lower().replace(" ", "_")
                })

        # Settings section
        settings_item = QTreeWidgetItem(project_item)
        settings_item.setText(0, "Settings")
        settings_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "id": "settings"})

        # Expand the project item
        self.expandItem(project_item)

        # Debug information
        print(f"Project tree initialized with {chapters_item.childCount()} chapters and {characters_item.childCount()} characters")

    def _on_item_double_clicked(self, item, column):
        """Handle double-clicking an item."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        if item_type and item_id:
            self.item_activated.emit(item_type, item_id)

    def _on_item_clicked(self, item, column):
        """Handle clicking an item."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        content = data.get("content")

        # Only emit for content types we can display
        if item_type in ["chapter", "character", "outline"] and content:
            print(f"Emitting content_selected for {item_type}")
            self.content_selected.emit(item_type, content)

    def _show_context_menu(self, position):
        """Show context menu for the tree item at the given position."""
        item = self.itemAt(position)
        if not item:
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        # Create context menu
        context_menu = QMenu(self)

        if item_type == "project":
            # Project context menu
            generate_action = QAction("Generate Content", self)
            generate_action.triggered.connect(lambda: self._on_generate(item))
            context_menu.addAction(generate_action)

            export_action = QAction("Export", self)
            export_action.triggered.connect(lambda: self._on_export(item))
            context_menu.addAction(export_action)

        elif item_type == "section":
            # Section context menu
            if item_id == "chapters":
                add_chapter_action = QAction("Add Chapter", self)
                add_chapter_action.triggered.connect(lambda: self._on_add_chapter(item))
                context_menu.addAction(add_chapter_action)

            elif item_id == "characters":
                add_character_action = QAction("Add Character", self)
                add_character_action.triggered.connect(lambda: self._on_add_character(item))
                context_menu.addAction(add_character_action)

            elif item_id == "settings":
                add_setting_action = QAction("Add Setting", self)
                add_setting_action.triggered.connect(lambda: self._on_add_setting(item))
                context_menu.addAction(add_setting_action)

        elif item_type in ["chapter", "character", "setting"]:
            # Item context menu
            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(lambda: self._on_edit_item(item))
            context_menu.addAction(edit_action)

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self._on_delete_item(item))
            context_menu.addAction(delete_action)

            # Additional actions for chapters
            if item_type == "chapter":
                generate_action = QAction("Generate Content", self)
                generate_action.triggered.connect(lambda: self._on_generate_chapter(item))
                context_menu.addAction(generate_action)

        # Show the context menu
        if not context_menu.isEmpty():
            context_menu.exec(QCursor.pos())

    def _on_generate(self, item):
        """Handle generating content for the project."""
        # TODO: Implement this
        QMessageBox.information(self, "Generate", "Generate project content")

    def _on_export(self, item):
        """Handle exporting the project."""
        # TODO: Implement this
        QMessageBox.information(self, "Export", "Export project")

    def _on_add_chapter(self, item):
        """Handle adding a chapter."""
        # TODO: Implement this
        # For now, just add a new item to the tree
        chapter_count = item.childCount() + 1
        chapter_item = QTreeWidgetItem(item)
        chapter_item.setText(0, f"Chapter {chapter_count}")
        chapter_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "chapter", "id": f"chapter_{chapter_count}"})

        # Expand the parent item
        self.expandItem(item)

    def _on_add_character(self, item):
        """Handle adding a character."""
        # TODO: Implement this
        # For now, just add a new item to the tree
        character_count = item.childCount() + 1
        character_item = QTreeWidgetItem(item)
        character_item.setText(0, f"Character {character_count}")
        character_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "character", "id": f"character_{character_count}"})

        # Expand the parent item
        self.expandItem(item)

    def _on_add_setting(self, item):
        """Handle adding a setting."""
        # TODO: Implement this
        # For now, just add a new item to the tree
        setting_count = item.childCount() + 1
        setting_item = QTreeWidgetItem(item)
        setting_item.setText(0, f"Setting {setting_count}")
        setting_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "setting", "id": f"setting_{setting_count}"})

        # Expand the parent item
        self.expandItem(item)

    def _on_edit_item(self, item):
        """Handle editing an item."""
        # TODO: Implement this
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        QMessageBox.information(self, "Edit", f"Edit {item_type}: {item_id}")

    def _on_delete_item(self, item):
        """Handle deleting an item."""
        # TODO: Implement this
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this {item_type}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove the item from the tree
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                self.invisibleRootItem().removeChild(item)

    def _on_generate_chapter(self, item):
        """Handle generating content for a chapter."""
        # TODO: Implement this
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_id = data.get("id")
        QMessageBox.information(self, "Generate Chapter", f"Generate content for {item_id}")
