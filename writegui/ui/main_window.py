"""
Main window for the WriterGUI application.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QDockWidget, QToolBar,
    QStatusBar, QMenuBar, QMenu, QApplication,
    QMessageBox, QFileDialog, QSplitter, QVBoxLayout,
    QWidget, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QProgressBar
)
from PyQt6.QtCore import Qt, QSize, QSettings, QPoint, QRect, QTimer, QByteArray
from PyQt6.QtGui import QAction, QKeySequence, QPalette, QColor

from writegui.controllers.app_controller import AppController
from writegui.ui.project_tree import ProjectTreeWidget
from writegui.ui.editor_tab import EditorTabWidget
from writegui.ui.properties_panel import PropertiesPanel
from writegui.dialogs.new_project_dialog import NewProjectDialog
from writegui.dialogs.refine_content_dialog import RefineContentDialog
from writegui.utils.stylesheet_manager import StylesheetManager
from writegui.utils.theme_manager import ThemeManager
from writegui.utils.settings_manager import SettingsManager
from writegui.ui.progress_widget import ProgressWidget
from writegui.resources.icons import IconManager


class MainWindow(QMainWindow):
    """Main window for the WriterGUI application."""

    def __init__(self, controller: AppController, parent=None):
        """Initialize the main window."""
        super().__init__(parent)
        self.controller = controller

        # Set window properties
        self.setWindowTitle("WriterGUI")
        self.setMinimumSize(1024, 768)

        # Setup theme and settings
        self.theme_manager = ThemeManager()
        self.settings_manager = controller.settings_manager
        
        # Apply the light green theme from StylesheetManager
        StylesheetManager.apply_theme()

        # Setup UI components
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_dock_widgets()
        self._create_central_widget()

        # Setup shortcuts
        self._setup_shortcuts()

        # Restore geometry and state if available
        self._restore_window_state()

    def _create_menus(self):
        """Create the application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")

        # New project action
        new_action = QAction(IconManager.new_icon(), "&New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._on_new_project)
        new_action.setToolTip("Create a new project")
        file_menu.addAction(new_action)

        # Open project action
        open_action = QAction(IconManager.open_icon(), "&Open...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._on_open_project)
        open_action.setToolTip("Open an existing project")
        file_menu.addAction(open_action)

        # Recent projects submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self._update_recent_projects_menu()

        # Clear recent action
        clear_recent_action = QAction("&Clear Recent", self)
        clear_recent_action.triggered.connect(self._on_clear_recent)
        self.recent_menu.addAction(clear_recent_action)

        file_menu.addSeparator()

        # Save project action
        save_action = QAction(IconManager.save_icon(), "&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._on_save_project)
        save_action.setToolTip("Save the current project")
        file_menu.addAction(save_action)

        # Save as action
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._on_save_project_as)
        save_as_action.setToolTip("Save the project with a new name")
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Export action
        export_action = QAction(IconManager.export_icon(), "&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._on_export)
        export_action.setToolTip("Export the project to various formats")
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")

        # Undo action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        edit_menu.addAction(undo_action)

        # Redo action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Cut action
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        edit_menu.addAction(cut_action)

        # Copy action
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        edit_menu.addAction(copy_action)

        # Paste action
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        edit_menu.addAction(paste_action)

        # Generate menu
        generate_menu = self.menuBar().addMenu("&Generate")

        # Complete book action
        complete_book_action = QAction(IconManager.generate_icon(), "Complete &Book", self)
        complete_book_action.triggered.connect(lambda: self._on_generate("complete_book"))
        complete_book_action.setToolTip("Generate a complete book")
        generate_menu.addAction(complete_book_action)

        # Outline action
        outline_action = QAction("&Outline", self)
        outline_action.triggered.connect(lambda: self._on_generate("outline"))
        outline_action.setToolTip("Generate an outline")
        generate_menu.addAction(outline_action)

        # Chapter action
        chapter_action = QAction("&Chapter", self)
        chapter_action.triggered.connect(lambda: self._on_generate("chapter"))
        chapter_action.setToolTip("Generate a chapter")
        generate_menu.addAction(chapter_action)

        # Character action
        character_action = QAction("C&haracter", self)
        character_action.triggered.connect(lambda: self._on_generate("character"))
        character_action.setToolTip("Generate a character")
        generate_menu.addAction(character_action)

        # View menu
        view_menu = self.menuBar().addMenu("&View")

        # Refresh action
        refresh_action = QAction(IconManager.refresh_icon(), "&Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._on_refresh)
        refresh_action.setToolTip("Refresh the view")
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu(IconManager.theme_icon(), "&Theme")
        
        # Theme actions
        theme_actions = {}
        for theme_name in ["Dark", "Light", "Sepia", "Blue"]:
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, t=theme_name.lower(): self._change_theme(t))
            theme_menu.addAction(theme_action)
            theme_actions[theme_name.lower()] = theme_action
            
        # Theme settings action
        theme_menu.addSeparator()
        theme_settings_action = QAction("Theme &Settings...", self)
        theme_settings_action.triggered.connect(self._show_theme_dialog)
        theme_menu.addAction(theme_settings_action)

        # Settings action
        view_menu.addSeparator()
        settings_action = QAction(IconManager.settings_icon(), "&Settings...", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        settings_action.setToolTip("Configure application settings")
        view_menu.addAction(settings_action)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _create_toolbars(self):
        """Create the application toolbars."""
        # Main toolbar
        self.main_toolbar = self.addToolBar("Main")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(24, 24))

        # Add actions to the toolbar
        # New action
        new_action = QAction(IconManager.new_icon(), "New", self)
        new_action.triggered.connect(self._on_new_project)
        new_action.setToolTip("Create a new project")
        self.main_toolbar.addAction(new_action)

        # Open action
        open_action = QAction(IconManager.open_icon(), "Open", self)
        open_action.triggered.connect(self._on_open_project)
        open_action.setToolTip("Open an existing project")
        self.main_toolbar.addAction(open_action)

        # Save action
        save_action = QAction(IconManager.save_icon(), "Save", self)
        save_action.triggered.connect(self._on_save_project)
        save_action.setToolTip("Save the current project")
        self.main_toolbar.addAction(save_action)

        self.main_toolbar.addSeparator()

        # Generate action
        generate_action = QAction(IconManager.generate_icon(), "Generate", self)
        generate_action.triggered.connect(lambda: self._on_generate("complete_book"))
        generate_action.setToolTip("Generate content")
        self.main_toolbar.addAction(generate_action)

        # Export action
        export_action = QAction(IconManager.export_icon(), "Export", self)
        export_action.triggered.connect(self._on_export)
        export_action.setToolTip("Export the project")
        self.main_toolbar.addAction(export_action)

        self.main_toolbar.addSeparator()

        # Settings action
        settings_action = QAction(IconManager.settings_icon(), "Settings", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        settings_action.setToolTip("Configure application settings")
        self.main_toolbar.addAction(settings_action)

    def _create_status_bar(self):
        """Create the status bar."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        # Add status labels
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        status_bar.addWidget(self.progress_bar)

        # Add word count label
        self.word_count_label = QLabel("Words: 0")
        status_bar.addPermanentWidget(self.word_count_label)

    def _create_dock_widgets(self):
        """Create the dock widgets."""
        # Project tree dock
        self.project_tree_dock = QDockWidget("Project Explorer", self)
        self.project_tree_dock.setObjectName("project_explorer_dock")
        self.project_tree_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.project_tree = ProjectTreeWidget(self.controller)
        self.project_tree_dock.setWidget(self.project_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_tree_dock)

        # Properties dock
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setObjectName("properties_dock")
        self.properties_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.properties_panel = PropertiesPanel(self.controller)
        self.properties_dock.setWidget(self.properties_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        # Add toggle actions to the View menu
        view_menu = self.menuBar().findChild(QMenu, "", Qt.FindChildOption.FindDirectChildrenOnly)
        if view_menu:
            view_menu.addAction(self.project_tree_dock.toggleViewAction())
            view_menu.addAction(self.properties_dock.toggleViewAction())

    def _create_central_widget(self):
        """Create the central widget."""
        # Main splitter for editor and results
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Create editor tabs
        self.editor_tabs = EditorTabWidget(self.controller)
        self.main_splitter.addWidget(self.editor_tabs)

        # Create results panel
        self.results_panel = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(0, 0, 0, 0)

        # Results header
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Add header title
        header_title = QLabel("Generated Content")
        header_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header_title)

        # Add spacer
        header_layout.addStretch()

        # Add Refine button
        self.refine_button = QPushButton("Refine")
        self.refine_button.setToolTip("Refine the generated content")
        self.refine_button.clicked.connect(self._on_refine_content)
        self.refine_button.setEnabled(False)  # Disabled until content is generated
        header_layout.addWidget(self.refine_button)

        # Add Export button
        export_results_button = QPushButton("Export")
        export_results_button.setToolTip("Export the generated content")
        export_results_button.clicked.connect(self._on_export)
        header_layout.addWidget(export_results_button)

        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: #f0f0f0;")
        results_layout.addWidget(header_widget)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)

        self.results_panel.setLayout(results_layout)
        self.main_splitter.addWidget(self.results_panel)

        # Initially hide the results panel
        self.results_panel.setVisible(False)

        # Create progress widget (initially hidden)
        self.progress_widget = ProgressWidget()
        self.progress_widget.setVisible(False)
        self.progress_widget.cancelled.connect(self._on_cancel_generation)

        # Add widgets to central widget
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(self.main_splitter)
        central_layout.addWidget(self.progress_widget)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def _setup_shortcuts(self):
        """Setup additional shortcuts."""
        # Ctrl+Tab to switch tabs
        next_tab_action = QAction(self)
        next_tab_action.setShortcut(QKeySequence("Ctrl+Tab"))
        next_tab_action.triggered.connect(self.editor_tabs.next_tab)
        self.addAction(next_tab_action)

        # Ctrl+Shift+Tab to switch tabs in reverse
        prev_tab_action = QAction(self)
        prev_tab_action.setShortcut(QKeySequence("Ctrl+Shift+Tab"))
        prev_tab_action.triggered.connect(self.editor_tabs.previous_tab)
        self.addAction(prev_tab_action)

        # F5 to refresh
        refresh_action = QAction(self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._on_refresh)
        self.addAction(refresh_action)

    def _update_recent_projects_menu(self):
        """Update the recent projects menu."""
        self.recent_menu.clear()

        recent_projects = self.controller.get_recent_projects()
        if not recent_projects:
            no_recent_action = QAction("No Recent Projects", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
            return

        for project in recent_projects:
            action = QAction(project["name"], self)
            action.setData(project["path"])
            action.triggered.connect(lambda checked, path=project["path"]: self._on_open_recent(path))
            self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Projects", self)
        clear_action.triggered.connect(self._on_clear_recent)
        self.recent_menu.addAction(clear_action)

    def _restore_window_state(self):
        """Restore the window geometry and state from settings."""
        import base64
        from PyQt6.QtCore import QByteArray
        
        window_state = self.settings_manager.get_window_state()
        if window_state:
            if "geometry" in window_state:
                geometry = QByteArray.fromBase64(window_state["geometry"].encode('ascii'))
                self.restoreGeometry(geometry)
            if "state" in window_state:
                state = QByteArray.fromBase64(window_state["state"].encode('ascii'))
                self.restoreState(state)

    def _save_window_state(self):
        """Save the window geometry and state to settings."""
        # Convert QByteArray to base64 string for JSON serialization
        import base64
        geometry = self.saveGeometry()
        state = self.saveState()
        
        window_state = {
            "geometry": base64.b64encode(geometry.data()).decode('ascii'),
            "state": base64.b64encode(state.data()).decode('ascii')
        }
        self.settings_manager.save_window_state(window_state)

    def _on_new_project(self):
        """Handle the new project action."""
        from writegui.dialogs.new_project_dialog import NewProjectDialog

        print("Opening new project dialog")
        dialog = NewProjectDialog(self, controller=self.controller)
        if dialog.exec():
            # Get the values from the dialog
            title = dialog.get_title()
            genre = dialog.get_genre()
            author = dialog.get_author()
            structure_type = dialog.get_structure_type()
            template = dialog.get_template()

            # Show status update
            self.status_label.setText("Creating new project...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            QApplication.processEvents()  # Update the UI

            print(f"Creating project with title={title}, genre={genre}, author={author}, structure={structure_type}")

            # Create a new project
            try:
                success = self.controller.create_project(
                    title=title,
                    genre=genre,
                    structure_type=structure_type,
                    template=template,
                    author=author,
                    llm_provider=self.controller.settings_manager.get("llm_provider", "gemini"),
                    model=self.controller.settings_manager.get("model", "gemini-1.5-flash"),
                    temperature=self.controller.settings_manager.get("temperature", 0.7)
                )

                self.progress_bar.setValue(50)
                QApplication.processEvents()  # Update the UI

                if success:
                    print("Project created successfully")
                    self.status_label.setText(f"Created new project: {title}")

                    # Update the UI to reflect the new project
                    print("Refreshing UI components")
                    self.project_tree.refresh()
                    self.editor_tabs.refresh()
                    self.properties_panel.refresh()

                    print("UI refreshed")
                    self.progress_bar.setValue(100)

                    # Debug info
                    print(f"Current project: {self.controller.current_project}")
                    print(f"Status bar updated with: Created new project: {title}")
                else:
                    print("Project creation failed")
                    self.status_label.setText("Failed to create project")
                    self.progress_bar.setValue(0)
                    QMessageBox.warning(self, "Warning", "Could not create the project.")

            except Exception as e:
                import traceback
                print(f"Exception during project creation: {e}")
                print(traceback.format_exc())
                self.status_label.setText(f"Error: {e}")
                self.progress_bar.setValue(0)
                QMessageBox.critical(self, "Error", f"Error creating project: {e}")

            finally:
                self.progress_bar.setVisible(False)
                print("Project creation process completed")

    def _on_open_project(self):
        """Handle the open project action."""
        project_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "WriterGUI Projects (*.wgp);;All Files (*)"
        )

        if project_path:
            self._open_project(project_path)

    def _on_open_recent(self, path):
        """Handle opening a recent project."""
        self._open_project(path)

    def _open_project(self, project_path):
        """Open a project from the given path."""
        try:
            self.controller.open_project(project_path)
            self.status_label.setText(f"Opened project: {project_path}")

            # Update the UI to reflect the opened project
            self.project_tree.refresh()
            self.editor_tabs.refresh()

            # Update recent projects menu
            self._update_recent_projects_menu()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening project: {e}")

    def _on_save_project(self):
        """Handle the save project action."""
        if not self.controller.current_project:
            QMessageBox.warning(self, "Warning", "No project is currently open.")
            return

        if not self.controller.current_project_path:
            self._on_save_project_as()
            return

        try:
            success = self.controller.save_project()
            if success:
                self.status_label.setText("Project saved successfully")
            else:
                QMessageBox.warning(self, "Warning", "Could not save the project.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving project: {e}")

    def _on_save_project_as(self):
        """Handle the save project as action."""
        if not self.controller.current_project:
            QMessageBox.warning(self, "Warning", "No project is currently open.")
            return

        project_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "WriterGUI Projects (*.wgp);;All Files (*)"
        )

        if project_path:
            try:
                # Add .wgp extension if not present
                if not project_path.lower().endswith(".wgp"):
                    project_path += ".wgp"

                success = self.controller.save_project(project_path)
                if success:
                    self.status_label.setText(f"Project saved as: {project_path}")

                    # Update recent projects menu
                    self._update_recent_projects_menu()
                else:
                    QMessageBox.warning(self, "Warning", "Could not save the project.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving project: {e}")

    def _on_export(self):
        """Handle the export action."""
        if not self.controller.current_project:
            QMessageBox.warning(self, "Warning", "No project is currently open.")
            return

        # Show export dialog to select format and options
        output_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Project", "", "Markdown Files (*.md);;HTML Files (*.html);;EPUB Files (*.epub);;PDF Files (*.pdf);;All Files (*)"
        )

        if output_path:
            # Show progress
            self.status_label.setText(f"Exporting to {output_path}...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(20)
            QApplication.processEvents()

            # Determine the format based on the file extension
            format_type = "markdown"  # Default
            if output_path.lower().endswith(".epub"):
                format_type = "epub"
            elif output_path.lower().endswith(".pdf"):
                format_type = "pdf"
            elif output_path.lower().endswith(".html"):
                format_type = "html"
            elif output_path.lower().endswith(".txt"):
                format_type = "text"

            try:
                # Update progress
                self.progress_bar.setValue(50)
                QApplication.processEvents()

                print(f"Exporting to {output_path} in {format_type} format")
                success = self.controller.export_content(output_path, format_type)

                if success:
                    self.progress_bar.setValue(100)
                    self.status_label.setText(f"Project exported to: {output_path}")

                    # Ask if the user wants to open the exported file
                    response = QMessageBox.question(
                        self,
                        "Export Successful",
                        f"Content exported to {output_path}. Would you like to open it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if response == QMessageBox.StandardButton.Yes:
                        # Open the file with the default application
                        import os
                        os.startfile(output_path) if os.name == 'nt' else QMessageBox.information(
                            self,
                            "File Location",
                            f"File exported to:\n{output_path}"
                        )
                else:
                    self.progress_bar.setValue(0)
                    self.status_label.setText("Export failed. See log for details.")
                    QMessageBox.warning(self, "Warning", "Could not export the project. Check the log file for details.")
            except Exception as e:
                self.progress_bar.setValue(0)
                self.status_label.setText(f"Export error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error exporting project: {e}")
            finally:
                # Hide progress bar
                self.progress_bar.setVisible(False)

    def _on_generate(self, scope):
        """Handle the generate action."""
        if not self.controller.current_project:
            QMessageBox.warning(self, "Warning", "No project is currently open.")
            return

        # Update status and show progress bar
        self.status_label.setText(f"Generating {scope}... Please wait.")
        
        # Get generation parameters from properties panel
        provider = self.properties_panel.provider_combo.currentText().lower()
        model = self.properties_panel.model_combo.currentText()
        temperature = self.properties_panel.temperature_spinbox.value()

        # Additional parameters
        params = {
            "provider": provider,
            "model": model,
            "temperature": temperature
        }

        # Add style if selected
        style = self.properties_panel.style_combo.currentText()
        if style:
            params["style"] = style

        # Add themes if selected
        themes = []
        if self.properties_panel.adventure_check.isChecked():
            themes.append("adventure")
        if self.properties_panel.romance_check.isChecked():
            themes.append("romance")
        if self.properties_panel.mystery_check.isChecked():
            themes.append("mystery")
        if themes:
            params["themes"] = themes

        # Setup and show progress widget
        self._setup_progress_for_scope(scope)
        self.progress_widget.setVisible(True)
        self.progress_widget.start_process()
        
        # Start a timer to simulate step progress
        self.generation_timer = QTimer(self)
        self.generation_timer.timeout.connect(self._update_generation_progress)
        self.generation_timer.start(500)  # Update every 500ms
        self.generation_step_progress = 0
        self.generation_scope = scope
        
        print(f"Generating {scope} with params: {params}")
        success = self.controller.generate_content(scope, **params)

        if success:
            self.progress_widget.complete_process()
            self.status_label.setText(f"Generation successful: Content ready to export. Click Export to save.")

            # Display the generated content in the results panel
            self._show_generated_content(scope)

            # Enable the refine button
            self.refine_button.setEnabled(True)

            # Update the editor tabs
            self.editor_tabs.refresh()
        else:
            self.progress_widget.fail_process(f"Failed to generate {scope}")
            self.status_label.setText(f"Generation failed: Could not generate {scope}.")
            QMessageBox.warning(self, "Warning", f"Could not generate {scope}. Check the log for details.")

        # Stop the progress timer
        if hasattr(self, 'generation_timer'):
            self.generation_timer.stop()

    def _setup_progress_for_scope(self, scope):
        """Setup the progress widget based on the generation scope."""
        if scope == "complete_book":
            steps = [
                "Planning story structure",
                "Creating characters",
                "Building world and settings",
                "Developing plot outline",
                "Writing chapters",
                "Editing and refining",
                "Final review"
            ]
        elif scope == "chapter":
            steps = [
                "Planning chapter structure",
                "Developing scenes",
                "Writing content",
                "Editing and refining"
            ]
        elif scope == "outline":
            steps = [
                "Analyzing genre requirements",
                "Creating story structure",
                "Developing plot points",
                "Finalizing outline"
            ]
        elif scope == "character":
            steps = [
                "Creating character profile",
                "Developing background",
                "Defining traits and motivations",
                "Creating character arc"
            ]
        else:
            steps = ["Generating content"]
            
        self.progress_widget.set_steps(steps)
        
    def _update_generation_progress(self):
        """Update the progress visualization during generation."""
        if not hasattr(self, 'generation_step_progress'):
            return
            
        # Update progress within current step
        self.generation_step_progress += 5
        if self.generation_step_progress >= 100:
            # Move to next step
            current_step = self.progress_widget.current_step_index
            if current_step < len(self.progress_widget.steps) - 1:
                self.progress_widget.advance_to_step(current_step + 1)
                self.generation_step_progress = 0
            else:
                self.generation_step_progress = 100
                
        self.progress_widget.set_step_progress(self.generation_step_progress)
        
    def _on_cancel_generation(self):
        """Handle cancellation of generation process."""
        # In a real implementation, you would need to actually cancel
        # the generation process in the controller
        self.status_label.setText("Generation cancelled by user")
        
        # Stop the progress timer
        if hasattr(self, 'generation_timer'):
            self.generation_timer.stop()

    def _show_generated_content(self, scope):
        """Display the generated content in the results panel."""
        if not self.controller.current_project:
            return

        # Make the results panel visible
        self.results_panel.setVisible(True)

        # Get the content based on scope
        if scope == "complete_book":
            content = self._format_book_for_display(self.controller.current_project)
        elif scope == "chapter":
            content = self._format_chapter_for_display(self.controller.current_project)
        else:
            # For other scopes, just display what we have
            content = f"Generated {scope} content"

        # Set the content
        print(f"Displaying generated content: {len(content)} characters")
        self.results_text.setMarkdown(content)

        # Resize the splitter to show both editor and results
        total_height = self.main_splitter.height()
        self.main_splitter.setSizes([int(total_height * 0.6), int(total_height * 0.4)])

    def _format_book_for_display(self, project):
        """Format book content for display in the results panel."""
        # This is a placeholder - in a real implementation, we would
        # extract the actual content from the project
        content = []

        # Add the title
        content.append(f"# {project.title}")
        content.append(f"*By {project.author if hasattr(project, 'author') else 'Anonymous'}*\n")

        # Add chapters if available
        if hasattr(project, 'chapters') and project.chapters:
            print(f"Formatting {len(project.chapters)} chapters for display")
            for i, chapter in enumerate(project.chapters):
                if isinstance(chapter, dict):
                    title = chapter.get('title', f"Chapter {i+1}")
                    content.append(f"## {title}")
                    chapter_content = chapter.get('content', '')
                    if chapter_content:
                        content.append(chapter_content)
                    else:
                        content.append("*No content generated for this chapter*")
                    content.append("\n---\n")
                else:
                    content.append(f"## Chapter {i+1}")
                    content.append("*Chapter data is not in expected format*")
                    content.append("\n---\n")
        else:
            print("No chapters found in project")
            content.append("\n## No chapters generated yet\n")
            content.append("Generate content using the Generate menu or toolbar button.")

        result = "\n".join(content)
        print(f"Generated display content: {len(result)} characters")
        return result

    def _format_chapter_for_display(self, project):
        """Format chapter content for display in the results panel."""
        # Placeholder implementation
        return "# Generated Chapter\n\nChapter content would appear here."

    def _on_refine_content(self):
        """Handle the refine content action."""
        if not self.controller.current_project:
            QMessageBox.warning(self, "Warning", "No project is currently open.")
            return

        # Show the refinement dialog
        dialog = RefineContentDialog(self)
        if dialog.exec():
            # Get the refinement prompt
            prompt = dialog.get_refinement_prompt()
            target = dialog.get_target()
            aspect = dialog.get_aspect()

            # Update status bar
            self.status_label.setText(f"Refining {aspect.lower()} of {target.lower()}... Please wait.")
            QApplication.processEvents()  # Update the UI

            try:
                # Get generation parameters from properties panel
                provider = self.properties_panel.provider_combo.currentText().lower()
                model = self.properties_panel.model_combo.currentText()
                temperature = self.properties_panel.temperature_spinbox.value()

                # Additional parameters for refinement
                params = {
                    "provider": provider,
                    "model": model,
                    "temperature": temperature,
                    "refinement_prompt": prompt,
                    "target": target.lower(),
                    "aspect": aspect.lower()
                }

                # Call refine on the controller
                success = self.controller.refine_content(**params)

                if success:
                    self.status_label.setText(f"Refinement successful: Content updated. Click Export to save.")

                    # Update the display with refined content
                    self._show_generated_content("complete_book")  # Default to showing the full book

                    # Update the editor tabs
                    self.editor_tabs.refresh()
                else:
                    self.status_label.setText("Refinement failed.")
                    QMessageBox.warning(self, "Warning", "Could not refine the content.")
            except Exception as e:
                self.status_label.setText(f"Refinement error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error refining content: {e}")

    def _on_refresh(self):
        """Handle the refresh action."""
        self.project_tree.refresh()
        self.editor_tabs.refresh()
        self.status_label.setText("Refreshed")

    def _on_clear_recent(self):
        """Clear the recent projects list."""
        self.controller.recent_projects.clear()
        self.controller._save_recent_projects()
        self._update_recent_projects_menu()

    def _show_theme_dialog(self):
        """Show the theme settings dialog."""
        from ..dialogs.theme_dialog import ThemeDialog
        
        # Get current theme from settings
        current_theme = self.settings_manager.get("theme", "dark")
        
        # Create and show the dialog
        dialog = ThemeDialog(self, current_theme)
        dialog.theme_selected.connect(lambda theme: self._change_theme(theme, dialog.is_remember_checked()))
        dialog.exec()
        
    def _change_theme(self, theme, save_setting=True):
        """Change the application theme."""
        # Apply the light green theme from StylesheetManager
        StylesheetManager.apply_theme()

        # Update the setting if requested
        if save_setting:
            self.settings_manager.set("theme", "light_green")

        self.status_label.setText(f"Theme changed to light green")

    def _show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About WriterGUI",
            "WriterGUI - PyQt6 GUI client for fmus_write\n\n"
            "Version: 0.0.1\n"
            "Copyright © 2025 Yusef Ulum\n\n"
            "A GUI for AI-powered content creation."
        )

    def _show_settings_dialog(self):
        """Show the settings dialog."""
        from ..dialogs.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
        
    def _on_settings_changed(self):
        """Handle settings changes."""
        # Update theme if it has changed
        current_theme = self.settings_manager.get("theme", "dark")
        self.theme_manager.apply_theme(self, current_theme)
        
        # Update status bar
        self.status_label.setText("Settings updated")
        
        # TODO: Apply other settings changes as needed

    def closeEvent(self, event):
        """Handle the window close event."""
        # Check for unsaved changes
        if self.controller.current_project:
            # TODO: Check for actual changes
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self._on_save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Save window state
        self._save_window_state()

        # Accept the event to close the window
        event.accept()
