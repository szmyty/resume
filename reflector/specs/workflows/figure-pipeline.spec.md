---
title: Figure Pipeline Specification
version: 0.1.0
status: draft
category:
  - workflows
  - figures
  - synchronization
tags:
  - placeholders
  - manifests
  - recursive-replacement
---

# Purpose

Define a reusable and deterministic figure workflow from placeholder stabilization to publication-ready assets.

---

# Canonical Figure Pipeline

1. Update prompt history (`paper/figures/prompts/*.prompt.md`).
2. Produce candidate figure while preserving canonical filename and dimensions.
3. Synchronize figure state in `paper/figures/manifest.md`.
4. Reconcile canonical caption in `paper/figures/captions.md`.
5. Verify manuscript placement in `paper/sections/*.tex`.
6. Run figure/publication audits before continuation.

---

# Determinism Constraints

- Figure identity MUST remain stable across iterations.
- Prompt, state, caption, and placement records MUST converge before finalization.
- Placeholder-to-final transitions MUST be explicit in manifest state.

---

# Reuse Contract

Any publication repository using this blueprint should provide:
- a canonical figure registry,
- a caption registry,
- prompt lineage for recursive regeneration,
- an auditable readiness check.
