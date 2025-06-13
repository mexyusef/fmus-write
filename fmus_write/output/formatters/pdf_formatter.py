from typing import Dict, Any, Optional
import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from ..formatter import OutputFormatter


class PDFFormatter(OutputFormatter):
    """Formatter for PDF output."""

    def __init__(self):
        super().__init__("pdf")
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom styles for PDF generation."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='BookTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=36,
            alignment=TA_CENTER
        ))

        # Chapter title style
        self.styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=24,
            spaceBefore=24,
            keepWithNext=True
        ))

        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            keepWithNext=True
        ))

        # Normal text style
        self.styles.add(ParagraphStyle(
            name='BookText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=6,
            spaceAfter=6
        ))

    def format(self, data: Dict[str, Any]) -> list:
        """Format the data for PDF generation.

        Args:
            data: The data to format

        Returns:
            A list of flowable objects for ReportLab
        """
        self.logger.info("Formatting data for PDF")

        # Extract key elements
        title = data.get("title", "Untitled")
        author = data.get("author", "Anonymous")
        genre = data.get("genre", "")
        theme = data.get("theme", "")
        summary = data.get("summary", "")
        chapters = data.get("final_chapters", [])

        # Create the document structure
        story = []

        # Title page
        story.append(Paragraph(title, self.styles['BookTitle']))
        story.append(Paragraph(f"By {author}", self.styles['Italic']))
        story.append(Spacer(1, 0.5 * inch))

        if genre:
            story.append(Paragraph(f"Genre: {genre}", self.styles['BookText']))

        if theme:
            story.append(Paragraph(f"Theme: {theme}", self.styles['BookText']))

        # Add a page break after title page
        story.append(PageBreak())

        # Table of Contents
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(name='TOCHeading1', fontSize=14, leading=16),
            ParagraphStyle(name='TOCHeading2', fontSize=12, leading=14, leftIndent=20)
        ]
        story.append(Paragraph("Table of Contents", self.styles['ChapterTitle']))
        story.append(toc)
        story.append(PageBreak())

        # Summary section if available
        if summary:
            story.append(Paragraph("Summary", self.styles['ChapterTitle']))
            story.append(Paragraph(summary, self.styles['BookText']))
            story.append(PageBreak())

        # Chapters
        if chapters:
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                chapter_content = chapter.get("content", "")

                # Add chapter title with bookmark for TOC
                story.append(Paragraph(chapter_title, self.styles['ChapterTitle']))

                # Process chapter content - split by paragraphs
                paragraphs = chapter_content.split("\n\n")
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, self.styles['BookText']))
                        story.append(Spacer(1, 0.1 * inch))

                # Add page break after each chapter
                story.append(PageBreak())

        return story

    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to a PDF file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format the content
        story = self.format(data)

        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            title=data.get("title", "Untitled"),
            author=data.get("author", "Anonymous")
        )

        # Build the PDF
        doc.build(story)

        self.logger.info(f"Wrote PDF content to {output_path}")
        return output_path
