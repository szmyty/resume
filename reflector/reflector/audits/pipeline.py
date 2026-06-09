# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Reflective audit pipeline.

Implements the four-stage audit pipeline described in reflective_auditing.tex:

Stage 1 — Event Capture:      Intercept agent actions and record state.
Stage 2 — Invariant Validation: Check structural, behavioural, governance invariants.
Stage 3 — Drift Detection:    Compare current state to milestone target.
Stage 4 — Audit Trail Append: Append signed entries to the immutable audit log.

This scaffold provides the architecture and interfaces. Concrete event
sources and invariant definitions are plugged in as adapters.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reflector.schemas.audit import (
    AuditEntry,
    AuditReport,
    CheckResult,
    InvariantResult,
)


# ---------------------------------------------------------------------------
# Built-in invariants
# ---------------------------------------------------------------------------

_DEFAULT_INVARIANTS: list[dict] = [
    {
        "id": "INV-001",
        "name": "no_infra_modifications",
        "description": "Agent must not modify infrastructure files.",
    },
    {
        "id": "INV-002",
        "name": "test_coverage_maintained",
        "description": "Test coverage must not drop below the configured threshold.",
    },
    {
        "id": "INV-003",
        "name": "governance_trail_complete",
        "description": "All milestone approvals must be recorded in the audit trail.",
    },
]

# Drift threshold above which an alert is raised.
_DRIFT_ALERT_THRESHOLD = 0.3


class AuditPipeline:
    """Executes the four-stage reflective audit pipeline.

    This class is the primary entry point for reflective auditing. It runs
    each stage in sequence and assembles an :class:`AuditReport`.

    Usage::

        pipeline = AuditPipeline(verbose=True)
        report = pipeline.run()
        pipeline.print_report(report, console)
    """

    def __init__(self, verbose: bool = False) -> None:
        self._verbose = verbose
        self._entries: list[AuditEntry] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> AuditReport:
        """Execute all four audit stages and return an :class:`AuditReport`."""
        # Stage 1 — Event Capture
        events = self._stage_event_capture()

        # Stage 2 — Invariant Validation
        validated = self._stage_invariant_validation(events)

        # Stage 3 — Drift Detection
        entries = self._stage_drift_detection(validated)

        # Stage 4 — Audit Trail Append
        return self._stage_audit_trail_append(entries)

    @staticmethod
    def print_report(report: AuditReport, console: Console) -> None:
        """Render an audit report to the terminal."""
        result_color = {
            CheckResult.PASS: "green",
            CheckResult.WARN: "yellow",
            CheckResult.FAIL: "red",
            CheckResult.SKIP: "dim",
        }.get(report.overall_result, "white")

        console.print(
            Panel(
                f"[{result_color}]Overall result: {report.overall_result.value}[/{result_color}]\n\n"
                f"Entries:     {report.total_entries}\n"
                f"Pass:        {report.pass_count}\n"
                f"Warn:        {report.warn_count}\n"
                f"Fail:        {report.fail_count}\n"
                f"Drift alerts:{report.drift_alerts}\n"
                f"Max drift:   {report.max_drift_score:.3f}",
                title=f"Audit Report — {report.generated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                border_style=result_color,
            )
        )

        if report.recommendations:
            table = Table(
                title="Recommendations",
                show_header=False,
                box=None,
                padding=(0, 1),
            )
            table.add_column("", style="dim")
            table.add_column("")
            for i, rec in enumerate(report.recommendations, 1):
                table.add_row(f"{i}.", rec)
            console.print(table)

    # ------------------------------------------------------------------
    # Pipeline stages (private)
    # ------------------------------------------------------------------

    def _stage_event_capture(self) -> list[dict]:
        """Stage 1: Capture agent events.

        In the scaffold, returns representative synthetic events. In a
        production integration this would intercept real agent actions.
        """
        if self._verbose:
            _info("Stage 1 — Event Capture")

        return [
            {
                "action": "package_scaffold",
                "target": "reflector/",
                "agent_id": "reflector-cli",
                "milestone": "M1",
                "phase": "scaffold",
            },
            {
                "action": "cli_entrypoint_created",
                "target": "reflector/cli/main.py",
                "agent_id": "reflector-cli",
                "milestone": "M1",
                "phase": "scaffold",
            },
            {
                "action": "schema_definitions_created",
                "target": "reflector/schemas/",
                "agent_id": "reflector-cli",
                "milestone": "M1",
                "phase": "scaffold",
            },
        ]

    @staticmethod
    def _stage_invariant_validation(events: list[dict]) -> list[dict]:
        """Stage 2: Validate governance invariants against captured events."""
        for event in events:
            results: list[InvariantResult] = []
            for inv in _DEFAULT_INVARIANTS:
                # Scaffold: all invariants pass for now.
                results.append(
                    InvariantResult(
                        id=inv["id"],
                        name=inv["name"],
                        result=CheckResult.PASS,
                    )
                )
            event["invariants"] = results
            event["scope_check"] = CheckResult.PASS
        return events

    @staticmethod
    def _stage_drift_detection(events: list[dict]) -> list[dict]:
        """Stage 3: Compute drift score and flag alerts."""
        for event in events:
            # Scaffold: drift is zero for all scaffold-phase events.
            event["drift_score"] = 0.0
            event["drift_alert"] = event["drift_score"] > _DRIFT_ALERT_THRESHOLD
        return events

    @staticmethod
    def _stage_audit_trail_append(events: list[dict]) -> AuditReport:
        """Stage 4: Assemble signed audit entries and build the report."""
        entries: list[AuditEntry] = []
        now = datetime.now(tz=timezone.utc)

        for event in events:
            entries.append(
                AuditEntry(
                    timestamp=now,
                    agent_id=event.get("agent_id", "unknown"),
                    action=event["action"],
                    target=event.get("target", ""),
                    scope_check=event.get("scope_check", CheckResult.PASS),
                    invariants_checked=event.get("invariants", []),
                    drift_score=event.get("drift_score", 0.0),
                    drift_alert=event.get("drift_alert", False),
                    milestone=event.get("milestone", ""),
                    phase=event.get("phase", ""),
                )
            )

        pass_count = sum(
            1 for e in entries if e.scope_check == CheckResult.PASS and not e.drift_alert
        )
        fail_count = sum(1 for e in entries if e.scope_check == CheckResult.FAIL)
        warn_count = sum(1 for e in entries if e.drift_alert and not e.scope_check == CheckResult.FAIL)
        drift_alerts = sum(1 for e in entries if e.drift_alert)
        max_drift = max((e.drift_score for e in entries), default=0.0)

        overall = CheckResult.PASS
        recommendations: list[str] = []

        if fail_count:
            overall = CheckResult.FAIL
            recommendations.append(
                "Investigate scope violations before proceeding to the next milestone."
            )
        elif warn_count or drift_alerts:
            overall = CheckResult.WARN
            recommendations.append(
                "Review drift alerts and ensure execution remains within governance bounds."
            )
        else:
            recommendations.append(
                "All invariants passed. Proceed to synchronization checkpoint for human review."
            )

        return AuditReport(
            generated_at=now,
            entries=entries,
            total_entries=len(entries),
            pass_count=pass_count,
            warn_count=warn_count,
            fail_count=fail_count,
            max_drift_score=max_drift,
            drift_alerts=drift_alerts,
            overall_result=overall,
            recommendations=recommendations,
        )


def _info(msg: str) -> None:
    print(f"[audit] {msg}")
