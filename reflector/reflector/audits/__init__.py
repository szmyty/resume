# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""reflector audits package.

Implements the reflective audit pipeline described in reflective_auditing.tex.
Provides four-stage audit execution: event capture, invariant validation,
drift detection, and audit trail append.
"""

from reflector.audits.pipeline import AuditPipeline

__all__ = ["AuditPipeline"]
