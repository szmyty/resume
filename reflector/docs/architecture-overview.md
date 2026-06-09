# Repository Architecture Overview

This document maps reflector's repository structure and synchronization architecture.

## Structure Map

- `paper/` — canonical manuscript source and publication assembly
- `paper/figures/` — figure files and synchronization registries
- `specs/` — specification contracts for workflows and publication architecture
- `reflector/` — synchronization/orchestration CLI package
- `scripts/` — deterministic build, validation, and audit scripts
- `.github/workflows/` — CI execution for build, release, and Pages deployment
- `docs/` — published documentation surface and research notes
- `audits/` — generated or maintained audit summaries/checkpoints

## Publication Architecture

reflector uses layered publication architecture:
- semantic content (`paper/sections/`)
- metadata layer (`paper/macros/metadata.tex`, `paper/config/title.tex`)
- render/style layer (`paper/styles/reflector.sty`)
- orchestration layer (`scripts/build-paper.sh`, workflows, `.latexmkrc`)

## Semantic/Render Separation

The repository keeps semantic writing and rendering concerns separated:
- semantic text stays in section-oriented manuscript files
- publication style and package decisions are isolated in style/config layers
- workflow scripts compile and publish without redefining manuscript semantics

## Specification Organization

Publication specifications are centered under `specs/publication/`, including:
- manifest architecture
- semantic content boundaries
- publication workflow model
- renderer abstraction
- arXiv publication orientation

Additional reusable extraction layers:
- `specs/workflows/` for recursive workflow and figure pipeline blueprints
- `specs/synchronization/` for checkpoint and boundary contracts
- `specs/repositories/` for portable publication repository architecture standards

## Workflow Organization

Workflow logic is distributed across:
- CLI orchestration (`reflector/`)
- shell/python scripts (`scripts/`)
- CI workflows (`.github/workflows/`)

This creates explicit execution boundaries between local automation and CI deployment.

## Synchronization Philosophy

Architecture decisions favor:
- explicit canonical sources
- deterministic transformations
- inspectable workflow boundaries
- low-ambiguity handoffs between humans, AI systems, and CI
