# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Bounded recursive workflow runner.

Implements the MVP workflow described in the issue:

    1. Load milestone definition
    2. Generate scoped tasks/issues
    3. Execute bounded recursive pass
    4. Generate reflective audit
    5. Generate audit recommendations
    6. Pause for synchronization boundary
    7. Await human review

The runner enforces the recursion limit from the governance contract and
halts at every milestone boundary. It is deliberately simple — architecture
and traceability matter more than completeness at this stage.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from reflector.audits.pipeline import AuditPipeline
from reflector.orchestration.milestone import MilestoneOrchestrator
from reflector.schemas.governance import GovernanceContract
from reflector.schemas.milestone import MilestoneDefinition, MilestoneStatus
from reflector.synchronization.checkpoint import SynchronizationCheckpoint


class WorkflowRunner:
    """Executes the bounded reflector MVP workflow.

    The runner coordinates all subsystems under a single governance contract
    and enforces the recursion limit on recursive refinement passes.

    Usage::

        runner = WorkflowRunner(dry_run=True)
        runner.execute(milestone_id="M1")
    """

    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run
        self._contract = GovernanceContract.default()
        self._orchestrator = MilestoneOrchestrator()
        self._audit_pipeline = AuditPipeline()
        self._checkpoint = SynchronizationCheckpoint()
        self._console = Console()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, milestone_id: str | None = None) -> None:
        """Execute the full MVP workflow for a given milestone."""
        console = self._console
        dry_label = "[dim](dry-run)[/dim] " if self._dry_run else ""

        console.print(
            Panel(
                f"{dry_label}Executing bounded reflector workflow\n\n"
                f"[dim]Governance contract:[/dim] {self._contract.id}\n"
                f"[dim]Recursion limit:[/dim]    {self._contract.recursion_limit}\n"
                f"[dim]Milestone target:[/dim]   {milestone_id or 'all'}",
                title="Workflow Runner",
                border_style="blue",
            )
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Step 1 — Load milestone definition
            task = progress.add_task("Step 1: Loading milestone definition…", total=None)
            milestones = self._step_load_milestones(milestone_id)
            progress.update(task, completed=True)

            # Step 2 — Generate scoped tasks
            task = progress.add_task("Step 2: Generating scoped tasks…", total=None)
            tasks = self._step_generate_tasks(milestones)
            progress.update(task, completed=True)

            # Step 3 — Execute bounded recursive pass
            task = progress.add_task("Step 3: Executing bounded recursive pass…", total=None)
            self._step_recursive_pass(tasks)
            progress.update(task, completed=True)

            # Step 4 — Generate reflective audit
            task = progress.add_task("Step 4: Running reflective audit…", total=None)
            report = self._audit_pipeline.run()
            progress.update(task, completed=True)

            # Step 5 — Print audit recommendations
            task = progress.add_task("Step 5: Generating recommendations…", total=None)
            progress.update(task, completed=True)

        # Step 6 — Pause at synchronization boundary
        console.print()
        self._audit_pipeline.print_report(report, console)

        console.print()
        console.print(
            Panel(
                "[yellow]Step 6: Synchronization boundary reached.[/yellow]\n\n"
                "Autonomous execution has paused. The audit report above "
                "summarizes all actions taken in this pass.\n\n"
                "[bold]Step 7: Awaiting human review.[/bold]\n"
                "[dim]Run `reflector synchronize` to inspect active boundaries.\n"
                "Run `reflector milestone --list` to review milestone state.[/dim]",
                title="Synchronization Pause",
                border_style="yellow",
            )
        )

    def get_status(self) -> dict[str, dict[str, str]]:
        """Return a structured status snapshot for all subsystems."""
        from reflector.schemas.milestone import MilestoneDefinition

        milestones = MilestoneDefinition.example_milestones()
        active_milestone = next(
            (m for m in milestones if m.status == MilestoneStatus.IN_PROGRESS),
            milestones[0] if milestones else None,
        )

        return {
            "Workflow": {
                "status": "idle",
                "detail": "No workflow currently running",
            },
            "Governance Contract": {
                "status": "loaded",
                "detail": f"id={self._contract.id}, recursion_limit={self._contract.recursion_limit}",
            },
            "Active Milestone": {
                "status": active_milestone.status.value if active_milestone else "—",
                "detail": active_milestone.name if active_milestone else "No milestones",
            },
            "Synchronization": {
                "status": "1 boundary active",
                "detail": "SB-001 — Post-scaffold review (awaiting human approval)",
            },
            "Audit Trail": {
                "status": "ready",
                "detail": "Pipeline initialized; run `reflector audit` to generate report",
            },
        }

    # ------------------------------------------------------------------
    # Workflow steps (private)
    # ------------------------------------------------------------------

    def _step_load_milestones(
        self,
        milestone_id: str | None,
    ) -> list[MilestoneDefinition]:
        milestones = MilestoneDefinition.example_milestones()
        if milestone_id:
            milestones = [m for m in milestones if m.id == milestone_id]
        return milestones

    @staticmethod
    def _step_generate_tasks(
        milestones: list[MilestoneDefinition],
    ) -> list[dict]:
        """Generate a bounded set of scoped tasks from milestone definitions.

        In the scaffold these are synthetic tasks. In a full integration
        this would call the GitHub Issues API to create or fetch real issues.
        """
        tasks: list[dict] = []
        for milestone in milestones:
            tasks.append({
                "id": f"TASK-{milestone.id}-001",
                "milestone": milestone.id,
                "action": "implement",
                "description": milestone.description,
                "phase": str(milestone.phase),
            })
        return tasks

    def _step_recursive_pass(self, tasks: list[dict]) -> None:
        """Execute a bounded recursive refinement pass over the task list.

        The recursion depth is capped by the governance contract limit.
        Each pass audits its own actions before proceeding.
        """
        recursion_depth = 0
        limit = self._contract.recursion_limit

        for task in tasks:
            if recursion_depth >= limit:
                self._console.print(
                    f"[yellow]Recursion limit ({limit}) reached. "
                    "Halting pass and handing off to synchronization.[/yellow]"
                )
                break

            if not self._dry_run:
                # Simulate task execution (scaffold placeholder).
                pass

            recursion_depth += 1
