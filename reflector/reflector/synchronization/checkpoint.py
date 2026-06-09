# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Synchronization checkpoint evaluator.

Evaluates the current synchronization boundary state and renders
a human-readable status panel. Corresponds to synchronization.tex.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reflector.synchronization.boundaries import SynchronizationBoundary


class SynchronizationCheckpoint:
    """Evaluates synchronization boundaries and presents state for human review.

    The checkpoint is the primary interface between autonomous execution and
    human governance. It surfaces which boundaries are active, why they were
    triggered, and what approval is required to proceed.
    """

    def __init__(self) -> None:
        # Use example boundaries as the initial scaffold state.
        self._boundaries: list[SynchronizationBoundary] = (
            SynchronizationBoundary.example_boundaries()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        boundary_id: str | None,
        console: Console,
    ) -> None:
        """Evaluate a specific boundary or all active boundaries."""
        if boundary_id:
            boundary = self._find(boundary_id)
            if boundary is None:
                console.print(
                    f"[red]No boundary found with id:[/red] {boundary_id!r}"
                )
                return
            self._render_boundary(boundary, console)
        else:
            active = [b for b in self._boundaries if b.active]
            if not active:
                console.print(
                    Panel(
                        "[green]No active synchronization boundaries.[/green]\n"
                        "Execution may proceed autonomously within governance contract.",
                        title="Synchronization Status",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"[yellow]{len(active)} active synchronization boundary/boundaries "
                        "require human review before execution can proceed.[/yellow]",
                        title="Synchronization Status",
                        border_style="yellow",
                    )
                )
                for boundary in active:
                    self._render_boundary(boundary, console)

    def list_boundaries(self, console: Console) -> None:
        """Print all registered synchronization boundaries."""
        table = Table(
            title="Synchronization Boundaries",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Active")
        table.add_column("Approval Required")

        for b in self._boundaries:
            active_str = "[yellow]Yes[/yellow]" if b.active else "[green]No[/green]"
            approval_str = "[red]Yes[/red]" if b.requires_approval else "No"
            table.add_row(b.id, b.name, b.boundary_type.value, active_str, approval_str)

        console.print(table)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find(self, boundary_id: str) -> SynchronizationBoundary | None:
        for b in self._boundaries:
            if b.id == boundary_id:
                return b
        return None

    @staticmethod
    def _render_boundary(boundary: SynchronizationBoundary, console: Console) -> None:
        color = "yellow" if boundary.active else "green"
        status = "ACTIVE — awaiting human review" if boundary.active else "Inactive"
        console.print(
            Panel(
                f"[bold]{boundary.name}[/bold]\n\n"
                f"{boundary.description}\n\n"
                f"[dim]Type:[/dim] {boundary.boundary_type.value}\n"
                f"[dim]Status:[/dim] {status}\n"
                f"[dim]Approval required:[/dim] {boundary.requires_approval}",
                title=f"Boundary {boundary.id}",
                border_style=color,
            )
        )
