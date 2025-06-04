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

        # Chapters section
        chapters_item = QTreeWidgetItem(project_item)
        chapters_item.setText(0, "Chapters")
        chapters_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "id": "chapters"})

        # Add actual chapters from the project if available
        if hasattr(project, 'chapters') and project.chapters:
            for i, chapter in enumerate(project.chapters):
                chapter_item = QTreeWidgetItem(chapters_item)

                # Get chapter title
                if isinstance(chapter, dict):
                    title = chapter.get('title', f"Chapter {i+1}")
                else:
                    title = f"Chapter {i+1}"

                chapter_item.setText(0, title)
                chapter_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "chapter",
                    "id": f"chapter_{i+1}"
                })
        else:
            # If no chapters, add a placeholder
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
        if hasattr(project, 'characters') and project.characters:
            for i, character in enumerate(project.characters):
                character_item = QTreeWidgetItem(characters_item)

                # Get character name
                if isinstance(character, dict):
                    name = character.get('name', f"Character {i+1}")
                else:
                    name = f"Character {i+1}"

                character_item.setText(0, name)
                character_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "character",
                    "id": f"character_{i+1}"
                })
        else:
            # Add default characters
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
        character_name = f"New Character {item.childCount() + 1}"
        character_item = QTreeWidgetItem(item)
        character_item.setText(0, character_name)
        character_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "character", "id": character_name.lower().replace(" ", "_")})

        # Expand the parent item
        self.expandItem(item)

    def _on_add_setting(self, item):
        """Handle adding a setting."""
        # TODO: Implement this
        # For now, just add a new item to the tree
        setting_name = f"New Setting {item.childCount() + 1}"
        setting_item = QTreeWidgetItem(item)
        setting_item.setText(0, setting_name)
        setting_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "setting", "id": setting_name.lower().replace(" ", "_")})

        # Expand the parent item
        self.expandItem(item)

    def _on_edit_item(self, item):
        """Handle editing an item."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        # TODO: Implement this
        QMessageBox.information(self, "Edit", f"Edit {item_type} {item_id}")

    def _on_delete_item(self, item):
        """Handle deleting an item."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        item_id = data.get("id")

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {item.text(0)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement actual deletion in the project
            # For now, just remove the item from the tree
            parent = item.parent()
            parent.removeChild(item)

    def _on_generate_chapter(self, item):
        """Handle generating content for a chapter."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_id = data.get("id")

        # TODO: Implement this
        QMessageBox.information(self, "Generate Chapter", f"Generate content for {item.text(0)}")
