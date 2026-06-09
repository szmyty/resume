# paper/figures

This directory contains all figure assets for the reflector paper, along with the figure management
infrastructure that keeps figures, captions, labels, and section placements synchronized.

## Files in this directory

| File | Purpose |
| --- | --- |
| `manifest.md` | Canonical figure manifest — tracks every figure's file, section, label, dimensions, state, and synchronization notes |
| `captions.md` | Centralized caption registry — canonical caption text for every figure placement |
| `prompts/*.prompt.md` | Canonical prompt-preservation records for recursive figure generation and synchronization checkpoints |
| `placeholders/` | Optional staging sources for placeholder design inputs |
| `final/` | Optional staging sources for candidate final renders before canonical replacement |
| `archive/` | Optional archive for superseded figure revisions |
| `figure1.png` … `figure17.png` | Figure assets (currently placeholder copies) |
| `hero.png` | Hero figure asset (currently a placeholder copy) |

---

## Figure naming conventions

Canonical body figures follow a deterministic numeric scheme:

```
figure1.png
figure2.png
...
figureN.png
```

The hero figure uses the fixed name `hero.png`.

Reserved figure numbers may exist in the directory without a corresponding section placement.
When that happens, track the slot with `Status: Reserved` in `manifest.md` and add reviewer-facing caption metadata in `captions.md` once the figure is assigned to a manuscript section.

**Do not rename figure files once they are referenced from the paper.**
The file names are stable identifiers. All `\includegraphics{}` calls, `manifest.md` entries,
and `captions.md` entries must stay in sync.

---

## Figure states

Each figure is in one of two states:

| State | Meaning |
| --- | --- |
| `placeholder` | A layout-stabilization copy with canonical dimensions. The paper compiles and the layout is stable, but the figure is not publication-ready. |
| `final` | A publication-ready rendered figure that has replaced the placeholder. |

When a figure moves from `placeholder` to `final`, update the `state` field in `manifest.md`.

---

## Figure lifecycle architecture

Canonical figure lifecycle:

```
Placeholder Figure
  ↓
Prompt Iteration
  ↓
Candidate Figure
  ↓
Synchronization Review
  ↓
Final Publication Figure
```

Synchronization review must checkpoint:

1. Prompt file update in `prompts/<figure>.prompt.md`
2. Manifest state/metadata updates in `manifest.md`
3. Caption + label synchronization in `captions.md` and `paper/sections/*.tex`
4. Publication validation (`python3 scripts/audit-publication-readiness.py`)

---

## Canonical dimensions

| Figure set | Dimensions |
| --- | --- |
| `figure1.png` – `figure17.png` | 1600 × 900 px |
| `hero.png` | 1920 × 1080 px |

Replacement figures must use these exact dimensions to preserve layout stability.

---

## Placeholder workflow

The placeholder workflow supports progressive figure replacement without disrupting LaTeX layout or figure numbering.

### Adding a new figure

1. Choose the next available number (e.g., `figureN.png`).
2. Create a 1600 × 900 px placeholder PNG and copy it to `paper/figures/figureN.png`.
3. Add a `\begin{figure}…\end{figure}` block to the target section file with:
   - `\includegraphics[width=\linewidth]{figureN.png}`
   - A `\caption{…}` with the canonical caption text
   - A `\label{fig:figureN}` (or a descriptive label like `fig:section-name`)
4. Add the figure to `manifest.md` with all metadata fields populated.
5. Add the caption entry to `captions.md`.
6. Run `scripts/audit-publication-readiness.py` to verify all figure integrity checks pass.

### Replacing a placeholder with a final figure

1. Render the final figure at the canonical dimensions (see above).
2. Record prompt iteration and rendering rationale in `prompts/figureN.prompt.md`.
3. Copy the rendered figure to `paper/figures/figureN.png`, overwriting the placeholder.
4. Update the `state` field from `placeholder` to `final` in `manifest.md`.
5. Optionally refine the caption in `captions.md` and apply the same update to the LaTeX section file.
6. Run `scripts/audit-publication-readiness.py` to verify the figure passes all integrity checks.

### Reserving a figure slot

To reserve a slot without placing the figure in a section yet:

1. Add a placeholder PNG with the canonical dimensions.
2. Add the figure to `manifest.md` with `state: placeholder` and `Status: Reserved`.
3. Set `section`, `label`, and `caption` to `null` in the manifest YAML.
4. Add a caption entry to `captions.md` once the slot is assigned to a manuscript section.
5. Do **not** reference the file from any LaTeX section until the slot is assigned.

---

## Caption update workflow

Captions are centralized in `captions.md`. The canonical caption text lives there;
the LaTeX `\caption{}` calls must always match.

1. Update the caption text in `captions.md` under the relevant figure heading.
2. Apply the identical text to the `\caption{}` call in the LaTeX section file.
3. Confirm the `\label{fig:…}` in the LaTeX file matches the `label` field in `manifest.md`.
4. Run `scripts/audit-publication-readiness.py` to confirm all figure integrity checks pass.

---

## Prompt preservation workflow

Prompt records are the canonical recursive figure-generation history.

1. Update the figure prompt file in `prompts/<figure>.prompt.md`.
2. Append prompt changes under **Prompt history**.
3. Record generation inputs under **Generation context**.
4. Record synchronization outcomes under **Synchronization notes** and **Recursive checkpoints**.
5. Keep prompt context aligned with `manifest.md` state and caption/label updates.

---

## Publication synchronization

All figure assets in this directory must meet the following criteria for publication:

- **Format:** PNG (preferred), PDF, JPEG, or EPS. See `scripts/audit-publication-readiness.py` for the full list of accepted formats.
- **Dimensions:** As specified under *Canonical dimensions* above.
- **arXiv safety:** PNG and PDF are arXiv-safe. JPEG is acceptable. EPS may require conversion.
- **Apple Pages safety:** PNG and JPEG are safe for Pages export workflows.
- **Deterministic naming:** File names must not change after a figure is referenced in the paper.

The `scripts/audit-publication-readiness.py` script enforces:

- All `\includegraphics{}` references resolve to existing files.
- All figure formats are render-safe.
- Referenced prompt files exist under `paper/figures/prompts/`.
- Referenced PNG figures preserve canonical dimensions.
- All `\begin{figure}` blocks include a `\caption{}`.
- All `\begin{figure}` blocks include a `\label{fig:…}`.
- All referenced figures are listed in `manifest.md`.

Run the audit after any change to figures, captions, or section files:

```sh
python3 scripts/audit-publication-readiness.py
```

---

## Recursive drift reduction

Figure drift occurs when captions, labels, and placements diverge across recursive paper iterations.
This directory structure prevents drift by making `manifest.md` and `captions.md` the single sources
of truth for figure metadata:

- The manifest governs file names, section assignments, labels, and states.
- The caption registry governs caption text for every figure placement.
- The audit script enforces manifest coverage and LaTeX block integrity on every build.

Any change to a figure, caption, or label must be reflected in all three locations
(manifest, caption registry, LaTeX section) before the change is considered complete.
