<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Template Extraction Opportunities

Generated: 2026-06-03
Issue: Final Boss: Publication Platform Completion & Production Readiness

## High-Value Reusable Components

1. **Publication workflow template**
   - Source: `.github/workflows/publication.yml`
   - Reuse value: scoped validation/build/package/release orchestration for publication projects.

2. **Pages publication deployment template**
   - Source: `.github/workflows/pages.yml`
   - Reuse value: docs synchronization with publication route verification and fallback handling.

3. **Release packaging template**
   - Source: `scripts/stage-publication-release.py`
   - Reuse value: deterministic checksums + release manifest generation.

4. **Metadata consistency validation template**
   - Source: `scripts/validate-metadata.py`, `metadata/`
   - Reuse value: DOI and publication metadata alignment across distribution files.

5. **Audit framework template**
   - Source: `audits/*.md`, `scripts/audit-publication-readiness.py`, `scripts/audit-chktex.py`
   - Reuse value: repeatable publication-readiness assessments.

6. **Visual publication framework template**
   - Source: `paper/figures/manifest.md`, `paper/figures/captions.md`, Pages docs sync
   - Reuse value: canonical figure and publication asset management.

## Suggested Extraction Order

1. Release packaging + metadata validation templates
2. Pages deployment + publication orchestrator templates
3. Audit/reporting templates
4. Visual/figure lifecycle templates
