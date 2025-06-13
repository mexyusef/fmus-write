"""
Settings manager for WriterGUI.
"""
from pathlib import Path
import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manager for application settings and user preferences."""

    def __init__(self):
        """Initialize the settings manager."""
        self.settings = self._get_default_settings()
        self.config_dir = self.get_config_dir()
        self.settings_file = self.config_dir / "settings.json"
        self.recent_projects_file = self.config_dir / "recent_projects.json"

        # Load settings
        self._load_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get the default settings."""
        return {
            "theme": "dark",
            "llm_provider": "gemini",
            "model": "gemini-1.5-pro",
            "temperature": 0.7,
            "default_export_format": "markdown",
            "autosave_interval": 5,  # minutes
            "window": {
                "width": 1200,
                "height": 800,
                "x": 100,
                "y": 100,
                "maximized": False
            },
            "editor": {
                "font_family": "Consolas",
                "font_size": 11,
                "tab_size": 4,
                "auto_indent": True,
                "line_numbers": True,
                "word_wrap": True
            },
            "generation": {
                "default_style": "descriptive",
                "default_themes": []
            }
        }

    def get_config_dir(self) -> Path:
        """Get the configuration directory."""
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", "")) / "WriterGUI"
        else:  # macOS, Linux, etc.
            config_dir = Path.home() / ".config" / "WriterGUI"

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _load_settings(self):
        """Load settings from the configuration file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Update settings, keeping default values for missing keys
                    self._update_nested_dict(self.settings, loaded_settings)
                    logger.info(f"Settings loaded from {self.settings_file}")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")

    def _update_nested_dict(self, d: Dict, u: Dict):
        """Update a nested dictionary with another dictionary."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

    def save_settings(self):
        """Save settings to the configuration file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        # Support nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            value = self.settings
            for part in parts:
                if part in value:
                    value = value[part]
                else:
                    return default
            return value
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value by key."""
        # Support nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            target = self.settings
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
        else:
            self.settings[key] = value

        # Save settings after each change
        self.save_settings()

    def has_setting(self, key: str) -> bool:
        """Check if a setting exists."""
        # Support nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            value = self.settings
            for part in parts:
                if part not in value:
                    return False
                value = value[part]
            return True
        return key in self.settings

    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self.settings

    def get_recent_projects(self) -> List[Dict[str, str]]:
        """Get the list of recent projects."""
        if self.recent_projects_file.exists():
            try:
                with open(self.recent_projects_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading recent projects: {e}")
        return []

    def add_recent_project(self, project_path: str, project_name: str = None):
        """Add a project to the recent projects list."""
        path = Path(project_path)

        # Use the file name as project name if not provided
        if not project_name:
            project_name = path.stem

        # Create project info
        project_info = {
            "path": str(path),
            "name": project_name,
            "last_opened": str(path.stat().st_mtime)
        }

        # Get current list
        recent_projects = self.get_recent_projects()

        # Remove if already in list
        recent_projects = [p for p in recent_projects if p.get("path") != str(path)]

        # Add to beginning
        recent_projects.insert(0, project_info)

        # Keep only the most recent 10
        recent_projects = recent_projects[:10]

        # Save
        self._save_recent_projects(recent_projects)

    def clear_recent_projects(self):
        """Clear the recent projects list."""
        self._save_recent_projects([])

    def _save_recent_projects(self, projects: List[Dict[str, str]]):
        """Save the recent projects list."""
        try:
            with open(self.recent_projects_file, "w", encoding="utf-8") as f:
                json.dump(projects, f, indent=2)
            logger.info(f"Recent projects saved to {self.recent_projects_file}")
        except Exception as e:
            logger.error(f"Error saving recent projects: {e}")

    def get_window_state(self) -> Dict[str, Any]:
        """Get the saved window state."""
        return self.settings.get("window", {})

    def save_window_state(self, window_state: Dict[str, Any]):
        """Save the window state."""
        self.settings["window"] = window_state
        self.save_settings()

    def get_editor_settings(self) -> Dict[str, Any]:
        """Get editor settings."""
        return self.settings.get("editor", {})
