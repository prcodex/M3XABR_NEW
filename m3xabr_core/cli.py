"""Command-line interface for m3xabr-core.

Usage:
    m3xabr "your query here"
    m3xabr --lancedb /path/to/db "como está o IPCA?"
    m3xabr --debug "Itaú revisou Selic?"
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from m3xabr_core import Pipeline

app = typer.Typer(
    help="m3xabr-core: Brazilian intelligence agent CLI",
    no_args_is_help=True,
)
console = Console()


@app.command()
def query(
    query: Annotated[str, typer.Argument(help="The user query in pt-BR or en")],
    lancedb_path: Annotated[
        str,
        typer.Option(
            "--lancedb",
            "-d",
            help="Path to the LanceDB directory",
            envvar="M3XABR_LANCEDB",
        ),
    ] = "./lancedb_data",
    debug: Annotated[
        bool,
        typer.Option(
            "--debug", help="Show full pipeline state (classifier, routing, etc.)"
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output the full PipelineResult as JSON"),
    ] = False,
) -> None:
    """Run a single query through the pipeline."""
    # Validate env
    missing = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.environ.get("VOYAGE_API_KEY"):
        missing.append("VOYAGE_API_KEY")
    if missing:
        console.print(
            f"[red]Missing required env vars: {', '.join(missing)}[/red]"
        )
        console.print(
            "Set them in your shell or in a .env file (e.g., export ANTHROPIC_API_KEY=...)"
        )
        raise typer.Exit(1)

    if not Path(lancedb_path).exists():
        console.print(
            f"[yellow]Warning: LanceDB path {lancedb_path} does not exist. "
            "Pipeline will return empty retrieval.[/yellow]"
        )

    with console.status("[cyan]Running pipeline...[/cyan]"):
        pipeline = Pipeline(lancedb_path=lancedb_path)
        result = pipeline.run(query)

    if json_output:
        console.print(result.model_dump_json(indent=2, exclude_none=True))
        return

    console.print(
        Panel(
            result.response,
            title=f"[bold green]Response[/bold green] (score: {result.score:.1f}/10.0)",
            border_style="green",
        )
    )

    if debug:
        _print_debug(result)


def _print_debug(result) -> None:
    """Print the full pipeline state."""
    console.print("\n[bold]Classifier output:[/bold]")
    console.print(result.classifier_output.model_dump())

    console.print("\n[bold]Routing decision:[/bold]")
    console.print(result.routing_decision.model_dump())

    console.print("\n[bold]Retrieved docs:[/bold]")
    console.print(f"  Count: {result.retrieved_doc_count}")

    console.print("\n[bold]Agent blocks:[/bold]")
    console.print(f"  Count: {result.agent_blocks_count}")

    console.print("\n[bold]Token estimates:[/bold]")
    table = Table(show_header=False)
    table.add_row("System prompt (assembled)", f"{result.estimated_system_tokens:,}")
    table.add_row("Total input", f"{result.estimated_total_input_tokens:,}")
    console.print(table)

    console.print("\n[bold]Evaluation rubric:[/bold]")
    table = Table(show_header=True)
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    rs = result.evaluation.rubric_scores
    for field_name in (
        "grounding",
        "citation",
        "clarity",
        "completeness",
        "no_fabrication",
        "format_compliance",
    ):
        table.add_row(field_name, f"{getattr(rs, field_name):.1f}")
    table.add_row("[bold]Overall[/bold]", f"[bold]{result.evaluation.score:.1f}[/bold]")
    console.print(table)

    if result.regen_triggered:
        console.print("\n[yellow]Regen path was triggered[/yellow]")

    console.print("\n[bold]Timing:[/bold]")
    for actor, ms in result.timing_ms.items():
        console.print(f"  {actor}: {ms:.0f}ms")


@app.command()
def expertises(
    expertises_dir: Annotated[
        str,
        typer.Option("--dir", "-d", help="Path to expertises directory"),
    ] = "./expertises",
) -> None:
    """List available expertise files with their token estimates."""
    import yaml

    path = Path(expertises_dir)
    if not path.exists():
        console.print(f"[red]Directory not found: {path}[/red]")
        raise typer.Exit(1)

    table = Table(title="Expertise Inventory")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Tokens (est.)", justify="right")
    table.add_column("Description")

    for md_file in sorted(path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        rest = content[3:]
        end = rest.find("---")
        if end == -1:
            continue
        try:
            meta = yaml.safe_load(rest[:end]) or {}
        except yaml.YAMLError:
            continue
        body = rest[end + 3 :]
        est_tokens = len(body) // 4

        desc = meta.get("description", "").split("\n")[0][:60]
        table.add_row(
            meta.get("name", md_file.stem),
            meta.get("type", "?"),
            f"{est_tokens:,}",
            desc,
        )

    console.print(table)


if __name__ == "__main__":
    app()
