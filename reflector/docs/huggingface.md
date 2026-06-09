# Hugging Face publication readiness

This document records the recommended Hugging Face cross-publishing strategy for reflector.

## Current repository state

reflector already has the core ingredients needed for later Hugging Face publication:

- canonical repository metadata in [`metadata/repository.yaml`](../metadata/repository.yaml)
- citation and publication metadata in [`CITATION.cff`](../CITATION.cff) and [`publication.json`](../publication.json)
- a public documentation and PDF surface on GitHub Pages
- a bounded CLI check via `reflector huggingface --check-sdk`
- a future-facing card scaffold in [`README_HF.md`](../README_HF.md)

## Recommended publication strategy

### 1. Treat GitHub as the canonical source of truth

Keep manuscript source, specifications, metadata, and synchronization scripts in this repository. Hugging Face should mirror public-facing assets rather than becoming the authoritative editing surface.

### 2. Publish a Space before publishing a model card

reflector is a research and workflow system, not a trained model. The most natural first Hugging Face surface is therefore a **Space** that links to:

- the paper PDF
- the GitHub Pages landing page
- the repository
- future demos or interactive workflow visualizations, such as architecture maps, audit walkthroughs, or synchronization lifecycle previews

That keeps the first Space focused on discovery and explorable research context rather than pretending reflector already ships a standalone model endpoint.

### 3. Use a dataset card only when artifacts exist

A dataset card should only be created if reflector later publishes structured traces, benchmark cases, synchronization logs, or reusable evaluation corpora.

### 4. Use a model card only for actual model artifacts

Do not publish a model card unless the repository begins distributing weights, adapters, or inference endpoints. Until then, the Hugging Face presence should describe the research system, not imply that reflector is itself a model release.

## Synchronization strategy

When Hugging Face publication begins, keep these boundaries explicit:

- **Canonical metadata:** `metadata/`, `publication.json`, `CITATION.cff`
- **Canonical research narrative:** `README.md`, `paper/README.md`, `docs/`
- **Hugging Face mirror surface:** derived card content adapted from [`README_HF.md`](../README_HF.md)
- **Verification path:** run `reflector huggingface --check-sdk` before publishing or updating the mirror

## Recommended repository mirroring workflow

1. Update canonical repository metadata and README content here first.
2. Build or verify the publication assets intended for external sharing.
3. Adapt [`README_HF.md`](../README_HF.md) into the Hugging Face Space or card README.
4. Link back to the canonical PDF, citation metadata, and GitHub Pages route.
5. Keep external mirrors descriptive and discoverable, but avoid splitting source-of-truth ownership across platforms.

## Minimum checklist before first Hugging Face publication

- [ ] GitHub Pages landing page is current
- [ ] `docs/reflector.pdf` is published from the latest paper build
- [ ] `CITATION.cff` and `publication.json` are up to date
- [ ] Hugging Face Space URL is added to `metadata/repository.yaml`
- [ ] `README_HF.md` is adapted for the target Hugging Face surface
- [ ] Public links between GitHub, Pages, and Hugging Face are reciprocal

## Practical recommendation

Use Hugging Face as a distribution and discovery layer for reflector, not as the primary authoring environment. That keeps the repository's publication architecture, synchronization boundaries, and auditability intact while still making the project easy to surface inside the Hugging Face ecosystem later.
