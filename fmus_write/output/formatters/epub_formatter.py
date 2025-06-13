from typing import Dict, Any, Optional
import os
import logging
from ebooklib import epub
from ..formatter import OutputFormatter


class EPUBFormatter(OutputFormatter):
    """Formatter for EPUB output."""

    def __init__(self):
        super().__init__("epub")

    def format(self, data: Dict[str, Any]) -> epub.EpubBook:
        """Format the data as an EPUB book.

        Args:
            data: The data to format

        Returns:
            An EpubBook object
        """
        self.logger.info("Formatting data as EPUB")

        # Extract key elements
        title = data.get("title", "Untitled")
        author = data.get("author", "Anonymous")
        genre = data.get("genre", "")
        theme = data.get("theme", "")
        summary = data.get("summary", "")
        chapters = data.get("final_chapters", [])

        # Create a new EPUB book
        book = epub.EpubBook()
        
        # Set metadata
        book.set_title(title)
        book.set_language('en')
        book.add_author(author)
        if genre:
            book.add_metadata('DC', 'subject', genre)

        # Create chapters
        epub_chapters = []
        toc = []
        spine = ['nav']

        # Add summary chapter if it exists
        if summary:
            summary_chapter = epub.EpubHtml(title='Summary', file_name='summary.xhtml')
            summary_content = f"<h1>Summary</h1><p>{summary}</p>"
            if theme:
                summary_content += f"<p><strong>Theme:</strong> {theme}</p>"
            summary_chapter.set_content(summary_content)
            book.add_item(summary_chapter)
            epub_chapters.append(summary_chapter)
            toc.append(summary_chapter)
            spine.append(summary_chapter)

        # Add content chapters
        if chapters:
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                chapter_content = chapter.get("content", "")
                
                # Create EPUB chapter
                epub_chapter = epub.EpubHtml(
                    title=chapter_title,
                    file_name=f'chapter_{i+1}.xhtml'
                )
                
                # Format content as HTML
                html_content = f"<h1>{chapter_title}</h1>"
                html_content += f"<div>{chapter_content}</div>"
                epub_chapter.set_content(html_content)
                
                # Add chapter to book
                book.add_item(epub_chapter)
                epub_chapters.append(epub_chapter)
                toc.append(epub_chapter)
                spine.append(epub_chapter)

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define Table of Contents
        book.toc = toc
        
        # Add spine
        book.spine = spine
        
        return book

    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to an EPUB file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format the content
        epub_book = self.format(data)

        # Write to file
        epub.write_epub(output_path, epub_book)

        self.logger.info(f"Wrote EPUB content to {output_path}")
        return output_path 