# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Hugging Face integration scaffold.

Provides a provider-agnostic configuration surface for future model/dataset
and inference endpoint orchestration. Current behavior is intentionally bounded
to metadata inspection and environment readiness checks.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl


class HuggingFaceIntegrationConfig(BaseModel):
    """Canonical Hugging Face integration settings."""

    enabled: bool = False
    space_url: HttpUrl | None = None

    @classmethod
    def from_repository_metadata(cls, path: Path) -> "HuggingFaceIntegrationConfig":
        """Load integration configuration from `metadata/repository.yaml`."""
        metadata = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        hf = (
            metadata.get("future_integrations", {})
            .get("huggingface", {})
        )
        return cls(
            enabled=bool(hf.get("enabled", False)),
            space_url=hf.get("space_url"),
        )

    @staticmethod
    def sdk_available() -> bool:
        """Return whether optional Hugging Face SDK is installed."""
        try:
            import huggingface_hub  # noqa: F401
        except ImportError:
            return False
        return True
