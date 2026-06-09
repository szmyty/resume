# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Milestone orchestrator.

Manages the lifecycle of governance milestones — bounded synchronization
checkpoints that require human approval before autonomous execution proceeds.
Corresponds to milestone_execution.tex.

The orchestrator:
- Loads milestone definitions
- Tracks milestone status transitions
- Enforces the halt-at-milestone obligation
- Surfaces pending approvals for human review
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reflector.schemas.milestone import MilestoneDefinition, MilestoneStatus


_STATUS_STYLE: dict[MilestoneStatus, str] = {
    MilestoneStatus.PENDING: "dim",
    MilestoneStatus.IN_PROGRESS: "blue",
    MilestoneStatus.AWAITING_REVIEW: "yellow",
    MilestoneStatus.APPROVED: "green",
    MilestoneStatus.REJECTED: "red",
    MilestoneStatus.COMPLETE: "green bold",
}


class MilestoneOrchestrator:
    """Orchestrates milestone lifecycle within governance bounds.

    Usage::

        orchestrator = MilestoneOrchestrator()
        orchestrator.list_milestones(console)
        orchestrator.advance("M1", console)
    """

    def __init__(self) -> None:
        # Scaffold: load example milestones. In a full implementation these
        # would be loaded from a YAML/JSON governance contract or GitHub Projects.
        self._milestones: dict[str, MilestoneDefinition] = {
            m.id: m for m in MilestoneDefinition.example_milestones()
        }
        # Mark M1 as in-progress for the scaffold demonstration.
        self._milestones["M1"].status = MilestoneStatus.IN_PROGRESS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_milestones(self, console: Console) -> None:
        """Render all milestones as a table."""
        table = Table(
            title="Milestones",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Phase")
        table.add_column("Status")

        for m in self._milestones.values():
            style = _STATUS_STYLE.get(m.status, "")
            table.add_row(
                m.id,
                m.name,
                str(m.phase),
                f"[{style}]{m.status.value}[/{style}]",
            )

        console.print(table)

    def inspect(
        self,
        milestone_id: str | None,
        console: Console,
    ) -> None:
        """Render detailed milestone information."""
        if milestone_id is None:
            console.print(
                "[yellow]No milestone ID provided. Use --list to see all milestones.[/yellow]"
            )
            return

        milestone = self._milestones.get(milestone_id)
        if milestone is None:
            console.print(f"[red]Milestone not found:[/red] {milestone_id!r}")
            return

        self._render_milestone(milestone, console)

    def advance(self, milestone_id: str, console: Console) -> None:
        """Attempt to advance a milestone to the next status.

        Advancement always requires human review when transitioning to
        APPROVED or COMPLETE — the orchestrator surfaces the approval
        requirement but does not auto-approve.
        """
        milestone = self._milestones.get(milestone_id)
        if milestone is None:
            console.print(f"[red]Milestone not found:[/red] {milestone_id!r}")
            return

        transitions: dict[MilestoneStatus, MilestoneStatus] = {
            MilestoneStatus.PENDING: MilestoneStatus.IN_PROGRESS,
            MilestoneStatus.IN_PROGRESS: MilestoneStatus.AWAITING_REVIEW,
            MilestoneStatus.AWAITING_REVIEW: MilestoneStatus.APPROVED,
            MilestoneStatus.APPROVED: MilestoneStatus.COMPLETE,
        }

        next_status = transitions.get(milestone.status)
        if next_status is None:
            console.print(
                f"[yellow]Milestone {milestone_id!r} is already in a terminal "
                f"state: {milestone.status.value}[/yellow]"
            )
            return

        # Enforce the synchronization boundary: AWAITING_REVIEW → APPROVED
        # requires explicit human action. In the scaffold we surface the
        # requirement and exit — the approval pathway is left for integration.
        if milestone.status == MilestoneStatus.AWAITING_REVIEW:
            console.print(
                Panel(
                    "[yellow]This milestone is awaiting human review.[/yellow]\n\n"
                    "The synchronization boundary requires a human approver to mark\n"
                    "this milestone as APPROVED before execution proceeds.\n\n"
                    "[dim]In a full integration this would open a GitHub review request.[/dim]",
                    title=f"Synchronization Boundary — {milestone_id}",
                    border_style="yellow",
                )
            )
            return

        milestone.status = next_status
        style = _STATUS_STYLE.get(next_status, "")
        console.print(
            f"[green]Milestone {milestone_id!r} advanced to:[/green] "
            f"[{style}]{next_status.value}[/{style}]"
        )
        self._render_milestone(milestone, console)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _render_milestone(milestone: MilestoneDefinition, console: Console) -> None:
        style = _STATUS_STYLE.get(milestone.status, "")
        validation_lines = (
            f"  tests_pass:          {milestone.validation.tests_pass}\n"
            f"  coverage_threshold:  {milestone.validation.coverage_threshold}%\n"
            f"  lint_clean:          {milestone.validation.lint_clean}"
        )
        console.print(
            Panel(
                f"[bold]{milestone.name}[/bold]\n\n"
                f"{milestone.description}\n\n"
                f"[dim]Phase:[/dim]  {milestone.phase}\n"
                f"[dim]Status:[/dim] [{style}]{milestone.status.value}[/{style}]\n\n"
                f"[dim]Validation criteria:[/dim]\n{validation_lines}",
                title=f"Milestone {milestone.id}",
                border_style=style or "white",
            )
        )
