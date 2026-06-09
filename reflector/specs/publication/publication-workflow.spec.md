---
title: Deterministic Publication Workflow Specification
version: 0.1.0
status: draft
category:
  - publication
  - workflow
  - orchestration
tags:
  - pipeline
  - deterministic
  - reproducibility
  - artifacts
---

# Purpose

Define the publication workflow abstraction that transforms semantic source content into reproducible renderer artifacts through manifest-driven orchestration.

---

# Workflow Model

```text
semantic content
    ↓
publication manifest
    ↓
renderer target
    ↓
generated artifact
```

---

# Workflow Phases

1. **Source Declaration**
   - enumerate canonical semantic inputs
   - classify input usage and inclusion boundaries

2. **Manifest Resolution**
   - resolve renderer target and compiler profile
   - resolve deterministic build parameters

3. **Compilation Orchestration**
   - execute explicit compilation pipeline
   - capture build metadata and artifacts

4. **Post-Processing**
   - apply optional deterministic post-processing steps
   - prepare final target bundle

5. **Verification**
   - validate artifact presence and reproducibility expectations

---

# Deterministic Guarantees

The workflow SHOULD guarantee:
- explicit inputs and outputs
- stable artifact naming
- reproducible orchestration behavior
- inspectable build metadata

The workflow MUST avoid opaque behavior that depends on local machine guesswork.

---

# Repository Alignment

reflector currently provides foundational workflow components:
- build orchestration script: `scripts/build-paper.sh`
- LaTeX build configuration: `.latexmkrc`
- publication automation workflows: `.github/workflows/build-paper.yml`, `.github/workflows/pages.yml`

This specification formalizes those patterns as reusable publication architecture.
