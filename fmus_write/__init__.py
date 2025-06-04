"""
FMUS-Write: AI-assisted content creation library
"""

__version__ = "0.0.1"
__author__ = "FMUS Team"

# Models
from .models.base import BaseModel
from .models.story import StoryStructure
from .models.character import Character
from .models.world import World

# Agents
from .agents.base import Agent
from .agents.factory import AgentFactory

# Workflows
from .workflows.base import Workflow
from .workflows.registry import WorkflowRegistry

# Consistency
from .consistency.engine import ConsistencyEngine

# Output
from .output.manager import OutputManager

# CLI - import last to avoid circular imports
from .cli import main

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models.story import StoryStructure
from .models.character import Character
from .models.world import World
from .workflows.registry import WorkflowRegistry
from .agents import AgentFactory
from .consistency.engine import ConsistencyEngine
from .output.manager import OutputManager
from .llm.config import get_llm_config
from .llm.key_manager import KeyManager

# Get logger
logger = logging.getLogger(__name__)

class BookProject:
    """Represents a book writing project."""

    def __init__(
        self,
        title: str,
        genre: str,
        author: str = "Anonymous",
        structure_type: str = "novel",
        template: str = "Three-Act Structure",
        provider: str = "gemini",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize a book project.

        Args:
            title: The title of the book
            genre: The genre of the book
            author: The author's name
            structure_type: Structure type (novel, novella, short_story)
            template: Story template (Three-Act, Hero's Journey, etc.)
            provider: LLM provider to use
            model: Specific model to use with the provider
            api_key: API key for the LLM provider
        """
        self.title = title
        self.genre = genre
        self.author = author
        self.logger = logging.getLogger(f"fmus_write.book_project.{title}")

        # Initialize components
        self.story = StoryStructure(title=title, genre=genre)
        self.characters: List[Character] = []
        self.world: Optional[World] = None

        # Initialize workflow registry
        self.workflow_registry = WorkflowRegistry()
        self.agent_factory = AgentFactory()

        # Initialize consistency checker
        self.consistency_engine = ConsistencyEngine()

        # Initialize output manager
        self.output_manager = OutputManager()

        # Set up settings
        self.settings = {
            "structure_type": structure_type,
            "template": template,
            "llm_provider": provider,
            "author": author
        }

        if model:
            self.settings["model"] = model

        if api_key:
            self.settings["api_key"] = api_key

        # Generated content will be stored here
        self.generated_content = {}

    def configure(self, settings: dict):
        """
        Update project settings.

        Args:
            settings: Configuration options to update
        """
        self.settings.update(settings)

    def generate(self, workflow_type: str = "complete_book", **kwargs):
        """
        Generate content using the specified workflow.

        Args:
            workflow_type: Type of workflow to use
            **kwargs: Additional parameters for the workflow
        """
        # Load workflows if not already loaded
        self.workflow_registry.load_workflows()

        try:
            # Create workflow from registry
            workflow = self.workflow_registry.create_workflow(
                workflow_type,
                name=f"{self.title}_{workflow_type}",
                config=self.settings
            )
        except (ValueError, KeyError) as e:
            # If workflow not found, raise meaningful error
            raise ValueError(f"Unknown workflow type: {workflow_type}. Error: {str(e)}")

        # Prepare input data
        input_data = {
            "title": self.title,
            "genre": self.genre,
            **self.settings,  # Include all settings
            **kwargs,         # Override with any additional arguments
        }

        # Add provider and model information if available
        if 'provider' not in input_data:
            input_data['provider'] = self.settings.get('llm_provider', 'gemini')

        if 'model' not in input_data:
            input_data['model'] = self.settings.get('model')

        # Add characters and world if they exist
        if self.characters:
            input_data['characters'] = [char.to_dict() for char in self.characters]

        if self.world:
            input_data['world'] = self.world.to_dict()

        # Check if the workflow's execute method is async
        import inspect
        import asyncio

        if inspect.iscoroutinefunction(workflow.execute):
            # Execute workflow asynchronously
            self.logger.info(f"Running async workflow: {workflow_type}")

            # Use asyncio to run the coroutine
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is available, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            self.generated_content = loop.run_until_complete(workflow.execute(input_data))
        else:
            # Execute workflow synchronously
            self.generated_content = workflow.execute(input_data)

        # Process the generated content
        if self.generated_content:
            # Update story structure if appropriate
            if workflow_type == "complete_book" and isinstance(self.generated_content, dict):
                # Extract characters if any were generated
                if "characters" in self.generated_content and isinstance(self.generated_content["characters"], dict):
                    if "characters" in self.generated_content["characters"]:
                        character_list = self.generated_content["characters"]["characters"]
                        if isinstance(character_list, list):
                            for char_data in character_list:
                                if isinstance(char_data, dict):
                                    self.characters.append(Character.from_dict(char_data))

                # Update story structure with chapters
                if "chapters" in self.generated_content and isinstance(self.generated_content["chapters"], list):
                    self.story.chapters = self.generated_content["chapters"]

                # Update premise if available
                if "premise" in self.generated_content:
                    self.story.premise = self.generated_content["premise"]

        # Run consistency checks
        issues = self.consistency_engine.check_story(self.generated_content)
        if issues:
            # Log issues but continue
            print(f"Found {len(issues)} consistency issues.")
            print(self.consistency_engine.get_report())

        return self.generated_content

    def export(self, output_path: str, format: str = "markdown"):
        """
        Export generated content to a file.

        Args:
            output_path: Path to save the output
            format: Output format (markdown, html, text, json, epub)

        Raises:
            ValueError: If no content has been generated
        """
        if not self.generated_content:
            raise ValueError("No content has been generated. Call generate() first.")

        return self.output_manager.export(
            self.generated_content,
            output_path=output_path,
            format_type=format
        )
