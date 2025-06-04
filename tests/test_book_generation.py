#!/usr/bin/env python3
"""
Test script for book generation using the FMUS-Write library.
"""
import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the package
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fmus_write import BookProject
from fmus_write.workflows.registry import WorkflowRegistry

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test book generation with FMUS-Write")
    parser.add_argument("--title", default="The Enchanted Forest", help="Book title")
    parser.add_argument("--genre", default="Fantasy", help="Book genre")
    parser.add_argument("--provider", default="gemini", help="LLM provider to use")
    parser.add_argument("--model", help="LLM model to use (provider specific)")
    parser.add_argument("--api-key", help="API key for the LLM provider")
    parser.add_argument("--structure", default="short_story", choices=["novel", "novella", "short_story"], help="Structure type")
    parser.add_argument("--template", default="Three-Act Structure", help="Story template")
    parser.add_argument("--output", default="generated_book.md", help="Output file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set API key from environment variable if not provided
    api_key = args.api_key
    if not api_key and args.provider:
        env_var = f"{args.provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)
        if not api_key:
            logger.warning(f"No API key provided and {env_var} environment variable not found")

    # Register and list available workflows
    registry = WorkflowRegistry()
    registry.load_workflows()
    logger.info(f"Available workflows: {registry.list_registered_workflows()}")

    try:
        # Create a book project
        logger.info(f"Creating book project: {args.title} ({args.genre})")
        project = BookProject(
            title=args.title,
            genre=args.genre,
            structure_type=args.structure,
            template=args.template,
            api_key=api_key,
            provider=args.provider,
            model=args.model
        )

        # Generate content
        logger.info("Generating content...")
        content = project.generate(workflow_type="complete_book")

        # Export content
        output_path = args.output
        logger.info(f"Exporting content to {output_path}...")
        project.export(output_path, format="markdown")

        logger.info("Book generation completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error generating book: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
