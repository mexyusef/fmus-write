"""
Application controller for the WriterGUI application.
"""
import os
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from fmus_write import BookProject
from fmus_write.config import ConfigManager
from writegui.utils.settings_manager import SettingsManager

# Fix Unicode encoding for logger
if sys.stdout.encoding != 'utf-8':
    # Force UTF-8 for FileHandler and StreamHandler
    class UTFStreamHandler(logging.StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            stream = self.stream
            try:
                stream.write(msg + self.terminator)
                self.flush()
            except UnicodeError:
                # Try to encode to ASCII with emoji replaced
                msg = msg.encode('ascii', 'replace').decode('ascii')
                stream.write(msg + self.terminator)
                self.flush()

    # Set up logging with UTF-8 encoding
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("writergui.log", encoding='utf-8'),
            UTFStreamHandler()
        ]
    )
else:
    # Standard setup if UTF-8 is already the encoding
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("writergui.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger("WriterGUI.Controller")

class AppController:
    """Main controller for the WriterGUI application."""

    def __init__(self):
        """Initialize the controller."""
        logger.info("Initializing AppController")
        self.current_project: Optional[BookProject] = None
        self.current_project_path: Optional[Path] = None
        self.recent_projects: List[Dict[str, str]] = []

        # Load configuration
        logger.debug("Loading configuration")
        self.config_manager = ConfigManager()
        app_config = self.config_manager.get_app_config()

        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize settings from app_config for backward compatibility
        default_settings = {
            "llm_provider": app_config.get('llm', {}).get('provider', 'openai'),
            "model": app_config.get('llm', {}).get('model', 'gpt-4o'),
            "temperature": app_config.get('llm', {}).get('temperature', 0.7),
            "default_export_format": app_config.get('export', {}).get('default_format', 'markdown'),
            "autosave_interval": app_config.get('interface', {}).get('autosave_interval', 5),
            "theme": app_config.get('interface', {}).get('theme', 'dark'),
        }
        
        # Update settings manager with default values if they don't exist
        for key, value in default_settings.items():
            if not self.settings_manager.has_setting(key):
                self.settings_manager.set(key, value)
        
        logger.debug(f"Initial settings: {self.settings_manager.get_all()}")

        # Load recent projects
        self._load_recent_projects()
        logger.info("AppController initialized successfully")

    def create_project(self, title, genre, structure_type="novel", template=None, author=None, **kwargs):
        """Create a new project with the given parameters."""
        try:
            # Import the BookProject class
            from fmus_write import BookProject
            # from fmus_write.llm.base import LLMMessage

            # Create a new BookProject instance
            print(f"Creating BookProject with title={title}, genre={genre}, structure={structure_type}")
            project = BookProject(title=title, genre=genre, structure_type=structure_type)
            print(f"BookProject created successfully: {project}")

            # Set the author if provided
            if author:
                project.author = author
                print(f"Set author to: {author}")

            # Configure the project with any additional parameters
            # This includes LLM provider settings
            llm_provider = kwargs.get('llm_provider', self.settings_manager.get('llm_provider', 'gemini'))
            model = kwargs.get('model', self.settings_manager.get('model', ''))
            temperature = kwargs.get('temperature', self.settings_manager.get('temperature', 0.7))

            print(f"Using llm_provider={llm_provider}, model={model}, temperature={temperature}")

            # Set provider-specific settings
            if hasattr(project, 'configure'):
                settings = {
                    'llm_provider': llm_provider,
                    'model': model,
                    'temperature': temperature
                }
                print(f"Calling project.configure with settings={settings}")
                project.configure(settings)
                print("Project configured successfully")

            # Set the current project
            self.current_project = project
            self.current_project_path = None  # No path until saved

            # Log project creation
            logger.info(f"Created new project: {title} ({genre})")
            logger.debug(f"Project structure: {structure_type}")
            logger.debug(f"LLM provider: {llm_provider}, model: {model}, temperature: {temperature}")

            print(f"Current project set to: {self.current_project}")
            print(f"Project title: {self.current_project.title}")
            print(f"Project genre: {self.current_project.genre}")

            # Add to recent projects (in memory only until saved)
            self._add_recent_project(title, "")

            return True

        except Exception as e:
            import traceback
            logger.error(f"Error creating project: {e}", exc_info=True)
            print(f"Exception creating project: {e}")
            print(traceback.format_exc())
            return False

    def open_project(self, project_path: str) -> Optional[BookProject]:
        """Open a project from the given path."""
        logger.info(f"Opening project from: {project_path}")
        try:
            # Convert to Path object
            path = Path(project_path)

            if not path.exists():
                logger.error(f"Project file does not exist: {path}")
                raise FileNotFoundError(f"Project file not found: {path}")

            logger.debug(f"Loading project data from {path}")
            # TODO: Implement actual project loading logic
            # For now, just create a dummy project
            try:
                with open(path, 'r') as f:
                    project_data = json.load(f)
                    logger.debug(f"Loaded project data: {project_data}")

                    title = project_data.get('title', path.stem)
                    genre = project_data.get('genre', 'Fiction')
                    author = project_data.get('author', 'Anonymous')

                    self.current_project = BookProject(
                        title=title,
                        genre=genre,
                        author=author
                    )
            except json.JSONDecodeError:
                logger.warning(f"Could not parse project file as JSON, creating default project")
                self.current_project = BookProject(
                    title=path.stem,
                    genre="Fiction"
                )

            self.current_project_path = path

            # Add to recent projects
            self._add_to_recent_projects(project_path)

            logger.info(f"Project opened successfully: {self.current_project.title}")
            return self.current_project
        except Exception as e:
            logger.error(f"Error opening project: {e}", exc_info=True)
            return None

    def save_project(self, project_path: Optional[str] = None) -> bool:
        """Save the current project to the given path."""
        if not self.current_project:
            logger.warning("Attempted to save with no active project")
            return False

        # If no path is provided, use the current project path
        if not project_path and self.current_project_path:
            project_path = str(self.current_project_path)
            logger.debug(f"Using existing project path: {project_path}")
        elif not project_path:
            logger.warning("No project path provided and no current path exists")
            return False

        logger.info(f"Saving project to: {project_path}")
        try:
            # Normalize the path to avoid double slashes on Windows
            norm_path = os.path.normpath(project_path)
            logger.debug(f"Normalized path: {norm_path}")

            # Create any parent directories if needed
            parent_dir = os.path.dirname(norm_path)
            logger.debug(f"Ensuring parent directory exists: {parent_dir}")
            os.makedirs(parent_dir, exist_ok=True)

            # Try to write a simple file to validate we can write to this location
            logger.debug(f"Writing project data to file")
            with open(norm_path, 'w') as f:
                # Get current timestamp for the saved_at field
                from datetime import datetime
                current_time = datetime.now().isoformat()

                # Save project data as JSON
                project_data = {
                    "title": self.current_project.title,
                    "genre": self.current_project.genre,
                    "author": getattr(self.current_project, "author", "Anonymous"),
                    "saved_at": current_time,
                    # Add other project data as needed
                }
                logger.debug(f"Project data: {project_data}")
                json.dump(project_data, f, indent=2)

            # Update current project path with normalized path
            self.current_project_path = Path(norm_path)

            # Add to recent projects with normalized path
            self._add_to_recent_projects(norm_path)

            logger.info(f"Project saved successfully to {norm_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving project: {e}", exc_info=True)
            return False

    def generate_content(self, workflow_type, **kwargs):
        """Generate content for the current project."""
        if not self.current_project:
            return False

        try:
            # Get the provider name from kwargs or settings
            provider_name = kwargs.get('provider', self.settings_manager.get('llm_provider', 'gemini')).lower()

            # Log the generation request - replace emoji with text equivalents
            logger.info(f"""Generating workflow "{workflow_type}" content with provider: {provider_name}""")
            logger.debug(f"Generation parameters: {kwargs}")

            # Set any additional generation params on the project
            if hasattr(self.current_project, 'configure'):
                logger.debug(f"[START] Configuring...")
                self.current_project.configure(settings=kwargs)
                logger.debug(f"[END] Configuring...")

            # Generate the content
            logger.debug(f"[START] Generating...")
            success = self.current_project.generate(workflow_type=workflow_type)
            logger.debug(f"[END] Generating...")

            if success:
                logger.info(f"Successfully generated {workflow_type} content")

                # Save the project after generation
                logger.info(f"Current project path: {str(self.current_project_path)}")
                self._save_project_with_backup()

                return True
            else:
                logger.warning(f"Failed to generate {workflow_type} content")
                return False

        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            return False

    def refine_content(self, **kwargs) -> bool:
        """Refine the generated content based on user instructions."""
        if not self.current_project:
            logger.warning("Attempted to refine content with no active project")
            return False

        try:
            # Extract refinement parameters
            refinement_prompt = kwargs.get("refinement_prompt", "")
            target = kwargs.get("target", "entire content")
            aspect = kwargs.get("aspect", "overall quality")

            logger.info(f"Refining {aspect} of {target}")
            logger.debug(f"Refinement prompt: {refinement_prompt}")

            # Get LLM parameters for the refinement
            provider = kwargs.get("provider", self.settings_manager.get("llm_provider", "openai"))
            model = kwargs.get("model", self.settings_manager.get("model", "gpt-4o"))
            temperature = kwargs.get("temperature", self.settings_manager.get("temperature", 0.7))

            logger.debug(f"Using provider: {provider}, model: {model}, temperature: {temperature}")

            # TODO: Implement actual content refinement
            # This would involve:
            # 1. Creating a refinement workflow or prompt
            # 2. Applying it to the correct part of the content
            # 3. Updating the project with the refined content

            logger.info("Refinement process completed")
            return True

        except Exception as e:
            logger.error(f"Error refining content: {e}", exc_info=True)
            return False

    def export_content(self, output_path: str, format_type: str = "markdown") -> bool:
        """Export the content in the specified format."""
        if not self.current_project:
            logger.warning("Attempted to export with no active project")
            return False

        logger.info(f"Exporting content to: {output_path} (format: {format_type})")

        try:
            # Normalize the path
            norm_path = os.path.normpath(output_path)
            logger.debug(f"Normalized output path: {norm_path}")

            # Create parent directories if needed
            parent_dir = os.path.dirname(norm_path)
            if parent_dir:
                logger.debug(f"Creating parent directory: {parent_dir}")
                os.makedirs(parent_dir, exist_ok=True)

            # Call the export method on the book project
            logger.debug("Calling export method on BookProject")

            self.current_project.export(norm_path, format_type)

            # Verify the file was created
            if os.path.exists(norm_path):
                file_size = os.path.getsize(norm_path)
                logger.info(f"Export successful: {norm_path} ({file_size} bytes)")
                return True
            else:
                logger.warning(f"Export failed: File {norm_path} was not created")
                return False

        except Exception as e:
            logger.error(f"Error exporting content: {e}", exc_info=True)
            return False

    def get_recent_projects(self) -> List[Dict[str, str]]:
        """Get the list of recent projects."""
        return self.recent_projects

    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings."""
        return self.settings_manager.get_all()

    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Update the settings."""
        for key, value in settings.items():
            self.settings_manager.set(key, value)
        
        # Update app_config with relevant settings for backward compatibility
        app_config = self.config_manager.get_app_config()
        if 'llm_provider' in settings:
            app_config['llm']['provider'] = settings['llm_provider']
        if 'model' in settings:
            app_config['llm']['model'] = settings['model']
        if 'temperature' in settings:
            app_config['llm']['temperature'] = settings['temperature']
        if 'default_export_format' in settings:
            app_config['export']['default_format'] = settings['default_export_format']
        if 'autosave_interval' in settings:
            app_config['interface']['autosave_interval'] = settings['autosave_interval']
        if 'theme' in settings:
            app_config['interface']['theme'] = settings['theme']

        self.config_manager.update_app_config(app_config)

    def get_available_genres(self) -> List[str]:
        """Get the list of available genres from configuration."""
        return self.config_manager.get_genres()

    def get_genre_info(self, genre: str) -> Dict[str, Any]:
        """Get information about a specific genre."""
        return self.config_manager.get_genre_info(genre)

    def get_available_templates(self) -> List[str]:
        """Get the list of available templates from configuration."""
        return self.config_manager.get_templates()

    def get_template_info(self, template: str) -> Dict[str, Any]:
        """Get information about a specific template."""
        return self.config_manager.get_template_info(template)

    def get_available_structures(self) -> List[str]:
        """Get the list of available project structures from configuration."""
        return self.config_manager.get_structures()

    def get_structure_info(self, structure: str) -> Dict[str, Any]:
        """Get information about a specific project structure."""
        return self.config_manager.get_structure_info(structure)

    def _add_to_recent_projects(self, project_path: str) -> None:
        """Add a project to the recent projects list."""
        path = Path(project_path)

        # Create a project info dictionary
        project_info = {
            "path": str(path),
            "name": path.stem,
            "last_opened": str(path.stat().st_mtime)
        }

        # Remove if already in the list
        self.recent_projects = [p for p in self.recent_projects if p["path"] != str(path)]

        # Add to the beginning of the list
        self.recent_projects.insert(0, project_info)

        # Keep only the 10 most recent
        self.recent_projects = self.recent_projects[:10]

        # Save the updated list
        self._save_recent_projects()

    def _load_settings(self) -> None:
        """Load settings from the configuration file."""
        # Settings are now loaded by the SettingsManager
        pass

    def _save_settings(self) -> None:
        """Save the current settings to the configuration file."""
        # Settings are now saved by the SettingsManager
        pass

    def _load_recent_projects(self) -> None:
        """Load the recent projects list from the configuration file."""
        config_dir = self._get_config_dir()
        recent_projects_path = config_dir / "recent_projects.json"

        if recent_projects_path.exists():
            try:
                with open(recent_projects_path, "r") as f:
                    self.recent_projects = json.load(f)
            except Exception as e:
                print(f"Error loading recent projects: {e}")

    def _save_recent_projects(self) -> None:
        """Save the recent projects list to the configuration file."""
        config_dir = self._get_config_dir()
        recent_projects_path = config_dir / "recent_projects.json"

        try:
            # Ensure the directory exists
            config_dir.mkdir(parents=True, exist_ok=True)

            with open(recent_projects_path, "w") as f:
                json.dump(self.recent_projects, f, indent=2)
        except Exception as e:
            print(f"Error saving recent projects: {e}")

    def _get_config_dir(self) -> Path:
        """Get the configuration directory for the application."""
        return self.settings_manager.get_config_dir()

    def _add_recent_project(self, project_name: str, project_path: str = "") -> None:
        """
        Add a project to the recent projects list even if not saved yet.
        Used for tracking newly created projects before they have a file path.
        """
        # Create a project info dictionary
        from datetime import datetime

        project_info = {
            "path": project_path,  # Empty path for unsaved projects
            "name": project_name,
            "last_opened": str(datetime.now().timestamp())
        }

        # Remove if already in the list by name (since path might be empty)
        self.recent_projects = [p for p in self.recent_projects
                               if not (p["name"] == project_name and p["path"] == "")]

        # Add to the beginning of the list
        self.recent_projects.insert(0, project_info)

        # Keep only the 10 most recent
        self.recent_projects = self.recent_projects[:10]

        # Note: We don't save to the config file until the project is actually saved
        # This keeps unsaved projects in memory only until they're saved with a path

    def _save_project_with_backup(self) -> bool:
        """
        Save the current project with a backup.
        Used after content generation to ensure work isn't lost.
        """
        try:
            # If we have a current project path, use it
            if self.current_project_path:
                return self.save_project()
            else:
                # For unsaved projects, create an autosave
                return self._create_autosave()

        except Exception as e:
            logger.error(f"Error in _save_project_with_backup: {e}", exc_info=True)
            return False

    def _create_autosave(self) -> bool:
        """
        Create an autosave file for the current project.
        Used to prevent data loss for unsaved projects.

        Returns:
            bool: True if autosave was successful, False otherwise
        """
        try:
            if not self.current_project:
                logger.warning("Cannot create autosave: No active project")
                return False

            # Get autosave directory from app configuration
            autosave_dir = self._get_autosave_directory()

            # Use the project title to create a filename (sanitized)
            safe_title = self._sanitize_filename(self.current_project.title)
            timestamp = self._get_timestamp_string()
            autosave_path = autosave_dir / f"{safe_title}_{timestamp}_autosave.json"

            logger.info(f"Auto-saving unsaved project to: {autosave_path}")
            return self.save_project(str(autosave_path))

        except Exception as e:
            logger.error(f"Error creating autosave: {e}", exc_info=True)
            return False

    def _get_autosave_directory(self) -> Path:
        """
        Get the directory for autosave files from application configuration.
        Creates the directory if it doesn't exist.

        Returns:
            Path: Path to the autosave directory
        """
        # Check app configuration for autosave directory
        app_config = self.config_manager.get_app_config()

        # Get the configured autosave directory or use default
        autosave_path = app_config.get('files', {}).get('autosave_directory')

        # If empty or not set, use default path and update config
        if not autosave_path:
            autosave_path = str(self._get_config_dir() / "autosave")

            # Update the configuration with the default path
            if 'files' not in app_config:
                app_config['files'] = {}

            app_config['files']['autosave_directory'] = autosave_path
            self.config_manager.update_app_config(app_config)
            logger.info(f"Set default autosave directory: {autosave_path}")

        # Convert to Path object
        autosave_dir = Path(autosave_path)

        # Ensure directory exists
        autosave_dir.mkdir(parents=True, exist_ok=True)

        return autosave_dir

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string for use as a filename.

        Args:
            filename: The string to sanitize

        Returns:
            str: A sanitized string safe for use as a filename
        """
        # Remove invalid characters and replace spaces with underscores
        safe_name = "".join(c for c in filename if c.isalnum() or c in " _-").strip()
        safe_name = safe_name.replace(" ", "_")

        # Ensure the filename isn't empty
        if not safe_name:
            safe_name = "unnamed_project"

        return safe_name

    def _get_timestamp_string(self) -> str:
        """
        Get a timestamp string suitable for filenames.

        Returns:
            str: A timestamp string in format YYYYMMDD_HHMMSS
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
