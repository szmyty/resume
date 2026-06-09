<!--
SPDX-FileCopyrightText: 2026 Alan Szmyt
SPDX-License-Identifier: Apache-2.0
-->

# Pages Publication Synchronization Findings

## Findings summary

## 1) Build outputs verification

Expected build outputs:

- `paper/.cache/out/paper.pdf`
- `magazine/.cache/out/magazine.pdf`
- `magazine/.cache/out/magazine-print.pdf`

Local verification in this sandbox:

- All three files are currently **missing** because local TeX dependencies are incomplete (`lmodern.sty` missing).
- Hero source exists:
  - `paper/figures/hero.png` size `1357921`
  - sha256 `fc3a6b84e61b38390bd211ecd010675dfcb873f4e4fa0450a624fa0f9510e765`

## 2) Synchronization verification

`docs/` currently contains site content but not publication PDFs. This confirms fallback reuse from repository state is unreliable for PDF assets.

Workflow hardening now requires synchronized publication files and logs full `docs/` and `_site/` inventories.

## 3) Artifact packaging verification

Workflow now validates required publication files in both staging paths before artifact upload:

- `docs/reflector.pdf`
- `docs/reflector-magazine.pdf`
- `docs/reflector-magazine-print.pdf`
- `docs/publication.json`
- `docs/figures/hero.png`
- `_site/reflector.pdf`
- `_site/reflector-magazine.pdf`
- `_site/reflector-magazine-print.pdf`
- `_site/publication.json`
- `_site/figures/hero.png`

## Root cause

Fallback behavior allowed successful deployments without regenerated publication PDFs, producing Pages artifacts missing publication files.

## Implementation plan

- [x] Force paper and magazine builds for push-based Pages deploys.
- [x] Fail synchronization when required fallback files are absent.
- [x] Fail verification if required publication assets are absent in `docs/` or `_site/`.
- [x] Log file inventories for synchronization and artifact diagnostics.
