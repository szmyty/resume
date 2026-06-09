# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Governance contract schemas.

Defines the typed governance contracts that constrain agent execution scope,
obligations, and milestone checkpoints. Corresponds to reflector_framework.tex.

Example YAML governance contract::

    scope:
      allowed_paths:
        - src/api/
        - tests/api/
      prohibited_paths:
        - infra/
        - .github/
    obligations:
      - emit_audit_events: true
      - halt_at_milestone: true
    recursion_limit: 5
    milestones:
      - id: M1
        name: Feature implementation complete
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScopeDefinition(BaseModel):
    """Defines the allowed and prohibited execution scope for an agent."""

    allowed_paths: list[str] = Field(
        default_factory=list,
        description="Paths the agent is permitted to modify.",
    )
    prohibited_paths: list[str] = Field(
        default_factory=list,
        description="Paths the agent must never modify.",
    )


class Obligation(BaseModel):
    """A single governance obligation (key-value constraint)."""

    key: str = Field(description="Obligation name.")
    value: Any = Field(description="Obligation value or flag.")


class GovernanceContract(BaseModel):
    """Governance contract binding an agent to a scoped, bounded execution context.

    Embodies the governance layer described in reflector_framework.tex:
    - Constrains execution to allowed_paths
    - Mandates audit event emission
    - Enforces milestone halt behaviour
    - Limits recursion depth
    """

    id: str = Field(default="default", description="Unique contract identifier.")
    scope: ScopeDefinition = Field(default_factory=ScopeDefinition)
    obligations: list[Obligation] = Field(
        default_factory=list,
        description="Governance obligations the agent must satisfy.",
    )
    recursion_limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum recursion depth before mandatory pause.",
    )

    @classmethod
    def default(cls) -> "GovernanceContract":
        """Return a safe default governance contract."""
        return cls(
            id="default",
            scope=ScopeDefinition(),
            obligations=[
                Obligation(key="emit_audit_events", value=True),
                Obligation(key="halt_at_milestone", value=True),
                Obligation(key="request_approval_for_out_of_scope", value=True),
            ],
            recursion_limit=5,
        )
