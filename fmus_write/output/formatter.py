from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import os
import logging


class OutputFormatter(ABC):
    """Base class for output formatters."""

    def __init__(self, name: str):
        """Initialize the formatter.

        Args:
            name: The name of the formatter
        """
        self.name = name
        self.logger = logging.getLogger(f"fmus_write.output.{name}")

    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """Format the data into the target format.

        Args:
            data: The data to format

        Returns:
            The formatted content as a string
        """
        pass

    @abstractmethod
    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to a file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        pass


class MarkdownFormatter(OutputFormatter):
    """Formatter for Markdown output."""

    def __init__(self):
        super().__init__("markdown")

    def format(self, data: Dict[str, Any]) -> str:
        """Format the data as Markdown.

        Args:
            data: The data to format

        Returns:
            The formatted content as a Markdown string
        """
        self.logger.info("Formatting data as Markdown")

        # Extract key elements
        title = data.get("title", "Untitled")
        genre = data.get("genre", "")
        theme = data.get("theme", "")
        summary = data.get("summary", "")
        chapters = data.get("final_chapters", [])

        # Build the Markdown content
        md_content = f"# {title}\n\n"

        if genre or theme:
            md_content += "## About\n\n"
            if genre:
                md_content += f"**Genre:** {genre}\n\n"
            if theme:
                md_content += f"**Theme:** {theme}\n\n"

        if summary:
            md_content += "## Summary\n\n"
            md_content += f"{summary}\n\n"

        # Add chapters
        if chapters:
            for chapter in chapters:
                chapter_title = chapter.get("title", "Untitled Chapter")
                chapter_content = chapter.get("content", "")

                md_content += f"## {chapter_title}\n\n"
                md_content += f"{chapter_content}\n\n"

        return md_content

    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to a Markdown file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format the content
        md_content = self.format(data)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        self.logger.info(f"Wrote Markdown content to {output_path}")
        return output_path


class TextFormatter(OutputFormatter):
    """Formatter for plain text output."""

    def __init__(self):
        super().__init__("text")

    def format(self, data: Dict[str, Any]) -> str:
        """Format the data as plain text.

        Args:
            data: The data to format

        Returns:
            The formatted content as a plain text string
        """
        self.logger.info("Formatting data as plain text")

        # Extract key elements
        title = data.get("title", "Untitled")
        genre = data.get("genre", "")
        theme = data.get("theme", "")
        summary = data.get("summary", "")
        chapters = data.get("final_chapters", [])

        # Build the text content
        text_content = f"{title.upper()}\n\n"

        if genre or theme:
            if genre:
                text_content += f"Genre: {genre}\n"
            if theme:
                text_content += f"Theme: {theme}\n"
            text_content += "\n"

        if summary:
            text_content += "SUMMARY\n\n"
            text_content += f"{summary}\n\n"

        # Add chapters
        if chapters:
            for chapter in chapters:
                chapter_title = chapter.get("title", "Untitled Chapter")
                chapter_content = chapter.get("content", "")

                # Remove any markdown formatting
                chapter_content = chapter_content.replace("#", "")

                text_content += f"{chapter_title.upper()}\n\n"
                text_content += f"{chapter_content}\n\n"
                text_content += "* * *\n\n"

        return text_content

    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to a text file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format the content
        text_content = self.format(data)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        self.logger.info(f"Wrote text content to {output_path}")
        return output_path
