# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Audit entry and report schemas.

Defines the typed data structures for individual audit log entries and
aggregate audit reports produced by the reflective audit pipeline.
Corresponds to reflective_auditing.tex.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CheckResult(str, Enum):
    """Result of a validation check."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class InvariantResult(BaseModel):
    """Result of a single invariant check within an audit stage."""

    id: str = Field(description="Invariant identifier (e.g. 'INV-001').")
    name: str = Field(description="Short invariant name.")
    result: CheckResult = Field(default=CheckResult.PASS)
    detail: str = Field(default="", description="Optional detail or failure message.")


class AuditEntry(BaseModel):
    """A single signed audit log entry capturing one agent action.

    Corresponds to the audit trail append stage in reflective_auditing.tex.
    """

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    agent_id: str = Field(default="reflector-cli")
    action: str = Field(description="Action performed (e.g. 'file_write').")
    target: str = Field(default="", description="Resource targeted by the action.")
    scope_check: CheckResult = Field(default=CheckResult.PASS)
    invariants_checked: list[InvariantResult] = Field(default_factory=list)
    drift_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalised drift score (0.0 = no drift, 1.0 = maximal drift).",
    )
    drift_alert: bool = Field(
        default=False,
        description="True when drift_score exceeds the configured threshold.",
    )
    milestone: str = Field(default="", description="Active milestone identifier.")
    phase: str = Field(default="", description="Current execution phase label.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditReport(BaseModel):
    """Aggregate audit report produced after running the full audit pipeline."""

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    entries: list[AuditEntry] = Field(default_factory=list)
    total_entries: int = Field(default=0)
    pass_count: int = Field(default=0)
    warn_count: int = Field(default=0)
    fail_count: int = Field(default=0)
    max_drift_score: float = Field(default=0.0)
    drift_alerts: int = Field(default=0)
    overall_result: CheckResult = Field(default=CheckResult.PASS)
    recommendations: list[str] = Field(default_factory=list)
