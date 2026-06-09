# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Milestone schemas.

Defines typed milestone definitions that serve as synchronization boundaries
in the recursive execution workflow. Corresponds to milestone_execution.tex.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MilestoneStatus(str, Enum):
    """Lifecycle status of a milestone."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETE = "complete"


class MilestoneValidation(BaseModel):
    """Validation criteria that must pass before a milestone is approved."""

    tests_pass: bool = Field(default=True)
    coverage_threshold: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Minimum test coverage percentage required.",
    )
    lint_clean: bool = Field(default=False)
    custom_checks: list[str] = Field(
        default_factory=list,
        description="Additional validation check identifiers.",
    )


class MilestoneDefinition(BaseModel):
    """A governance milestone — a bounded synchronization point in the workflow.

    Milestones act as mandatory human-review checkpoints. Autonomous execution
    halts at each milestone boundary until a human approves progression.
    """

    id: str = Field(description="Unique milestone identifier (e.g. 'M1').")
    name: str = Field(description="Human-readable milestone name.")
    description: str = Field(default="", description="Milestone purpose and scope.")
    validation: MilestoneValidation = Field(default_factory=MilestoneValidation)
    status: MilestoneStatus = Field(default=MilestoneStatus.PENDING)
    phase: int = Field(
        default=1,
        ge=1,
        description="Execution phase this milestone belongs to.",
    )

    @classmethod
    def example_milestones(cls) -> list["MilestoneDefinition"]:
        """Return example milestone definitions aligned with the paper."""
        return [
            cls(
                id="M1",
                name="Scaffold complete",
                description="Package topology and CLI entry point established.",
                validation=MilestoneValidation(tests_pass=True, lint_clean=True),
                phase=1,
            ),
            cls(
                id="M2",
                name="Synchronization layer operational",
                description="Checkpoint evaluation and boundary detection functional.",
                validation=MilestoneValidation(
                    tests_pass=True, coverage_threshold=60, lint_clean=True
                ),
                phase=2,
            ),
            cls(
                id="M3",
                name="Audit pipeline complete",
                description="All four audit stages produce structured output.",
                validation=MilestoneValidation(
                    tests_pass=True, coverage_threshold=70, lint_clean=True
                ),
                phase=3,
            ),
        ]
