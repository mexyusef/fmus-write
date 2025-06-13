from typing import Dict, Any, Optional
import os
import logging
from ..formatter import OutputFormatter


class HTMLFormatter(OutputFormatter):
    """Formatter for HTML output."""

    def __init__(self):
        super().__init__("html")
        
    def format(self, data: Dict[str, Any]) -> str:
        """Format the data as HTML.

        Args:
            data: The data to format

        Returns:
            The formatted content as an HTML string
        """
        self.logger.info("Formatting data as HTML")

        # Extract key elements
        title = data.get("title", "Untitled")
        author = data.get("author", "Anonymous")
        genre = data.get("genre", "")
        theme = data.get("theme", "")
        summary = data.get("summary", "")
        chapters = data.get("final_chapters", [])

        # Build the HTML content with modern styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --text-color: #333;
            --bg-color: #fff;
            --accent-color: #e74c3c;
            --light-bg: #f5f5f5;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: var(--secondary-color);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        h1 {{
            font-size: 2.5em;
            text-align: center;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
        }}
        
        h2 {{
            font-size: 1.8em;
            border-bottom: 1px solid var(--primary-color);
            padding-bottom: 5px;
        }}
        
        .author {{
            text-align: center;
            font-style: italic;
            margin-bottom: 2em;
        }}
        
        .metadata {{
            background-color: var(--light-bg);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 2em;
        }}
        
        .summary {{
            background-color: var(--light-bg);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 2em;
            font-style: italic;
        }}
        
        .chapter {{
            margin-bottom: 3em;
        }}
        
        .chapter-content {{
            text-align: justify;
        }}
        
        .toc {{
            background-color: var(--light-bg);
            padding: 15px;
            border-radius: 5px;
            margin: 2em 0;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 20px;
        }}
        
        .toc a {{
            text-decoration: none;
            color: var(--primary-color);
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="author">By {author}</div>
"""

        # Add metadata if available
        if genre or theme:
            html_content += '    <div class="metadata">\n'
            if genre:
                html_content += f'        <p><strong>Genre:</strong> {genre}</p>\n'
            if theme:
                html_content += f'        <p><strong>Theme:</strong> {theme}</p>\n'
            html_content += '    </div>\n'

        # Add table of contents
        html_content += '    <div class="toc">\n'
        html_content += '        <h2>Table of Contents</h2>\n'
        html_content += '        <ul>\n'
        
        if summary:
            html_content += '            <li><a href="#summary">Summary</a></li>\n'
            
        if chapters:
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                html_content += f'            <li><a href="#chapter-{i+1}">{chapter_title}</a></li>\n'
                
        html_content += '        </ul>\n'
        html_content += '    </div>\n'

        # Add summary if available
        if summary:
            html_content += '    <div class="summary">\n'
            html_content += '        <h2 id="summary">Summary</h2>\n'
            html_content += f'        <p>{summary}</p>\n'
            html_content += '    </div>\n'

        # Add chapters
        if chapters:
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                chapter_content = chapter.get("content", "")
                
                # Format chapter content with paragraphs
                formatted_content = ""
                paragraphs = chapter_content.split("\n\n")
                for para in paragraphs:
                    if para.strip():
                        formatted_content += f"        <p>{para}</p>\n"
                
                html_content += f'    <div class="chapter">\n'
                html_content += f'        <h2 id="chapter-{i+1}">{chapter_title}</h2>\n'
                html_content += f'        <div class="chapter-content">\n{formatted_content}        </div>\n'
                html_content += '    </div>\n'

        # Close HTML tags
        html_content += '</body>\n</html>'

        return html_content

    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write the formatted data to an HTML file.

        Args:
            data: The data to format
            output_path: The path to write to

        Returns:
            The path to the written file
        """
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format the content
        html_content = self.format(data)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"Wrote HTML content to {output_path}")
        return output_path 