# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""reflector CLI — bounded recursive synchronization and governance prototype.

Entry point for the `reflector` command. Provides subcommands for:
- run        Execute a reflector workflow
- synchronize  Run a synchronization checkpoint
- audit      Run the reflective audit pipeline
- milestone  Inspect or advance milestone state
- status     Show current reflector status
- sync       Short alias for synchronize
- huggingface  Inspect Hugging Face integration scaffold status
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reflector import __version__
from reflector.integrations.huggingface import HuggingFaceIntegrationConfig
from reflector.orchestration.milestone import MilestoneOrchestrator
from reflector.synchronization.checkpoint import SynchronizationCheckpoint
from reflector.audits.pipeline import AuditPipeline
from reflector.workflows.runner import WorkflowRunner

app = typer.Typer(
    name="reflector",
    help=(
        "reflector: a bounded recursive synchronization and governance prototype.\n\n"
        "Embodies recursive issue orchestration, milestone synchronization, "
        "reflective auditing, and human synchronization boundaries."
    ),
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"reflector {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: FBT001
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """reflector — bounded recursive synchronization prototype."""


@app.command()
def run(
    milestone_id: str | None = typer.Option(
        None,
        "--milestone",
        "-m",
        help="Milestone identifier to run the workflow against.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate the workflow without executing side-effects.",
    ),
) -> None:
    """Execute a bounded reflector workflow.

    Runs the MVP flow:
    1. Load milestone definition
    2. Generate scoped tasks
    3. Execute bounded recursive pass
    4. Generate reflective audit
    5. Pause at synchronization boundary
    """
    console.rule("[bold blue]reflector Run")

    runner = WorkflowRunner(dry_run=dry_run)
    runner.execute(milestone_id=milestone_id)


@app.command()
def synchronize(
    boundary_id: str | None = typer.Argument(
        None,
        help="Synchronization boundary identifier to check or advance.",
    ),
    list_boundaries: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all registered synchronization boundaries.",
    ),
) -> None:
    """Run a synchronization checkpoint.

    Evaluates the current synchronization boundary state and pauses
    for human review if required. Corresponds to the synchronization
    layer described in synchronization.tex.
    """
    console.rule("[bold cyan]Synchronization Checkpoint")

    _run_synchronization(boundary_id=boundary_id, list_boundaries=list_boundaries)


@app.command(name="sync")
def sync(
    boundary_id: str | None = typer.Argument(
        None,
        help="Synchronization boundary identifier to check or advance.",
    ),
    list_boundaries: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all registered synchronization boundaries.",
    ),
) -> None:
    """Alias for `reflector synchronize`."""
    console.rule("[bold cyan]Synchronization Checkpoint")
    _run_synchronization(boundary_id=boundary_id, list_boundaries=list_boundaries)


@app.command()
def audit(
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the audit report (JSON). Defaults to stdout.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print detailed audit stage output.",
    ),
) -> None:
    """Run the reflective audit pipeline.

    Executes the four-stage audit pipeline:
    1. Event capture
    2. Invariant validation
    3. Drift detection
    4. Audit trail append

    Corresponds to reflective_auditing.tex.
    """
    console.rule("[bold yellow]Reflective Audit Pipeline")

    pipeline = AuditPipeline(verbose=verbose)
    report = pipeline.run()

    if output:
        import json
        import pathlib

        out_path = pathlib.Path(output)
        out_path.write_text(json.dumps(report.model_dump(), indent=2, default=str))
        console.print(f"[green]Audit report written to:[/green] {out_path}")
    else:
        pipeline.print_report(report, console)


@app.command()
def milestone(
    milestone_id: str | None = typer.Argument(
        None,
        help="Milestone identifier to inspect or advance.",
    ),
    list_milestones: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all milestones and their current status.",
    ),
    advance: bool = typer.Option(
        False,
        "--advance",
        "-a",
        help="Advance the milestone to the next phase (requires approval).",
    ),
) -> None:
    """Inspect or manage milestone state.

    Milestones act as governance checkpoints — bounded synchronization
    boundaries that require human approval before execution proceeds.

    Corresponds to milestone_execution.tex.
    """
    console.rule("[bold magenta]Milestone Orchestration")

    orchestrator = MilestoneOrchestrator()

    if list_milestones:
        orchestrator.list_milestones(console)
        return

    if advance and milestone_id:
        orchestrator.advance(milestone_id=milestone_id, console=console)
        return

    orchestrator.inspect(milestone_id=milestone_id, console=console)


@app.command()
def status() -> None:
    """Show current reflector status.

    Displays an overview of:
    - Active workflow state
    - Pending synchronization boundaries
    - Audit trail summary
    - Milestone progress
    """
    console.rule("[bold green]reflector Status")

    runner = WorkflowRunner()
    state = runner.get_status()

    table = Table(title="reflector Status", show_header=True, header_style="bold")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Detail")

    for component, info in state.items():
        table.add_row(component, info.get("status", "—"), info.get("detail", ""))

    console.print(table)

    console.print(
        Panel(
            "[dim]reflector is a bounded synchronization prototype.\n"
            "All recursive execution halts at milestone boundaries for human review.[/dim]",
            title="About",
            border_style="dim",
        )
    )


@app.command()
def huggingface(
    metadata_path: str = typer.Option(
        "metadata/repository.yaml",
        "--metadata",
        "-m",
        help="Path to canonical repository metadata YAML.",
    ),
    check_sdk: bool = typer.Option(
        False,
        "--check-sdk",
        help="Check whether `huggingface_hub` is installed in this environment.",
    ),
) -> None:
    """Inspect Hugging Face integration scaffold status."""
    import pathlib

    console.rule("[bold white]Hugging Face Integration")
    try:
        config = HuggingFaceIntegrationConfig.from_repository_metadata(
            pathlib.Path(metadata_path)
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc), param_hint="--metadata") from exc

    table = Table(title="Hugging Face Integration", show_header=True, header_style="bold")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Enabled", "yes" if config.enabled else "no")
    table.add_row("Space URL", str(config.space_url) if config.space_url else "N/A")

    if check_sdk:
        table.add_row(
            "SDK installed",
            "yes" if config.sdk_available() else "no (install reflector with huggingface extra)",
        )

    console.print(table)


def _run_synchronization(boundary_id: str | None, list_boundaries: bool) -> None:
    checkpoint = SynchronizationCheckpoint()
    if list_boundaries:
        checkpoint.list_boundaries(console)
        return
    checkpoint.evaluate(boundary_id=boundary_id, console=console)
