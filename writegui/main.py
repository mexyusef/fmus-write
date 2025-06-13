#!/usr/bin/env python3
"""
Main entry point for the WriterGUI application.
"""
import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDir

# Setup proper logging
def setup_logging():
    """Set up logging configuration."""
    # Determine log directory
    if os.name == "nt":  # Windows
        log_dir = Path(os.environ.get("APPDATA", "")) / "WriterGUI" / "logs"
    else:  # macOS, Linux, etc.
        log_dir = Path.home() / ".config" / "WriterGUI" / "logs"

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / "writergui.log"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Log startup information
    logger.info("="*80)
    logger.info("WriterGUI starting up")
    logger.info(f"Logging to: {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info("="*80)

    return logger

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Global exception handler
def global_exception_handler(exctype, value, tb):
    """Handle uncaught exceptions."""
    logger = logging.getLogger("WriterGUI.ExceptionHandler")
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Uncaught exception: {error_msg}")

    # Show error dialog if it's a GUI application
    if QApplication.instance():
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Critical Error")
        error_dialog.setText("An unexpected error occurred:")
        error_dialog.setDetailedText(error_msg)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    # Call the original exception handler
    sys.__excepthook__(exctype, value, tb)

def main():
    """Main entry point for the application"""
    # Setup logging first
    logger = setup_logging()

    # Set global exception handler
    sys.excepthook = global_exception_handler

    try:
        # Import after logging setup
        from writegui.controllers.app_controller import AppController
        from writegui.ui.main_window import MainWindow
        from fmus_write.llm.providers.provider_map import PROVIDER_MAP
        from writegui.utils.stylesheet_manager import StylesheetManager

        logger.info("Creating application")
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("WriterGUI")
        app.setOrganizationName("FMUS")

        # Apply the light green theme
        StylesheetManager.apply_theme()
        logger.info("Applied light green theme")

        # Check available LLM providers from fmus_write package
        logger.info(f"Available LLM providers: {list(PROVIDER_MAP.keys())}")

        logger.info("Initializing controller")
        # Create the main controller
        controller = AppController()

        # Configure default settings
        default_settings = {
            "llm_provider": "gemini",  # Using gemini as documented in HOW-TO-USE.md
            "model": "gemini-1.5-flash",
            "temperature": 0.7
        }

        # Apply default settings
        for key, value in default_settings.items():
            if not controller.settings_manager.has_setting(key):
                controller.settings_manager.set(key, value)

        logger.info(f"Configured default settings: {default_settings}")

        logger.info("Creating main window")
        # Create and show the main window
        main_window = MainWindow(controller)
        main_window.show()

        # Log UI components initialization
        logger.info("Main window components:")
        logger.info(f"  - Editor tabs: {main_window.editor_tabs.count()} tabs")
        logger.info(f"  - Project tree initialized: {hasattr(main_window, 'project_tree')}")
        logger.info(f"  - Properties panel initialized: {hasattr(main_window, 'properties_panel')}")
        logger.info(f"  - Content viewer initialized: {hasattr(main_window, 'content_viewer')}")
        logger.info(f"  - Content viewer visible: {main_window.content_viewer.isVisible()}")

        # Create a test project if requested by command line args
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            logger.info("Creating test project")
            controller.create_project(
                title="Test Project",
                genre="Science Fiction",
                author="Test Author",
                llm_provider="gemini",
                model="gemini-1.5-flash",
                temperature=0.7
            )
            main_window.project_tree.refresh()
            main_window.editor_tabs.refresh()
            main_window.properties_panel.refresh()
            logger.info("Test project created and loaded")

        logger.info("Starting event loop")
        # Start the event loop
        result = app.exec()
        logger.info(f"Application exited with code: {result}")
        return result
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
