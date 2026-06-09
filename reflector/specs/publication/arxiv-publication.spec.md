---
title: arXiv Publication Adapter Concept Specification
version: 0.1.0
status: draft
category:
  - publication
  - arxiv
  - adapters
tags:
  - 00readme
  - deterministic-build
  - compiler-abstraction
---

# Purpose

Capture reusable architectural concepts from the modern arXiv `00README` publication model as a reflector-compatible adapter specification.

---

# Extracted Concepts

The arXiv publication model demonstrates:
- declarative compilation manifests
- explicit source declarations
- compiler abstraction
- deterministic orchestration
- reproducibility-oriented metadata
- explicit post-processing controls

These concepts SHOULD be adopted architecturally without cloning arXiv internals.

---

# arXiv-Oriented Manifest Concepts

An arXiv adapter SHOULD support declaration of:
- compiler pipeline (e.g., `pdflatex`, `latex` toolchain variants)
- source usage classification (`toplevel`, `include`, `ignore`)
- deterministic processing choices
- build metadata (toolchain version, output rules)
- optional post-processing directives

---

# Deterministic Philosophy

The adapter SHOULD eliminate:
- hidden local assumptions
- implicit source guessing
- non-reproducible build behavior

The adapter SHOULD preserve:
- explicit orchestration inputs
- stable artifact expectations
- repeatable publication builds

---

# Relationship to reflector

This specification aligns with existing reflector publication structure:
- `paper/paper.tex` as orchestration entrypoint
- `.latexmkrc` + scripts as deterministic build infrastructure
- GitHub Actions workflows for repeatable CI publication behavior

---

# Non-Goals

This specification does not:
- mirror arXiv implementation details one-to-one
- implement full arXiv submission automation
- replace current build scripts immediately
