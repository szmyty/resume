---
title: Publication Manifest Architecture
version: 0.1.0
status: draft
category:
  - publication
  - orchestration
  - reproducibility
tags:
  - manifest
  - deterministic-build
  - renderer-targets
  - metadata
---

# Purpose

Define a reusable, renderer-agnostic publication manifest model that separates semantic source content from rendering orchestration.

---

# Scope

This specification defines:
- manifest structure and required keys
- deterministic compilation intent
- source classification and ordering
- build metadata capture
- renderer target declarations

This specification does not define renderer implementation details.

---

# Core Principles

- Manifest-driven orchestration over implicit build behavior.
- Deterministic publication outputs from explicit inputs.
- Semantic content as canonical source material.
- Renderer configuration as replaceable infrastructure.

---

# Conceptual Manifest Model

```yaml
publication:
  manifest_version: 1
  renderer: arxiv
  process:
    compiler: pdflatex
    deterministic: true
  sources:
    - path: paper.tex
      usage: toplevel
    - path: sections/
      usage: include
  metadata:
    texlive: "2025"
    postprocess: []
```

---

# Source Classification

Sources SHOULD be classified using semantic intent:
- `toplevel`: primary compilation entrypoints
- `include`: semantic source inputs used by entrypoints
- `ignore`: present in repository but excluded from compilation

Source ordering MUST be explicit when order affects output determinism.

---

# Deterministic Build Requirements

Publication manifests SHOULD capture:
- compiler target
- compilation mode
- source declarations
- renderer target
- build metadata (toolchain versions, post-processing switches)

Manifest processing MUST avoid implicit source discovery that changes output unpredictably.

---

# Repository Alignment

Current reflector layout maps naturally to this model:
- canonical entrypoint: `paper/paper.tex`
- semantic content: `paper/sections/`
- metadata layer: `paper/macros/metadata.tex`
- style/render layer: `paper/styles/reflector.sty`
- build orchestration: `.latexmkrc`, `scripts/build-paper.sh`
