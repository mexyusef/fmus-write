import argparse
import json
import os
import logging
from typing import Dict, Any, Optional, List

from ..workflows import WorkflowRegistry
from ..output import OutputManager


class CLI:
    """Command-line interface for FMUS-Write."""

    def __init__(self):
        """Initialize the CLI."""
        self.parser = self._create_parser()
        self.output_manager = OutputManager()
        self.logger = logging.getLogger("fmus_write.cli")

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser.

        Returns:
            The configured argument parser
        """
        parser = argparse.ArgumentParser(
            description="FMUS-Write: AI-powered content creation for books and novels"
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # init command
        init_parser = subparsers.add_parser("init", help="Initialize a new project")
        init_parser.add_argument("title", help="Title of the book")
        init_parser.add_argument("--genre", help="Genre of the book", default="Fiction")
        init_parser.add_argument("--theme", help="Theme of the book")
        init_parser.add_argument("--llm", help="LLM provider to use", default="openai")
        init_parser.add_argument("--model", help="LLM model to use", default="gpt-4")

        # config command
        config_parser = subparsers.add_parser("config", help="Configure the project")
        config_parser.add_argument("--chapters", help="Number of chapters", type=int)
        config_parser.add_argument("--words-per-chapter", help="Words per chapter", type=int)
        config_parser.add_argument("--style", help="Writing style")
        config_parser.add_argument("--theme", help="Theme of the book")

        # generate command
        generate_parser = subparsers.add_parser("generate", help="Generate content")
        generate_parser.add_argument("--workflow", help="Workflow to use", default="complete_book")
        generate_parser.add_argument("--config", help="Path to configuration file")

        # export command
        export_parser = subparsers.add_parser("export", help="Export content")
        export_parser.add_argument("--format", help="Output format", default="markdown")
        export_parser.add_argument("--output", help="Output file path", required=True)

        return parser

    def run(self, args=None):
        """Run the CLI with the given arguments.

        Args:
            args: Command-line arguments (if None, uses sys.argv)
        """
        args = self.parser.parse_args(args)

        if args.command == "init":
            self.init_command(args)
        elif args.command == "config":
            self.config_command(args)
        elif args.command == "generate":
            self.generate_command(args)
        elif args.command == "export":
            self.export_command(args)
        else:
            self.parser.print_help()

    def init_command(self, args):
        """Handle the init command.

        Args:
            args: Parsed arguments
        """
        self.logger.info(f"Initializing project: {args.title}")

        # Create project configuration
        config = {
            "title": args.title,
            "genre": args.genre,
            "theme": args.theme,
            "llm": {
                "provider": args.llm,
                "model": args.model
            },
            "project_path": os.getcwd(),
            "created_at": None  # Will be set when saved
        }

        # Create project directory
        project_dir = args.title.lower().replace(" ", "_")
        os.makedirs(project_dir, exist_ok=True)

        # Save configuration
        config_path = os.path.join(project_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        self.logger.info(f"Project initialized in directory: {project_dir}")
        print(f"Project '{args.title}' initialized in directory: {project_dir}")

    def config_command(self, args):
        """Handle the config command.

        Args:
            args: Parsed arguments
        """
        # Find config file in current directory
        config_path = "config.json"
        if not os.path.exists(config_path):
            config_path = os.path.join(os.getcwd(), "config.json")
            if not os.path.exists(config_path):
                self.logger.error("No config.json found in current directory")
                print("Error: No config.json found in current directory")
                return

        # Load existing configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Update configuration
        if args.chapters is not None:
            config["chapter_count"] = args.chapters

        if args.words_per_chapter is not None:
            config["words_per_chapter"] = args.words_per_chapter

        if args.style is not None:
            config["style"] = args.style

        if args.theme is not None:
            config["theme"] = args.theme

        # Save updated configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        self.logger.info(f"Configuration updated: {config_path}")
        print(f"Configuration updated: {config_path}")

    def generate_command(self, args):
        """Handle the generate command.

        Args:
            args: Parsed arguments
        """
        # Load configuration
        config_path = args.config if args.config else "config.json"
        if not os.path.exists(config_path):
            config_path = os.path.join(os.getcwd(), "config.json")
            if not os.path.exists(config_path):
                self.logger.error("No config.json found")
                print("Error: No config.json found. Use --config to specify the path or run from project directory.")
                return

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Create and run workflow
        try:
            workflow = WorkflowRegistry.create(args.workflow)
            self.logger.info(f"Running workflow: {args.workflow}")
            print(f"Running workflow: {args.workflow}")

            result = workflow.run(config)

            # Save result
            result_path = os.path.join(os.path.dirname(config_path), "result.json")
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            self.logger.info(f"Generation complete. Result saved to: {result_path}")
            print(f"Generation complete. Result saved to: {result_path}")

        except Exception as e:
            self.logger.error(f"Error running workflow: {str(e)}")
            print(f"Error: {str(e)}")

    def export_command(self, args):
        """Handle the export command.

        Args:
            args: Parsed arguments
        """
        # Find result file
        result_path = "result.json"
        if not os.path.exists(result_path):
            result_path = os.path.join(os.getcwd(), "result.json")
            if not os.path.exists(result_path):
                self.logger.error("No result.json found")
                print("Error: No result.json found. Run the generate command first.")
                return

        # Load result data
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Export in requested format
        try:
            output_path = self.output_manager.export(data, args.output, args.format)
            if output_path:
                self.logger.info(f"Content exported to: {output_path}")
                print(f"Content exported to: {output_path}")
            else:
                self.logger.error(f"Failed to export in format: {args.format}")
                print(f"Error: Failed to export in format: {args.format}")
        except Exception as e:
            self.logger.error(f"Error exporting content: {str(e)}")
            print(f"Error: {str(e)}")


def main():
    """Main entry point for the CLI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run CLI
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
