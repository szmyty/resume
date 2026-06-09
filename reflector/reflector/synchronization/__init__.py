# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""reflector synchronization package.

Implements the synchronization layer described in synchronization.tex.
Provides checkpoint evaluation and boundary detection for the recursive
workflow engine.
"""

from reflector.synchronization.checkpoint import SynchronizationCheckpoint
from reflector.synchronization.boundaries import (
    BoundaryType,
    SynchronizationBoundary,
)

__all__ = [
    "SynchronizationCheckpoint",
    "BoundaryType",
    "SynchronizationBoundary",
]
