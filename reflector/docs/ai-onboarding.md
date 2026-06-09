# AI Onboarding and Synchronization Guide

This guide provides deterministic orientation for AI systems working in reflector.

## Repository Philosophy

reflector is not just a manuscript directory; it is a specification-driven synchronization system for publication infrastructure.

AI agents should optimize for:
- deterministic edits
- explicit synchronization boundaries
- low-ambiguity workflow execution

## Synchronization Principles

1. Treat canonical files as sources of truth.
2. Keep semantic content separate from rendering infrastructure.
3. Prefer explicit manifests/specs over implicit assumptions.
4. Preserve stable file identities (especially figures and manuscript entrypoints).
5. Validate synchronization with existing audit/build workflows.

## Recursive Workflow Structure

reflector workflows are intentionally recursive:

```text
orient
  → edit
  → synchronize
  → audit
  → publish
  → re-orient
```

Each iteration should reduce drift and increase observability.

## Specification-Driven Execution

Before or during implementation, AI systems should align with `specs/`, especially `specs/publication/`.

Specs define:
- expected workflow behavior
- deterministic publication contracts
- semantic/render separation constraints

## Publication Architecture Orientation

Canonical publication path:
- manuscript entrypoint: `paper/paper.tex`
- metadata + title layering: `paper/macros/`, `paper/config/`
- style abstraction: `paper/styles/reflector.sty`
- build orchestration: `scripts/build-paper.sh` + workflows

## Figure Workflow Orientation

Figure synchronization has explicit registries:
- `paper/figures/manifest.md` for figure identity/state
- `paper/figures/captions.md` for caption truth
- `paper/sections/*.tex` for placement references

AI edits must preserve consistency across all three surfaces.

## Issue Orchestration Philosophy

When resolving issues:
- minimize unrelated change scope
- preserve deterministic repository contracts
- document orientation-level changes in canonical docs
- prioritize maintainability and recursive clarity over one-off shortcuts
