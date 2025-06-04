"""
Main CLI implementation for FMUS-Write.
"""

import os
import sys
import logging
import typer
from typing import Optional, List
from rich.console import Console
from rich.logging import RichHandler
from rich import print as rprint

# Import directly from modules to avoid circular imports
from fmus_write.models.story import StoryStructure
from fmus_write.models.character import Character
from fmus_write.models.world import World

# Set up CLI app
app = typer.Typer(
    name="fmus-write",
    help="AI-assisted content creation tool for writing",
    add_completion=False
)

# Console for rich output
console = Console()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("fmus_write")

# Version information
__version__ = "0.0.1"

@app.command("version")
def version():
    """Show the version of FMUS-Write."""
    rprint(f"FMUS-Write version: [bold green]{__version__}[/bold green]")


@app.command("generate")
def generate(
    title: str = typer.Option(..., help="Title of the book"),
    genre: str = typer.Option(..., help="Genre of the book"),
    output: str = typer.Option("book.md", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, help="API key for the AI service"),
    provider: str = typer.Option("openai", help="AI provider (openai, anthropic)"),
    model: Optional[str] = typer.Option(None, help="Model to use"),
    workflow: str = typer.Option("complete_book", help="Workflow type to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Generate a book with the given parameters."""
    # Set up logging level based on verbose flag
    if verbose:
        logger.setLevel(logging.DEBUG)

    # Extract API key from environment if not provided
    if api_key is None:
        if provider.lower() == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif provider.lower() == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")

    if api_key is None:
        rprint("[bold red]Error:[/bold red] No API key provided. Please provide an API key or set the appropriate environment variable.")
        sys.exit(1)

    # Determine the model if not provided
    if model is None:
        if provider.lower() == "openai":
            model = "gpt-4"
        elif provider.lower() == "anthropic":
            model = "claude-3-opus-20240229"

    with console.status(f"[bold green]Generating content for '{title}'...[/bold green]", spinner="dots"):
        try:
            # Import these here to avoid circular imports
            from fmus_write.output.manager import OutputManager
            from fmus_write.workflows.registry import WorkflowRegistry

            # Create story structure
            story = StoryStructure(title=title, genre=genre)

            # Set up workflow registry
            workflow_registry = WorkflowRegistry()
            workflow_registry.load_workflows()

            # Create workflow
            try:
                workflow = workflow_registry.create_workflow(
                    workflow_type=workflow,
                    name=f"{title}_{workflow}",
                    config={
                        "api_key": api_key,
                        "provider": provider,
                        "model": model
                    }
                )
            except ValueError as e:
                rprint(f"[bold red]Error:[/bold red] {str(e)}")
                rprint("[yellow]Available workflows:[/yellow]")
                for wf in workflow_registry.list_registered_workflows():
                    rprint(f"  - {wf}")
                sys.exit(1)

            # Prepare input data
            input_data = {
                "title": title,
                "genre": genre,
                "story": story.to_dict(),
                "characters": [],
                "world": {}
            }

            # Execute workflow
            rprint("[bold green]Generating content...[/bold green]")
            generated_content = workflow.execute(input_data)

            # Export content
            output_manager = OutputManager()
            output_manager.export(generated_content, output_path=output)

            rprint(f"[bold green]Successfully generated and exported to:[/bold green] {output}")

        except Exception as e:
            rprint(f"[bold red]Error generating content:[/bold red] {str(e)}")
            if verbose:
                console.print_exception()
            sys.exit(1)


@app.command("config")
def config(
    key: str = typer.Option(..., help="Configuration key to set"),
    value: str = typer.Option(..., help="Value to set for the key"),
    global_config: bool = typer.Option(False, "--global", help="Apply to global configuration")
):
    """Set configuration options."""
    config_dir = os.path.expanduser("~/.fmus-write") if global_config else "./.fmus-write"
    os.makedirs(config_dir, exist_ok=True)

    config_file = os.path.join(config_dir, "config.json")

    import json

    # Load existing config
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config_data = {}

    # Update config
    config_data[key] = value

    # Save config
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    rprint(f"[bold green]Updated configuration:[/bold green] {key}={value}")


@app.command("export")
def export(
    input_file: str = typer.Option(..., help="Input JSON file with content"),
    output_file: str = typer.Option(..., help="Output file path"),
    format: str = typer.Option("markdown", help="Output format (markdown, html, text, json, epub)")
):
    """Export content to different formats."""
    from fmus_write.output.manager import OutputManager
    import json

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Export the data
        output_manager = OutputManager()
        output_path = output_manager.export(data, output_path=output_file, format_type=format)

        rprint(f"[bold green]Successfully exported to:[/bold green] {output_path}")

    except Exception as e:
        rprint(f"[bold red]Error exporting content:[/bold red] {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except Exception as e:
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
