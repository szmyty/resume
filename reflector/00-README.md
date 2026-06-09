# 00-README — Canonical Repository Orientation

This document is the canonical onboarding and synchronization layer for the reflector repository.

## Repository Overview

reflector is both a research manuscript repository and a synchronization system for deterministic publication workflows.

Core roles:
- semantic paper authoring
- publication orchestration
- specification-driven execution
- recursive synchronization and auditability

## Architecture Overview

Primary repository layers:
- `paper/` — canonical manuscript source and publication-facing LaTeX structure
- `paper/figures/` — figure assets plus figure synchronization infrastructure (`manifest.md`, `captions.md`)
- `specs/` — architecture and workflow specifications, including publication contracts
- `scripts/` — deterministic build and audit utilities
- `.github/workflows/` — CI orchestration for build, Pages, and release flows
- `docs/` — published/static documentation and research notes
- `audits/` — publication readiness and synchronization audit artifacts
- `reflector/` — CLI and synchronization runtime package

## Workflow Overview

High-level flow:

```text
semantic content
    ↓
specification + manifest alignment
    ↓
synchronization + audits
    ↓
publication orchestration
    ↓
generated artifacts
```

## Publication Overview

Canonical manuscript entrypoint: `paper/paper.tex`
Build orchestration: `scripts/build-paper.sh` + `.latexmkrc`
Publication metadata: `publication.json`, `release-manifest.json`, `CITATION.cff`

Main publication outputs:
- local/CI PDF artifacts
- GitHub Pages-hosted output in `docs/`
- release metadata for versioned publication workflow

## Synchronization Philosophy

reflector prioritizes:
- deterministic inputs and outputs
- explicit contracts over implicit behavior
- inspectable synchronization boundaries
- stable canonical sources with replaceable render layers

Synchronization objective: reduce ambiguity while keeping recursive work observable and maintainable.

## Specification Philosophy

Specifications in `specs/` define expected architecture and workflow behavior before or alongside implementation.

This keeps:
- execution contracts explicit
- workflow evolution reviewable
- recursive changes bounded by declared intent

## Recursive Workflow Orientation

reflector is designed for repeated authoring and synchronization cycles:
1. update semantic content or metadata
2. reconcile with specs/manifests
3. run synchronization and audits
4. produce publication artifacts
5. observe drift and iterate with explicit checkpoints

## Figure Workflow Orientation

Figure synchronization is deterministic and registry-driven:
- file-level truth and state in `paper/figures/manifest.md`
- caption truth in `paper/figures/captions.md`
- placement truth in `paper/sections/*.tex`
- consistency verification via `scripts/audit-publication-readiness.py`

## Pages and Deployment Overview

GitHub Actions workflows build publication artifacts and deploy Pages content from repository-managed sources.

Pages deployment role:
- stable public documentation/publication surface
- synchronized with CI outputs and repository metadata

## Publication Pipeline Overview

Publication pipeline is manifest/spec-aware and deterministic by design:
1. resolve canonical source + metadata
2. run orchestrated build workflow
3. validate artifact and synchronization integrity
4. publish/deploy artifacts with traceable metadata

For detailed subsystem references:
- `docs/publication-system-reference.md` — authoritative end-to-end publication lifecycle
- `docs/publication-workflow-reference.md` — workflow registry, triggers, ownership
- `docs/publication-artifact-reference.md` — artifact lifecycle, producers, consumers
- `docs/publication-lessons-learned.md` — lessons learned and future recommendations
- `docs/architecture-overview.md`
- `docs/workflows.md`
- `docs/publication-architecture.md`
- `docs/ai-onboarding.md`
