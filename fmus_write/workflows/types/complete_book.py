"""
Complete Book Generation Workflow.
"""
import json
import logging
from typing import Dict, Any, List

from fmus_write.workflows.base import Workflow
from fmus_write.models.story import StoryStructure
from fmus_write.llm.base import LLMMessage
from fmus_write.llm.providers.provider_map import PROVIDER_MAP
from fmus_write.llm.utils import parse_llm_json_response

logger = logging.getLogger(__name__)

class CompleteBookWorkflow(Workflow):
    """Workflow for generating a complete book."""

    def __init__(self, name: str, config: Dict[str, Any] = None, **kwargs):
        """Initialize the workflow."""
        description = "Generates a complete book with outline, characters, and content."
        super().__init__(name, description, config)

    async def generate_with_llm(self, provider_name: str, messages: List[LLMMessage]) -> str:
        """
        Generate content using the specified LLM provider.

        Args:
            provider_name: Name of the LLM provider to use
            messages: List of messages to send to the LLM

        Returns:
            Generated content as a string
        """
        try:
            # Get the provider class from the provider map
            provider_class = PROVIDER_MAP.get(provider_name)
            if provider_class:
                provider_instance = provider_class()
                self.logger.info(f"Calling generate_response method of {provider_name} provider")
                return await provider_instance.generate_response(messages)
            else:
                raise ValueError(f"Provider '{provider_name}' not supported")

        except Exception as e:
            self.logger.error(f"Error generating content with LLM: {e}")
            raise

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow to generate a complete book.

        Args:
            input_data: Dictionary containing:
                - title: Book title
                - genre: Book genre
                - provider: LLM provider to use (default: gemini)
                - structure_type: Type of story structure (e.g., novel, novella)
                - template: Type of story template (e.g., Three-Act, Hero's Journey)
                - story_description: User's description of the story idea
                - settings: Additional settings for generation

        Returns:
            Dictionary containing the generated book content
        """
        self.logger.info(f"Starting complete book generation for: {input_data.get('title')}")

        # Extract basic info
        title = input_data.get('title', 'Untitled Book')
        genre = input_data.get('genre', 'Fiction')
        provider = input_data.get('provider', 'gemini')
        structure_type = input_data.get('structure_type', 'novel')
        template = input_data.get('template', 'Three-Act Structure')
        story_description = input_data.get('story_description', '')

        # Create story structure object
        story = StoryStructure(
            title=title,
            genre=genre,
            premise=f"A {genre} story titled '{title}'."
        )

        # Use the actual LLM to generate content
        try:
            self.logger.info(f"Generating outline using {provider} provider")
            outline_prompt = self._create_outline_prompt(title, genre, structure_type, template, story_description)
            outline_messages = [LLMMessage(role="user", content=outline_prompt)]
            outline_json = await self.generate_with_llm(provider, outline_messages)
            print(f">> Hasil dari LLM [outline]: outline_json: {outline_json}")

            # Use our utility function instead of direct json.loads
            try:
                outline = parse_llm_json_response(outline_json)
                self.logger.info("Successfully parsed outline JSON")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse outline JSON: {e}")
                # Create a minimal outline to continue
                outline = {"title": title, "genre": genre, "premise": story.premise, "sections": []}

            self.logger.info(f"Generating characters using {provider} provider")
            character_prompt = self._create_character_prompt(title, genre, outline, story_description)
            character_messages = [LLMMessage(role="user", content=character_prompt)]
            character_json = await self.generate_with_llm(provider, character_messages)
            print(f">> Hasil dari LLM [characters]: character_json: {character_json}")

            # Use our utility function instead of direct json.loads
            try:
                characters = parse_llm_json_response(character_json)
                self.logger.info("Successfully parsed characters JSON")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse characters JSON: {e}")
                # Create minimal character data to continue
                characters = {"characters": []}

            # Determine number of chapters based on structure type
            if structure_type.lower() == 'novel':
                total_chapters = 10
            elif structure_type.lower() == 'novella':
                total_chapters = 5
            else:  # short_story or default
                total_chapters = 3

            chapters = []
            for i in range(1, total_chapters + 1):
                self.logger.info(f"Generating chapter {i}/{total_chapters} using {provider} provider")
                chapter_prompt = self._create_chapter_prompt(title, genre, outline, characters, i, total_chapters, story_description)
                chapter_messages = [LLMMessage(role="user", content=chapter_prompt)]
                chapter_content = await self.generate_with_llm(provider, chapter_messages)
                print(f">> Hasil dari LLM [chapter {i}]: chapter_content: {chapter_content}")

                chapters.append({
                    "title": f"Chapter {i}",
                    "number": i,
                    "summary": f"Chapter {i} of {title}",
                    "content": chapter_content
                })

            self.logger.info(f"Successfully generated content for book: {title}")

        except Exception as e:
            self.logger.error(f"Error during book generation: {e}")
            # Continue with empty structures so the workflow doesn't completely fail
            outline = {"title": title, "genre": genre, "premise": story.premise, "sections": []}
            characters = {"characters": []}
            chapters = []

        # Prepare output data
        output_data = {
            "title": title,
            "genre": genre,
            "author": input_data.get('author', 'Anonymous'),
            "premise": story.premise,
            "outline": outline,
            "characters": characters,
            "chapters": chapters,
            "structure_type": structure_type,
            "template": template
        }

        self.logger.info(f"Completed book generation for: {title}")
        return output_data

    def _create_outline_prompt(self, title: str, genre: str, structure_type: str, template: str, story_description: str = "") -> str:
        """Create a prompt for generating a book outline."""
        # Add the story description if provided
        story_guidance = ""
        if story_description:
            story_guidance = f"""
            Use the following story description as a guide:
            {story_description}

            Make sure your outline aligns with this description while still being creative and engaging.
            """

        prompt = f"""
        I need you to create a detailed outline for a {structure_type} titled "{title}" in the {genre} genre.
        Use the {template} story structure as a framework.
        {story_guidance}

        Please format your response as a JSON object with the following structure:
        {{
            "title": "{title}",
            "genre": "{genre}",
            "premise": "A brief one or two sentence premise of the story",
            "theme": "The central theme of the story",
            "sections": [
                {{
                    "title": "Section title (e.g., Act 1, Chapter 1, etc.)",
                    "description": "Brief description of this section",
                    "events": [
                        "Key event 1 that happens in this section",
                        "Key event 2 that happens in this section",
                        "..."
                    ]
                }},
                // More sections...
            ]
        }}

        Make sure the outline is coherent and follows a logical progression. The story should have a clear beginning, middle, and end.
        Only include the JSON object in your response, no other text.
        """
        return prompt

    def _create_character_prompt(self, title: str, genre: str, outline: Dict[str, Any], story_description: str = "") -> str:
        """Create a prompt for generating characters."""
        # Convert outline to a string representation for the prompt
        outline_str = json.dumps(outline, indent=2)

        # Add the story description if provided
        story_guidance = ""
        if story_description:
            story_guidance = f"""
            Also consider this story description:
            {story_description}

            Ensure the characters align with this vision while still being well-developed and interesting.
            """

        prompt = f"""
        Based on the following outline for a {genre} story titled "{title}", create a set of detailed characters.

        Outline:
        {outline_str}
        {story_guidance}

        Please format your response as a JSON object with the following structure:
        {{
            "characters": [
                {{
                    "name": "Character's full name",
                    "role": "protagonist/antagonist/supporting",
                    "description": "Physical and personality description",
                    "background": "Character's backstory",
                    "motivation": "What drives this character",
                    "arc": "How the character changes throughout the story"
                }},
                // More characters...
            ]
        }}

        Create at least one protagonist, one antagonist, and 2-3 supporting characters.
        Only include the JSON object in your response, no other text.
        """
        return prompt

    def _create_chapter_prompt(self, title: str, genre: str, outline: Dict[str, Any],
                              characters: Dict[str, Any], chapter_num: int, total_chapters: int,
                              story_description: str = "") -> str:
        """Create a prompt for generating a chapter."""
        # Convert data to string representations for the prompt
        outline_str = json.dumps(outline, indent=2)
        characters_str = json.dumps(characters, indent=2)

        # Add the story description if provided
        story_guidance = ""
        if story_description:
            story_guidance = f"""
            Additionally, keep in mind this story description from the author:
            {story_description}

            Make sure your chapter aligns with this vision.
            """

        prompt = f"""
        I need you to write Chapter {chapter_num} of {total_chapters} for a {genre} story titled "{title}".

        Here is the outline of the story:
        {outline_str}

        And here are the characters:
        {characters_str}
        {story_guidance}

        This is chapter {chapter_num} out of {total_chapters}, so consider where we are in the overall story arc.

        Please write a complete, engaging chapter with proper pacing, dialogue, description, and character development.
        Write the chapter directly, not as JSON. Start with a chapter title, then the content.
        Aim for approximately 1500-2000 words for this chapter.

        Format your response as markdown, with the chapter title as an H1 header (# Chapter Title),
        and use formatting like **bold**, *italic*, and > blockquote where appropriate.
        """
        return prompt

    def setup_steps(self):
        """Set up the workflow steps."""
        # Required abstract method implementation
        pass
