"""CLI entry point for Agent Forge."""
import click
from dotenv import load_dotenv
from rich.console import Console

from .agents.base import AgentError
from .orchestrator import Pipeline

console = Console()


@click.command()
@click.argument("idea", required=False)
@click.option("--output", "-o", default="output", help="Output directory for generated project")
@click.option("--max-reviews", "-r", default=3, type=click.IntRange(1, 5), help="Max review iterations (1-5)")
def main(idea: str | None, output: str, max_reviews: int):
    """🔥 Agent Forge — Turn an idea into shippable code.

    Pass your idea as an argument, or omit it for interactive mode.

    Examples:

        agent-forge "Build a todo app with Next.js and Supabase"

        agent-forge "Create a REST API for a bookstore" -o bookstore-api

        agent-forge -r 1  # Single review pass (faster)
    """
    load_dotenv()

    if not idea:
        idea = console.input("[bold cyan]💡 Describe your project idea:[/bold cyan]\n> ")

    if not idea.strip():
        console.print("[red]No idea provided. Exiting.[/red]")
        raise SystemExit(1)

    pipeline = Pipeline(output_dir=output, max_review_iterations=max_reviews)
    try:
        pipeline.run(idea)
    except (AgentError, ValueError) as e:
        console.print(f"\n[bold red]✗ Pipeline failed:[/bold red] {e}")
        raise SystemExit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
