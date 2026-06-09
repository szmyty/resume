<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# TODO — Publication Completion Roadmap

Canonical execution checklist from publication-ready state through release, archival indexing, discoverability, and ecosystem integration.

## Current objective

1. Finish the paper
2. Finish publication validation
3. Publish Reflector

---

## Release blockers (must complete before publication is considered complete)

### Phase 1 — Publication Readiness

Key artifacts: [`audits/publication-readiness-summary.md`](./audits/publication-readiness-summary.md), [`audits/publication-readiness.md`](./audits/publication-readiness.md), [`.github/workflows/paper-quality.yml`](./.github/workflows/paper-quality.yml), [`scripts/validate-metadata.py`](./scripts/validate-metadata.py), [`paper/figures/prompts/`](./paper/figures/prompts/)

- [ ] Final paper audit passes
- [x] All GitHub Actions passing
- [x] Figure reproducibility issues resolved
- [x] Prompt preservation complete
- [x] Metadata validation passes
- [ ] Final PDF review completed
- [ ] Final magazine review completed
- [ ] GitHub Release created

### Phase 2 — DOI and Archival Preservation

Key artifacts: [`.zenodo.json`](./.zenodo.json), [`CITATION.cff`](./CITATION.cff), [`metadata/publication.yaml`](./metadata/publication.yaml)

- [ ] Create Zenodo record
- [ ] Connect GitHub Release to Zenodo
- [ ] Generate DOI
- [ ] Verify DOI resolves correctly
- [ ] Add DOI badge to README
- [ ] Add DOI to CITATION.cff
- [ ] Add DOI to publication metadata

### Phase 3 — ORCID Synchronization

Key artifacts: [`CITATION.cff`](./CITATION.cff), [`metadata/authors.yaml`](./metadata/authors.yaml), [`metadata/publication.yaml`](./metadata/publication.yaml)

- [ ] Verify ORCID profile
- [ ] Add publication to ORCID
- [ ] Verify DOI synchronization
- [ ] Verify citation metadata appears correctly

### Phase 4 — arXiv Submission

Key artifacts: [`paper/00README.json`](./paper/00README.json), [`audits/arxiv-validation.md`](./audits/arxiv-validation.md), [`specs/publication/arxiv-publication.spec.md`](./specs/publication/arxiv-publication.spec.md)

- [ ] Confirm arXiv author eligibility
- [ ] Determine endorsement requirements
- [ ] Submit arXiv package
- [ ] Verify metadata
- [ ] Verify PDF rendering
- [ ] Verify references
- [ ] Verify figures
- [ ] Record arXiv identifier
- [ ] Add arXiv badge to README

### Phase 5 — Repository Publication

Key artifacts: [`.github/workflows/release-paper.yml`](./.github/workflows/release-paper.yml), [`.github/workflows/pages.yml`](./.github/workflows/pages.yml), [`release/`](./release/)

- [ ] Create GitHub Release
- [ ] Upload canonical artifacts
- [ ] Upload checksums
- [ ] Verify release notes
- [ ] Verify Pages deployment

---

## Post-publication enhancements (non-blocking)

### Phase 6 — Visibility and Discovery

Key artifacts: [`README.md`](./README.md), [`docs/`](./docs/), [`metadata/publication.yaml`](./metadata/publication.yaml), [`docs/huggingface.md`](./docs/huggingface.md)

- [ ] Portfolio integration
- [ ] GitHub profile integration
- [ ] Website integration
- [ ] OpenAlex indexing investigation
- [ ] Semantic Scholar indexing investigation
- [ ] Google Scholar discoverability investigation
- [ ] Hugging Face mirror evaluation

### Phase 7 — Communication Artifacts

Linked deliverable context: [`README.md`](./README.md), [`docs/index.html`](./docs/index.html), [`audits/publication-readiness-summary.md`](./audits/publication-readiness-summary.md)

#### LinkedIn Post — Research Paper

Create a publication announcement focused on:

- publication journey
- recursive systems
- synchronization
- articulation
- learning through building
- systems thinking

Avoid:

- hype
- exaggerated claims
- AI evangelism

Tone:

- reflective
- thoughtful
- humble
- technically grounded

#### LinkedIn Post — Visual Companion Magazine

Create a separate publication announcement focused on:

- visual communication
- accessibility
- transforming complexity into understanding
- educational design
- knowledge compression

Avoid:

- self-promotion
- marketing language
- clickbait

Tone:

- creative
- reflective
- educational

Deliverables:

- [ ] Paper announcement draft
- [ ] Magazine announcement draft

### Phase 8 — Future Work

Reference artifacts: [`ROADMAP.md`](./ROADMAP.md), [`docs/research/`](./docs/research/)

- [ ] Reflector visual companion expansion
- [ ] Article series
- [ ] Conference submissions
- [ ] Talks
- [ ] Videos
- [ ] Future papers
- [ ] Visual synapse integrations
- [ ] Educational adaptations

---

## Acceptance Criteria

- [x] TODO.md exists
- [x] Publication workflow is documented end-to-end
- [x] DOI workflow is documented
- [x] ORCID workflow is documented
- [x] arXiv workflow is documented
- [x] Communication deliverables are defined
- [x] Future work is preserved without competing with publication completion

---

## Notes

- Source of completed checkmarks above: `audits/publication-readiness-summary.md` and current repository state checks.
- Keep this file updated as the single publication completion tracker.
