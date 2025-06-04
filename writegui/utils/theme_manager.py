"""
Theme manager for the WriterGUI application.
"""
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt


class ThemeManager:
    """Manages application themes and styling."""

    def __init__(self):
        """Initialize the theme manager."""
        # Define theme color palettes
        self.themes = {
            "dark": self._create_dark_theme(),
            "light": self._create_light_theme()
        }

        # Define style sheets for different themes
        self.style_sheets = {
            "dark": self._create_dark_style_sheet(),
            "light": self._create_light_style_sheet()
        }

    def apply_theme(self, widget: QWidget, theme_name: str = "dark"):
        """Apply a theme to the widget and its application."""
        if theme_name not in self.themes:
            theme_name = "dark"

        # Get the application instance
        app = QApplication.instance()

        # Apply palette to application
        app.setPalette(self.themes[theme_name])

        # Apply stylesheet to application
        app.setStyleSheet(self.style_sheets[theme_name])

        # Configure fonts
        font = QFont("Segoe UI", 9)
        app.setFont(font)

    def _create_dark_theme(self) -> QPalette:
        """Create a dark theme palette."""
        palette = QPalette()

        # Base colors
        palette.setColor(QPalette.ColorRole.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.Base, QColor(26, 35, 126))  # Deep blue
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(10, 10, 46))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(26, 35, 126))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(224, 224, 224))

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 191, 165))  # Teal
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 145, 234))  # Electric blue
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(142, 36, 170))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 145, 234))  # Electric blue
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(128, 128, 128))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(128, 128, 128))

        return palette

    def _create_light_theme(self) -> QPalette:
        """Create a light theme palette."""
        palette = QPalette()

        # Base colors
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(225, 245, 254))  # Light blue
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 236, 239))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(225, 245, 254))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 150, 136))  # Teal
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(3, 169, 244))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(103, 58, 183))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(3, 169, 244))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(153, 153, 153))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(153, 153, 153))

        return palette

    def _create_dark_style_sheet(self) -> str:
        """Create a dark theme style sheet."""
        return """
        QMainWindow {
            background-color: #121212;
        }

        QTabWidget {
            background-color: #1a237e;
        }

        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #1a237e;
        }

        QTabBar::tab {
            background-color: #0a0a2e;
            color: #e0e0e0;
            padding: 8px 15px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background-color: #00bfa5;
            color: #000000;
        }

        QTabBar::tab:hover:!selected {
            background-color: #303F9F;
        }

        QMenuBar {
            background-color: #121212;
            color: #e0e0e0;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 10px;
        }

        QMenuBar::item:selected {
            background-color: #0091ea;
            color: #ffffff;
        }

        QMenu {
            background-color: #1a237e;
            color: #e0e0e0;
            border: 1px solid #0a0a2e;
        }

        QMenu::item {
            padding: 5px 25px 5px 20px;
        }

        QMenu::item:selected {
            background-color: #0091ea;
            color: #ffffff;
        }

        QToolBar {
            background-color: #1a237e;
            border: none;
            spacing: 3px;
        }

        QToolButton {
            background-color: transparent;
            color: #e0e0e0;
            padding: 5px;
            border-radius: 3px;
        }

        QToolButton:hover {
            background-color: #303F9F;
        }

        QToolButton:pressed {
            background-color: #00bfa5;
            color: #000000;
        }

        QStatusBar {
            background-color: #0a0a2e;
            color: #e0e0e0;
        }

        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }

        QDockWidget::title {
            text-align: center;
            background-color: #0a0a2e;
            color: #e0e0e0;
            padding: 6px;
        }

        QListView, QTreeView, QTableView {
            background-color: #1a237e;
            border: 1px solid #0a0a2e;
            color: #e0e0e0;
            gridline-color: #303F9F;
        }

        QTreeView::item, QListView::item, QTableView::item {
            padding: 5px;
        }

        QTreeView::item:selected, QListView::item:selected, QTableView::item:selected {
            background-color: #0091ea;
            color: #ffffff;
        }

        QHeaderView::section {
            background-color: #0a0a2e;
            color: #e0e0e0;
            padding: 5px;
            border: 1px solid #303F9F;
        }

        QScrollBar:vertical {
            border: none;
            background-color: #0a0a2e;
            width: 12px;
            margin: 15px 0 15px 0;
        }

        QScrollBar::handle:vertical {
            background-color: #303F9F;
            min-height: 30px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #00bfa5;
        }

        QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
            border: none;
            background: none;
            height: 15px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QScrollBar:horizontal {
            border: none;
            background-color: #0a0a2e;
            height: 12px;
            margin: 0 15px 0 15px;
        }

        QScrollBar::handle:horizontal {
            background-color: #303F9F;
            min-width: 30px;
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #00bfa5;
        }

        QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
            border: none;
            background: none;
            width: 15px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }

        QPushButton {
            background-color: #00bfa5;
            color: #000000;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }

        QPushButton:hover {
            background-color: #00e5c0;
        }

        QPushButton:pressed {
            background-color: #008e76;
        }

        QPushButton:disabled {
            background-color: #4d4d4d;
            color: #a0a0a0;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1a237e;
            color: #e0e0e0;
            border: 1px solid #303F9F;
            padding: 5px;
            selection-background-color: #0091ea;
            selection-color: #ffffff;
        }

        QComboBox {
            background-color: #1a237e;
            color: #e0e0e0;
            border: 1px solid #303F9F;
            padding: 5px;
            border-radius: 3px;
        }

        QComboBox:editable {
            background-color: #1a237e;
        }

        QComboBox:hover {
            border: 1px solid #00bfa5;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #303F9F;
            border-left-style: solid;
        }

        QComboBox QAbstractItemView {
            background-color: #1a237e;
            color: #e0e0e0;
            selection-background-color: #0091ea;
            selection-color: #ffffff;
            border: 1px solid #303F9F;
        }

        QGroupBox {
            border: 1px solid #303F9F;
            border-radius: 5px;
            margin-top: 20px;
            color: #e0e0e0;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: #00bfa5;
        }

        QSpinBox, QDoubleSpinBox {
            background-color: #1a237e;
            color: #e0e0e0;
            border: 1px solid #303F9F;
            padding: 5px;
            border-radius: 3px;
        }

        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-left-width: 1px;
            border-left-color: #303F9F;
            border-left-style: solid;
        }

        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-left-width: 1px;
            border-left-color: #303F9F;
            border-left-style: solid;
        }

        QCheckBox, QRadioButton {
            spacing: 10px;
            color: #e0e0e0;
        }

        QCheckBox::indicator, QRadioButton::indicator {
            width: 15px;
            height: 15px;
        }

        QSlider::groove:horizontal {
            border: 1px solid #303F9F;
            height: 8px;
            background: #0a0a2e;
            margin: 2px 0;
        }

        QSlider::handle:horizontal {
            background: #00bfa5;
            border: 1px solid #00bfa5;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }

        QSlider::groove:vertical {
            border: 1px solid #303F9F;
            width: 8px;
            background: #0a0a2e;
            margin: 0 2px;
        }

        QSlider::handle:vertical {
            background: #00bfa5;
            border: 1px solid #00bfa5;
            width: 18px;
            height: 18px;
            margin: 0 -6px;
            border-radius: 9px;
        }

        QProgressBar {
            border: 1px solid #303F9F;
            border-radius: 3px;
            background-color: #0a0a2e;
            color: #e0e0e0;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #00bfa5;
            width: 20px;
        }
        """

    def _create_light_style_sheet(self) -> str:
        """Create a light theme style sheet."""
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }

        QTabWidget {
            background-color: #e1f5fe;
        }

        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #e1f5fe;
        }

        QTabBar::tab {
            background-color: #e9ecef;
            color: #000000;
            padding: 8px 15px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background-color: #009688;
            color: #ffffff;
        }

        QTabBar::tab:hover:!selected {
            background-color: #bbdefb;
        }

        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 10px;
        }

        QMenuBar::item:selected {
            background-color: #03a9f4;
            color: #ffffff;
        }

        QMenu {
            background-color: #e1f5fe;
            color: #000000;
            border: 1px solid #c0c0c0;
        }

        QMenu::item {
            padding: 5px 25px 5px 20px;
        }

        QMenu::item:selected {
            background-color: #03a9f4;
            color: #ffffff;
        }

        QToolBar {
            background-color: #e1f5fe;
            border: none;
            spacing: 3px;
        }

        QToolButton {
            background-color: transparent;
            color: #000000;
            padding: 5px;
            border-radius: 3px;
        }

        QToolButton:hover {
            background-color: #bbdefb;
        }

        QToolButton:pressed {
            background-color: #009688;
            color: #ffffff;
        }

        QStatusBar {
            background-color: #e9ecef;
            color: #000000;
        }

        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }

        QDockWidget::title {
            text-align: center;
            background-color: #e9ecef;
            color: #000000;
            padding: 6px;
        }

        QListView, QTreeView, QTableView {
            background-color: #e1f5fe;
            border: 1px solid #c0c0c0;
            color: #000000;
            gridline-color: #bbdefb;
        }

        QTreeView::item, QListView::item, QTableView::item {
            padding: 5px;
        }

        QTreeView::item:selected, QListView::item:selected, QTableView::item:selected {
            background-color: #03a9f4;
            color: #ffffff;
        }

        QHeaderView::section {
            background-color: #e9ecef;
            color: #000000;
            padding: 5px;
            border: 1px solid #c0c0c0;
        }

        QScrollBar:vertical {
            border: none;
            background-color: #e9ecef;
            width: 12px;
            margin: 15px 0 15px 0;
        }

        QScrollBar::handle:vertical {
            background-color: #bbdefb;
            min-height: 30px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #009688;
        }

        QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
            border: none;
            background: none;
            height: 15px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QScrollBar:horizontal {
            border: none;
            background-color: #e9ecef;
            height: 12px;
            margin: 0 15px 0 15px;
        }

        QScrollBar::handle:horizontal {
            background-color: #bbdefb;
            min-width: 30px;
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #009688;
        }

        QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
            border: none;
            background: none;
            width: 15px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }

        QPushButton {
            background-color: #009688;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }

        QPushButton:hover {
            background-color: #00bfa5;
        }

        QPushButton:pressed {
            background-color: #00796b;
        }

        QPushButton:disabled {
            background-color: #c0c0c0;
            color: #707070;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #e1f5fe;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 5px;
            selection-background-color: #03a9f4;
            selection-color: #ffffff;
        }

        QComboBox {
            background-color: #e1f5fe;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 5px;
            border-radius: 3px;
        }

        QComboBox:editable {
            background-color: #e1f5fe;
        }

        QComboBox:hover {
            border: 1px solid #009688;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #c0c0c0;
            border-left-style: solid;
        }

        QComboBox QAbstractItemView {
            background-color: #e1f5fe;
            color: #000000;
            selection-background-color: #03a9f4;
            selection-color: #ffffff;
            border: 1px solid #c0c0c0;
        }

        QGroupBox {
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 20px;
            color: #000000;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: #009688;
        }

        QSpinBox, QDoubleSpinBox {
            background-color: #e1f5fe;
            color: #000000;
            border: 1px solid #c0c0c0;
            padding: 5px;
            border-radius: 3px;
        }

        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-left-width: 1px;
            border-left-color: #c0c0c0;
            border-left-style: solid;
        }

        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-left-width: 1px;
            border-left-color: #c0c0c0;
            border-left-style: solid;
        }

        QCheckBox, QRadioButton {
            spacing: 10px;
            color: #000000;
        }

        QCheckBox::indicator, QRadioButton::indicator {
            width: 15px;
            height: 15px;
        }

        QSlider::groove:horizontal {
            border: 1px solid #c0c0c0;
            height: 8px;
            background: #e9ecef;
            margin: 2px 0;
        }

        QSlider::handle:horizontal {
            background: #009688;
            border: 1px solid #009688;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }

        QSlider::groove:vertical {
            border: 1px solid #c0c0c0;
            width: 8px;
            background: #e9ecef;
            margin: 0 2px;
        }

        QSlider::handle:vertical {
            background: #009688;
            border: 1px solid #009688;
            width: 18px;
            height: 18px;
            margin: 0 -6px;
            border-radius: 9px;
        }

        QProgressBar {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            background-color: #e9ecef;
            color: #000000;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #009688;
            width: 20px;
        }
        """
