"""
Configuration management for FMUS-Write.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class ConfigManager:
    """Manages configuration for the application."""

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """Initialize the config manager.

        Args:
            config_dir: Optional directory for configuration files.
                        Defaults to fmus_write/config.
        """
        if config_dir is None:
            # Get the directory of this file
            this_dir = Path(__file__).parent
            self.config_dir = this_dir
        else:
            self.config_dir = Path(config_dir)

        # Ensure the config directory exists
        os.makedirs(self.config_dir, exist_ok=True)

        # Default paths for various config files
        self.genres_path = self.config_dir / "genres.yaml"
        self.templates_path = self.config_dir / "templates.yaml"
        self.structures_path = self.config_dir / "structures.yaml"
        self.app_config_path = self.config_dir / "app_config.yaml"

        # Load configurations
        self.genres = self._load_yaml(self.genres_path)
        self.templates = self._load_yaml(self.templates_path)
        self.structures = self._load_yaml(self.structures_path)
        self.app_config = self._load_yaml(self.app_config_path)

        # Initialize with defaults if files don't exist
        if not self.genres:
            self._initialize_default_genres()

        if not self.templates:
            self._initialize_default_templates()

        if not self.structures:
            self._initialize_default_structures()

        if not self.app_config:
            self._initialize_default_app_config()

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML configuration file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dictionary with configuration data or empty dict if file doesn't exist
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading configuration from {file_path}: {e}")
            return {}

    def save_yaml(self, data: Dict[str, Any], file_path: Path) -> bool:
        """Save data to a YAML configuration file.

        Args:
            data: Data to save
            file_path: Path to the YAML file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving configuration to {file_path}: {e}")
            return False

    def get_genres(self) -> List[str]:
        """Get the list of available genres.

        Returns:
            List of genre names
        """
        return list(self.genres.get('genres', {}).keys())

    def get_genre_info(self, genre: str) -> Dict[str, Any]:
        """Get information about a specific genre.

        Args:
            genre: The genre name

        Returns:
            Dictionary with genre information
        """
        return self.genres.get('genres', {}).get(genre, {})

    def get_templates(self) -> List[str]:
        """Get the list of available templates.

        Returns:
            List of template names
        """
        return list(self.templates.get('templates', {}).keys())

    def get_template_info(self, template: str) -> Dict[str, Any]:
        """Get information about a specific template.

        Args:
            template: The template name

        Returns:
            Dictionary with template information
        """
        return self.templates.get('templates', {}).get(template, {})

    def get_structures(self) -> List[str]:
        """Get the list of available project structures.

        Returns:
            List of structure names
        """
        return list(self.structures.get('structures', {}).keys())

    def get_structure_info(self, structure: str) -> Dict[str, Any]:
        """Get information about a specific project structure.

        Args:
            structure: The structure name

        Returns:
            Dictionary with structure information
        """
        return self.structures.get('structures', {}).get(structure, {})

    def get_app_config(self) -> Dict[str, Any]:
        """Get the application configuration.

        Returns:
            Dictionary with application configuration
        """
        return self.app_config

    def update_app_config(self, config: Dict[str, Any]) -> bool:
        """Update the application configuration.

        Args:
            config: Configuration data to update

        Returns:
            True if successful, False otherwise
        """
        self.app_config.update(config)
        return self.save_yaml(self.app_config, self.app_config_path)

    def _initialize_default_genres(self) -> None:
        """Initialize the genres configuration with default values."""
        self.genres = {
            'genres': {
                'Fantasy': {
                    'description': 'Stories that involve magic, mythical creatures, or supernatural elements.',
                    'common_elements': ['Magic systems', 'Mythical creatures', 'Quests', 'Epic battles'],
                    'keywords': ['magic', 'quest', 'adventure', 'dragon', 'sword', 'wizard']
                },
                'Science Fiction': {
                    'description': 'Stories based on scientific or technological advances, often set in the future or space.',
                    'common_elements': ['Advanced technology', 'Space travel', 'Dystopian societies', 'Artificial intelligence'],
                    'keywords': ['technology', 'space', 'future', 'robot', 'alien', 'dystopia']
                },
                'Mystery': {
                    'description': 'Stories that revolve around solving a crime or puzzle.',
                    'common_elements': ['Detective protagonist', 'Crime scene', 'Clues', 'Suspects'],
                    'keywords': ['detective', 'murder', 'clue', 'suspect', 'investigation']
                },
                'Thriller': {
                    'description': 'Fast-paced, suspenseful stories often involving danger or high stakes.',
                    'common_elements': ['High stakes', 'Danger', 'Plot twists', 'Ticking clock'],
                    'keywords': ['suspense', 'danger', 'conspiracy', 'chase', 'assassin']
                },
                'Romance': {
                    'description': 'Stories focused on romantic relationships between characters.',
                    'common_elements': ['Love interests', 'Relationship development', 'Emotional conflicts', 'Happy ending'],
                    'keywords': ['love', 'relationship', 'passion', 'heartbreak', 'marriage']
                },
                'Historical Fiction': {
                    'description': 'Stories set in the past that blend historical facts with fictional elements.',
                    'common_elements': ['Historical setting', 'Period-accurate details', 'Historical events', 'Cultural context'],
                    'keywords': ['history', 'period', 'war', 'ancient', 'medieval', 'renaissance']
                },
                'Literary Fiction': {
                    'description': 'Character-driven stories with a focus on style, themes, and psychological depth.',
                    'common_elements': ['Complex characters', 'Internal conflicts', 'Social commentary', 'Symbolic elements'],
                    'keywords': ['character', 'literary', 'psychological', 'introspection', 'philosophical']
                },
                'Horror': {
                    'description': 'Stories designed to frighten, scare, or disgust readers.',
                    'common_elements': ['Monsters', 'Psychological terror', 'Gore', 'Suspense'],
                    'keywords': ['fear', 'terror', 'monster', 'supernatural', 'nightmare', 'death']
                },
                'Young Adult': {
                    'description': 'Stories aimed at teenage readers, often dealing with coming-of-age themes.',
                    'common_elements': ['Teenage protagonist', 'Coming-of-age', 'Identity exploration', 'Friendship'],
                    'keywords': ['teen', 'young adult', 'coming of age', 'school', 'friendship', 'identity']
                }
            }
        }
        self.save_yaml(self.genres, self.genres_path)

    def _initialize_default_templates(self) -> None:
        """Initialize the templates configuration with default values."""
        self.templates = {
            'templates': {
                'Blank Project': {
                    'description': 'An empty project with minimal structure.',
                    'components': ['title_page', 'chapters'],
                    'default_chapters': []
                },
                'Three-Act Structure': {
                    'description': 'Classical three-act structure with setup, confrontation, and resolution.',
                    'components': ['title_page', 'prologue', 'acts', 'epilogue'],
                    'plot_points': [
                        {'name': 'Inciting Incident', 'position': 0.12, 'description': 'Event that sets the story in motion'},
                        {'name': 'First Plot Point', 'position': 0.25, 'description': 'End of Act 1, protagonist commits to main conflict'},
                        {'name': 'Midpoint', 'position': 0.5, 'description': 'Major twist or revelation that changes the direction'},
                        {'name': 'Second Plot Point', 'position': 0.75, 'description': 'Final piece of the puzzle before climax'},
                        {'name': 'Climax', 'position': 0.9, 'description': 'The final confrontation or resolution of the main conflict'}
                    ],
                    'act_structure': [
                        {'name': 'Act 1: Setup', 'percentage': 0.25, 'description': 'Introduce characters, world, and initial conflict'},
                        {'name': 'Act 2: Confrontation', 'percentage': 0.5, 'description': 'Develop conflict, raise stakes, encounter obstacles'},
                        {'name': 'Act 3: Resolution', 'percentage': 0.25, 'description': 'Climax and resolution of the story'}
                    ]
                },
                'Hero\'s Journey': {
                    'description': 'Classic monomyth structure based on Joseph Campbell\'s Hero\'s Journey.',
                    'components': ['title_page', 'chapters'],
                    'plot_points': [
                        {'name': 'Ordinary World', 'position': 0.05, 'description': 'The hero\'s normal life before the adventure'},
                        {'name': 'Call to Adventure', 'position': 0.1, 'description': 'The hero is presented with a challenge or quest'},
                        {'name': 'Refusal of the Call', 'position': 0.15, 'description': 'The hero initially refuses the challenge'},
                        {'name': 'Meeting the Mentor', 'position': 0.2, 'description': 'The hero gains guidance from a mentor figure'},
                        {'name': 'Crossing the Threshold', 'position': 0.25, 'description': 'The hero leaves the ordinary world'},
                        {'name': 'Tests, Allies, Enemies', 'position': 0.35, 'description': 'The hero faces tests, makes allies and enemies'},
                        {'name': 'Approach to the Inmost Cave', 'position': 0.5, 'description': 'The hero approaches the central challenge'},
                        {'name': 'Ordeal', 'position': 0.6, 'description': 'The hero faces a major challenge or crisis'},
                        {'name': 'Reward', 'position': 0.7, 'description': 'The hero gains something from the ordeal'},
                        {'name': 'The Road Back', 'position': 0.8, 'description': 'The hero begins the journey home'},
                        {'name': 'Resurrection', 'position': 0.9, 'description': 'The hero faces a final test'},
                        {'name': 'Return with the Elixir', 'position': 0.95, 'description': 'The hero returns transformed'}
                    ]
                },
                'Save the Cat': {
                    'description': 'Modern storytelling structure based on Blake Snyder\'s Save the Cat.',
                    'components': ['title_page', 'chapters'],
                    'plot_points': [
                        {'name': 'Opening Image', 'position': 0.01, 'description': 'Sets the tone and gives a snapshot of the main character'},
                        {'name': 'Theme Stated', 'position': 0.05, 'description': 'Someone states the theme of the story'},
                        {'name': 'Setup', 'position': 0.1, 'description': 'Introduce characters and their world'},
                        {'name': 'Catalyst', 'position': 0.12, 'description': 'Something happens that changes the protagonist\'s world'},
                        {'name': 'Debate', 'position': 0.2, 'description': 'The protagonist debates what to do'},
                        {'name': 'Break into Two', 'position': 0.25, 'description': 'The protagonist makes a choice and enters Act 2'},
                        {'name': 'B Story', 'position': 0.3, 'description': 'Introduction of a secondary story or character'},
                        {'name': 'Fun and Games', 'position': 0.45, 'description': 'The "promise of the premise" plays out'},
                        {'name': 'Midpoint', 'position': 0.5, 'description': 'Either an "up" or a "down" moment for the protagonist'},
                        {'name': 'Bad Guys Close In', 'position': 0.65, 'description': 'Antagonistic forces tighten their grip'},
                        {'name': 'All Is Lost', 'position': 0.75, 'description': 'The worst moment for the protagonist'},
                        {'name': 'Dark Night of the Soul', 'position': 0.8, 'description': 'The protagonist\'s darkest moment'},
                        {'name': 'Break into Three', 'position': 0.85, 'description': 'The protagonist finds the solution'},
                        {'name': 'Finale', 'position': 0.95, 'description': 'The protagonist proves they have changed and solves the problem'},
                        {'name': 'Final Image', 'position': 0.99, 'description': 'Opposite of the opening image, shows change'}
                    ]
                }
            }
        }
        self.save_yaml(self.templates, self.templates_path)

    def _initialize_default_structures(self) -> None:
        """Initialize the structures configuration with default values."""
        self.structures = {
            'structures': {
                'novel': {
                    'description': 'A long narrative work of fiction.',
                    'word_count_range': [40000, 150000],
                    'default_chapters': 12,
                    'default_scenes_per_chapter': 3
                },
                'novella': {
                    'description': 'A short novel or long short story.',
                    'word_count_range': [10000, 40000],
                    'default_chapters': 6,
                    'default_scenes_per_chapter': 2
                },
                'short_story': {
                    'description': 'A brief fictional narrative.',
                    'word_count_range': [1000, 10000],
                    'default_chapters': 1,
                    'default_scenes_per_chapter': 1
                }
            }
        }
        self.save_yaml(self.structures, self.structures_path)

    def _initialize_default_app_config(self) -> None:
        """Initialize the application configuration with default values."""
        self.app_config = {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'interface': {
                'theme': 'dark',
                'font_size': 12,
                'autosave_interval': 5  # minutes
            },
            'export': {
                'default_format': 'markdown',
                'available_formats': ['markdown', 'html', 'epub', 'pdf', 'docx']
            }
        }
        self.save_yaml(self.app_config, self.app_config_path)
