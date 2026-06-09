---
title: Recursive Workflow Blueprints
version: 0.1.0
status: draft
category:
  - workflows
  - blueprints
  - reuse
tags:
  - section-writing
  - synchronization-checkpoints
  - publication-validation
---

# Purpose

Capture reusable workflow blueprints extracted from reflector's stabilized publication system.

---

# Blueprint Catalog

## 1) Section Writing Blueprint
- edit semantic source (`paper/sections/`)
- avoid renderer-specific coupling
- validate against active specs before publication

## 2) Placeholder-First Stabilization Blueprint
- begin with explicit placeholder assets
- preserve stable names and dimensions
- converge toward final assets with manifest state transitions

## 3) Recursive Figure Replacement Blueprint
- iterate prompt → candidate → review → synchronized replacement
- enforce prompt/manifest/caption/placement consistency

## 4) Synchronization Checkpoint Blueprint
- record spec alignment, artifact state, and audit verdict
- require explicit continuation decision for recursion

## 5) Publication Validation Blueprint
- build with deterministic orchestration (`scripts/build-paper.sh`, `.latexmkrc`)
- reconcile metadata/manifests/audits before release/deploy

---

# Selection Guidance

Choose the smallest blueprint that satisfies current issue scope, then recurse only when checkpoint evidence supports continuation.
