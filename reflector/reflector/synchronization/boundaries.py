# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Synchronization boundary definitions.

Defines the types and structures for synchronization boundaries — the
points in execution at which autonomous progress pauses and awaits human
review. Corresponds to synchronization.tex.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class BoundaryType(str, Enum):
    """Classification of synchronization boundary triggers."""

    MILESTONE = "milestone"       # Halts at a governance milestone
    RECURSION_LIMIT = "recursion_limit"  # Halts when recursion depth is reached
    DRIFT_ALERT = "drift_alert"   # Halts when drift exceeds threshold
    SCOPE_VIOLATION = "scope_violation"  # Halts on out-of-scope action
    MANUAL = "manual"             # Explicit human-requested pause


class SynchronizationBoundary(BaseModel):
    """A synchronization boundary — a point where execution pauses for review.

    Boundaries enforce the core reflector principle: autonomous execution
    must be bounded and human-reviewable at defined intervals.
    """

    id: str = Field(description="Unique boundary identifier.")
    name: str = Field(description="Human-readable boundary name.")
    boundary_type: BoundaryType = Field(
        default=BoundaryType.MILESTONE,
        description="What triggered this boundary.",
    )
    description: str = Field(
        default="",
        description="Why this boundary exists and what it protects.",
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether human approval is required to cross this boundary.",
    )
    active: bool = Field(
        default=True,
        description="Whether this boundary is currently blocking progression.",
    )

    @classmethod
    def example_boundaries(cls) -> list["SynchronizationBoundary"]:
        """Return example synchronization boundaries aligned with the paper."""
        return [
            cls(
                id="SB-001",
                name="Post-scaffold review",
                boundary_type=BoundaryType.MILESTONE,
                description=(
                    "Review point after initial package scaffold is complete. "
                    "Human reviews directory topology and CLI interface."
                ),
                requires_approval=True,
                active=True,
            ),
            cls(
                id="SB-002",
                name="Recursion depth limit",
                boundary_type=BoundaryType.RECURSION_LIMIT,
                description="Execution halts when recursion depth reaches the configured limit.",
                requires_approval=True,
                active=False,
            ),
            cls(
                id="SB-003",
                name="Drift threshold exceeded",
                boundary_type=BoundaryType.DRIFT_ALERT,
                description=(
                    "Execution halts when the audit drift score exceeds 0.3, "
                    "indicating significant deviation from the milestone target."
                ),
                requires_approval=True,
                active=False,
            ),
        ]
