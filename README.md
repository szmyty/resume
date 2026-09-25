# Career Document Publishing System

A specification-driven LaTeX system for producing Alan Szmyt's résumé and CV
from a validated, self-contained rendering ledger. It renders a sanitized
public baseline and role-specific application documents without forking facts
or committing private contact data.

## Public resume

The canonical sanitized résumé is published at:

- **Resume site:** <https://szmyty.github.io/resume/>
- **Direct PDF:** <https://szmyty.github.io/resume/resume.pdf>

The Pages deployment is built from the same validated `general` public artifact
used by CI. Application-only email, phone, location overlays, and generated
application PDFs are never included in the Pages artifact.

GitHub Pages requires one repository-level setup before the first deployment:
**Settings → Pages → Build and deployment → Source → GitHub Actions**. After that
one-time selection, successful `main` builds publish the site automatically.

## Publication model

| Layer | Location | Responsibility |
| --- | --- | --- |
| Source facts and evidence | Private career repository | Source catalog and future owner-reviewed career facts, outside this public build |
| Rendering projection | `content/career.json` | Existing validated ledger with reviewed additions, public-safe claims, provenance summaries, privacy rules, and destinations |
| Role profiles | `profiles/*.yaml` | Headline, summary, selected claim IDs, evidenced skill groups, and section order |
| Audience | `--audience public\|application` | Selects sanitized or owner-approved wording and contact projection |
| Document type | `documents/*.yaml` | Résumé/CV section pool, template, and page-size defaults |
| Target overlay | `targets/*.yaml` | Optional application-specific ordering, page size, and output naming |
| Presentation | `templates/`, `*.sty` | ATS-safe LaTeX metadata, typography, and layout |

Configuration resolves in this order:

```text
document manifest → role profile → optional target → CLI overrides
```

Career text is always selected by ID from `content/career.json`. Profiles and
targets cannot introduce new career facts. The private career repository is the
authority for source facts and evidence as they are reviewed; this local ledger
is the canonical input to the renderer and must remain independently buildable
without private access. Existing public content stays in place as the current
publication baseline. A source catalog is not an approved claim, and this
documentation change performs no new source audit or content migration.

## Current résumé lanes

| Profile | Purpose | Application filename |
| --- | --- | --- |
| `general` | Canonical Platform/DevEx baseline | `Alan-Szmyt-Resume-Platform-DevEx.pdf` |
| `platform` | Platform engineering and developer experience | `Alan-Szmyt-Resume-Platform-DevEx.pdf` |
| `research` | Research software and AI-assisted systems | `Alan-Szmyt-Resume-Research-AI-Systems.pdf` |
| `mobile-geospatial` | Resilient mobile and geospatial systems | `Alan-Szmyt-Resume-Mobile-Geospatial.pdf` |

The permanent public baseline is intentionally named `Alan-Szmyt-Resume.pdf`.
Other public role renders include `-Public` in their filenames.

`Greater Boston, MA` is the intentionally approved permanent-public location.
It is broad location context, not an application-only contact value; changing
or removing it requires an owner-approved canonical-ledger update.

## Build

Prerequisites:

- Python 3.11+
- PyYAML and pypdf
- TeX Live, `latexmk`, and Poppler (`pdftotext`, `pdffonts`, `pdfinfo`)

Install Python dependencies with Poetry:

```bash
poetry install
```

List documents, profiles, and targets:

```bash
python scripts/build.py --list
```

Build the sanitized public baseline:

```bash
python scripts/build.py \
  --document resume \
  --profile general \
  --audience public
```

The artifact is written to:

```text
dist/resume/general/public/Alan-Szmyt-Resume.pdf
```

### Application builds

Application builds require a local, owner-approved contact overlay. Start from
`content/application-contact.example.json`, save the completed file under
`.local/`, and never commit it.

```json
{
  "email": "approved-address@example.com",
  "phone": "+1 555-010-0200",
  "location": "Approved application location"
}
```

Build a role variant:

```bash
python scripts/build.py \
  --document resume \
  --profile research \
  --audience application \
  --contact-file .local/application-contact.json
```

Only `email`, `phone`, and `location` are accepted. At least one of `email` or
`phone` is required, and unknown fields fail closed.

### Other examples

```bash
# Platform/DevEx application résumé
python scripts/build.py \
  --document resume \
  --profile platform \
  --audience application \
  --contact-file .local/application-contact.json

# Mobile/geospatial public derivative
python scripts/build.py \
  --document resume \
  --profile mobile-geospatial \
  --audience public

# Public research CV
python scripts/build.py \
  --document cv \
  --profile research \
  --audience public

# A4 or a thin target overlay
python scripts/build.py \
  --document resume \
  --profile general \
  --audience public \
  --page-size a4
python scripts/build.py \
  --document resume \
  --profile general \
  --audience public \
  --target example
```

Generated PDFs are written below:

```text
dist/<document>/<profile>/<audience>/[<target>/]<intentional-filename>.pdf
```

A compatibility copy is also written to `outputs/`. Generated artifacts and
local contact overlays are ignored by git.

## Quality gates

Run deterministic source checks:

```bash
python scripts/quality_gates.py validate-facts
python scripts/quality_gates.py validate-documents
python scripts/quality_gates.py validate-profiles
python scripts/quality_gates.py check-placeholders
python scripts/quality_gates.py validate-destinations --audience public
python -m pytest tests/ -v
```

Validate a built public résumé:

```bash
python scripts/quality_gates.py validate-ats \
  --pdf dist/resume/general/public/Alan-Szmyt-Resume.pdf \
  --audience public
python scripts/quality_gates.py validate-pdf \
  --pdf dist/resume/general/public/Alan-Szmyt-Resume.pdf \
  --audience public
```

The artifact gates enforce:

- stable Poppler and pypdf extraction;
- required headings, identity phrases, and token boundaries;
- exactly two balanced résumé pages with at least 58% vertical occupancy;
- intentional filename, metadata, document language, links, and embedded fonts;
- no unsafe PDF actions;
- public/application contact allowlists.

## Continuous integration

`.github/workflows/build-resume.yml` validates the fact ledger, profiles,
destinations, privacy policy, and tests. It then:

1. builds and validates four public résumé renders;
2. builds and validates four application role variants with synthetic CI-only
   contact data;
3. builds and fully validates the public research CV;
4. renders résumé pages to PNG for visual review;
5. uploads only public PDFs and visual renders; and
6. on successful `main` pushes, packages the validated canonical public résumé
   with `site/` and deploys it to GitHub Pages.

Application artifacts are never uploaded by CI or GitHub Pages.

## Changing content safely

1. Review the source fact and evidence in the private career repository. Obtain
   owner approval for new or revised wording and the intended audience.
2. Add only the approved public-safe projection to `content/career.json`, with
   a stable claim ID, public-safe provenance, and separate public/application
   wording when sensitivity differs. Do not copy private documents, private
   URLs, personal notes, or contact information into this repository.
3. Reference the claim ID from an approved role profile; add skills only when a
   selected claim supplies evidence.
4. Run all deterministic gates and affected public/application builds.
5. Inspect the generated PDF pages, not only the LaTeX source.

No rendering or CI step fetches from the private career repository. There is
no automatic export into `content/career.json`; its future additions require a
separate, reviewed content change. This handoff does not migrate claims or
replace a PDF.

Do not infer employment status for overlapping work, upgrade seniority, remove
qualifiers from metrics, or convert an independent artifact into a peer-reviewed
publication claim.

See [`specs/resume.spec.md`](specs/resume.spec.md) for the architecture contract
and [`specs/governance.md`](specs/governance.md) for publication policy.
