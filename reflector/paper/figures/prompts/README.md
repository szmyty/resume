# Figure Prompt Preservation Registry

This directory preserves figure-generation prompts and synchronization context for deterministic recursive iteration.

## Canonical prompt files

Use one prompt file per canonical figure asset:

- `hero.prompt.md`
- `figureN.prompt.md`

Prompt files should persist across revisions. Update the existing file rather than creating ad-hoc alternatives.

## Required sections

Every prompt file must contain the following headings:

1. `## Prompt history`
2. `## Generation context`
3. `## Synchronization notes`
4. `## Rendering rationale`
5. `## Recursive checkpoints`

## Directory roles

- `paper/figures/` — canonical publication-safe figure files referenced by LaTeX
- `paper/figures/placeholders/` — optional source placeholders and staging inputs
- `paper/figures/final/` — optional source exports before canonical replacement
- `paper/figures/archive/` — optional archived revisions for traceability

Do not change LaTeX `\\includegraphics{}` references to non-canonical paths. Final publication assets must remain `paper/figures/figureN.png` (or `hero.png`).
