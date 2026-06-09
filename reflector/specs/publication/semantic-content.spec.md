---
title: Semantic Content Canonical Source Specification
version: 0.1.0
status: draft
category:
  - publication
  - semantics
  - content
tags:
  - canonical-source
  - portability
  - publisher-agnostic
---

# Purpose

Define semantic-first content principles that keep manuscript meaning stable, reusable, and publisher-independent across rendering targets.

---

# Canonical Source Principle

Canonical manuscript content MUST prioritize:
- semantic structure
- conceptual clarity
- reusable section composition
- portability across publication targets

Canonical source files MUST NOT be permanently coupled to one publisher format.

---

# Content Boundaries

Semantic content SHOULD live in content-oriented files such as:
- section files (`paper/sections/`)
- bibliography and references
- conceptual figures/diagrams

Rendering concerns SHOULD remain outside semantic content where possible.

---

# Separation Rules

Semantic content SHOULD be separated from:
- renderer-specific compilation options
- style/package configuration
- environment/toolchain metadata
- publication post-processing logic

Repository structures like `paper/macros/metadata.tex` and `paper/styles/reflector.sty` support this separation.

---

# Stability and Reuse

Semantic content SHOULD remain:
- stable across renderer changes
- reusable for multiple publication destinations
- reviewable independent of tooling details

Renderer migration SHOULD preserve semantic source continuity.

---

# Non-Goals

This specification does not require:
- immediate publisher-specific rewrites
- renderer implementation work
- a new document authoring platform
