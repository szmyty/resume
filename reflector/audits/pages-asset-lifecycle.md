<!--
SPDX-FileCopyrightText: 2026 Alan Szmyt
SPDX-License-Identifier: Apache-2.0
-->

# GitHub Pages Publication Asset Lifecycle Audit

## Root cause

The Pages workflow allowed publication PDFs to be skipped and treated missing `docs/*.pdf` as non-fatal fallback warnings. Because PDFs are not committed under `docs/`, deployments could publish HTML without publication assets, causing `/reflector.pdf` and magazine routes to 404.

## Lifecycle trace

| Asset | Producer | Build output | docs/ sync path | Pages artifact path | Published URL |
| --- | --- | --- | --- | --- | --- |
| reflector.pdf | `Build reflector PDF` (`xu-cheng/latex-action@v4`) | `paper/.cache/out/paper.pdf` | `docs/reflector.pdf` | `_site/reflector.pdf` | `/reflector.pdf` |
| reflector-magazine.pdf | `Build reflector magazine PDF (digital)` + `Copy magazine PDFs to dist` | `magazine/.cache/out/magazine.pdf` -> `magazine/dist/reflector-magazine.pdf` | `docs/reflector-magazine.pdf` | `_site/reflector-magazine.pdf` | `/reflector-magazine.pdf` |
| reflector-magazine-print.pdf | `Build reflector magazine PDF (print)` + `Copy magazine PDFs to dist` | `magazine/.cache/out/magazine-print.pdf` -> `magazine/dist/reflector-magazine-print.pdf` | `docs/reflector-magazine-print.pdf` | `_site/reflector-magazine-print.pdf` | `/reflector-magazine-print.pdf` |
| hero.png | Repository asset | `paper/figures/hero.png` | `docs/figures/hero.png` | `_site/figures/hero.png` | `/figures/hero.png` |

## Evidence

- Local repository currently has no committed publication PDFs in `docs/`.
- Prior workflow behavior logged warnings for missing fallback files (run `26858878731`):
  - `Warning: Fallback PDF not found at 'docs/reflector.pdf'`
  - `Warning: Fallback magazine PDF not found at 'docs/reflector-magazine.pdf'`
  - `Warning: Fallback magazine print PDF not found at 'docs/reflector-magazine-print.pdf'`

## Implemented fix

1. Always rebuild paper + magazine PDFs on push-triggered Pages deployments.
2. Make missing fallback PDFs fatal when a build is intentionally skipped.
3. Require publication PDFs, `publication.json`, and `hero.png` in both `docs/` and `_site/` before upload.
4. Add deterministic file inventories (`find docs -type f` and `find _site -type f`) in workflow logs.

## Recommended follow-up

- Keep Pages deployment as the publication gate for web-delivered artifacts.
- Treat any missing publication asset as deployment failure.
