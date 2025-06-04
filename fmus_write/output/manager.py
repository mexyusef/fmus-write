"""
Output management for FMUS-Write.
"""

from typing import Dict, Any, Optional, List, BinaryIO, Union
import logging
import os
import json
import markdown
import tempfile
import shutil

logger = logging.getLogger(__name__)

try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False


class OutputManager:
    """Manager for formatting and exporting generated content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the output manager.

        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.formatters = {
            "markdown": self._format_markdown,
            "html": self._format_html,
            "text": self._format_text,
            "json": self._format_json,
            "epub": self._format_epub
        }

    def export(
        self,
        data: Dict[str, Any],
        output_path: str,
        format_type: str = "markdown",
        **kwargs
    ) -> str:
        """
        Export content to a file.

        Args:
            data: Content data to export
            output_path: Path to save the output
            format_type: Format type (markdown, html, text, json, epub)
            **kwargs: Additional format-specific options

        Returns:
            str: Path to the exported file

        Raises:
            ValueError: If the format is not supported
            IOError: If the file cannot be written
        """
        if format_type not in self.formatters:
            raise ValueError(f"Unsupported format: {format_type}")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Format the content
            content = self.formatters[format_type](data, **kwargs)

            # Write to file
            if isinstance(content, str):
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                # Binary content
                with open(output_path, "wb") as f:
                    f.write(content)

            logger.info(f"Exported content to {output_path} in {format_type} format")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting to {output_path}: {e}")
            raise

    def _format_markdown(self, data: Dict[str, Any], **kwargs) -> str:
        """
        Format data as Markdown.

        Args:
            data: Content data
            **kwargs: Additional options

        Returns:
            str: Formatted Markdown content
        """
        title = data.get("title", "Untitled")
        author = data.get("author", "Unknown Author")
        chapters = data.get("chapters", [])

        lines = [
            f"# {title}",
            f"*By {author}*",
            "",
        ]

        if "description" in data:
            lines.extend([data["description"], "", "---", ""])

        # Add table of contents if requested
        if kwargs.get("include_toc", True):
            lines.extend(["## Table of Contents", ""])
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                lines.append(f"{i+1}. [{chapter_title}](#{chapter_title.lower().replace(' ', '-')})")
            lines.extend(["", "---", ""])

        # Add chapters
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get("title", f"Chapter {i+1}")
            chapter_content = chapter.get("content", "")

            lines.extend([
                f"## {chapter_title}",
                "",
                chapter_content,
                "",
                "---",
                ""
            ])

        return "\n".join(lines)

    def _format_html(self, data: Dict[str, Any], **kwargs) -> str:
        """
        Format data as HTML.

        Args:
            data: Content data
            **kwargs: Additional options

        Returns:
            str: Formatted HTML content
        """
        # First convert to Markdown
        md_content = self._format_markdown(data, **kwargs)

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])

        # Add basic styling
        title = data.get("title", "Untitled")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ text-align: center; margin-bottom: 0.5em; }}
        h2 {{ border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 2em 0; }}
        .author {{ text-align: center; font-style: italic; margin-bottom: 2em; }}
        .toc {{ background: #f8f9fa; padding: 1em; border-radius: 5px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    def _format_text(self, data: Dict[str, Any], **kwargs) -> str:
        """
        Format data as plain text.

        Args:
            data: Content data
            **kwargs: Additional options

        Returns:
            str: Formatted text content
        """
        title = data.get("title", "Untitled")
        author = data.get("author", "Unknown Author")
        chapters = data.get("chapters", [])

        lines = [
            title.upper(),
            f"By {author}",
            "",
            "=" * len(title),
            "",
        ]

        if "description" in data:
            lines.extend([data["description"], "", "=" * 40, ""])

        # Add chapters
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get("title", f"Chapter {i+1}")
            chapter_content = chapter.get("content", "")

            lines.extend([
                chapter_title.upper(),
                "-" * len(chapter_title),
                "",
                chapter_content,
                "",
                "=" * 40,
                ""
            ])

        return "\n".join(lines)

    def _format_json(self, data: Dict[str, Any], **kwargs) -> str:
        """
        Format data as JSON.

        Args:
            data: Content data
            **kwargs: Additional options

        Returns:
            str: Formatted JSON content
        """
        indent = kwargs.get("indent", 2)
        return json.dumps(data, indent=indent)

    def _format_epub(self, data: Dict[str, Any], **kwargs) -> bytes:
        """
        Format data as EPUB.

        Args:
            data: Content data
            **kwargs: Additional options

        Returns:
            bytes: EPUB file content

        Raises:
            ImportError: If ebooklib is not installed
        """
        if not EPUB_AVAILABLE:
            raise ImportError("ebooklib is required for EPUB export. Install with 'pip install ebooklib'")

        title = data.get("title", "Untitled")
        author = data.get("author", "Unknown Author")
        chapters = data.get("chapters", [])

        # Create a new EPUB book
        book = epub.EpubBook()

        # Set metadata
        book.set_title(title)
        book.set_language('en')
        book.add_author(author)

        # Create chapters
        epub_chapters = []
        toc_items = []

        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get("title", f"Chapter {i+1}")
            chapter_content = chapter.get("content", "")

            # Convert markdown to HTML for the chapter
            chapter_html = markdown.markdown(chapter_content)

            # Create chapter
            epub_chapter = epub.EpubHtml(
                title=chapter_title,
                file_name=f"chapter_{i+1}.xhtml",
                content=f"<h1>{chapter_title}</h1>\n{chapter_html}"
            )

            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
            toc_items.append(epub.Link(f"chapter_{i+1}.xhtml", chapter_title, f"chapter{i+1}"))

        # Add navigation files
        book.toc = toc_items
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define the reading order
        book.spine = ['nav'] + epub_chapters

        # Create a temporary file to save the EPUB
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            epub.write_epub(tmp_file.name, book)

            # Read the file content
            with open(tmp_file.name, 'rb') as f:
                content = f.read()

            # Delete the temporary file
            os.unlink(tmp_file.name)

        return content

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Update the output manager configuration.

        Args:
            config: New configuration options
        """
        self.config.update(config)
        logger.debug("Updated output manager configuration")

    def register_formatter(self, format_type: str, formatter_func) -> None:
        """
        Register a custom formatter.

        Args:
            format_type: Format identifier
            formatter_func: Formatter function
        """
        self.formatters[format_type] = formatter_func
        logger.debug(f"Registered custom formatter for {format_type}")

    def get_supported_formats(self) -> List[str]:
        """
        Get a list of supported export formats.

        Returns:
            List[str]: Supported format types
        """
        return list(self.formatters.keys())
