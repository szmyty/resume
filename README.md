# Resume

A specification-driven, LaTeX-based resume system capable of generating profile-targeted resume variants from shared source content.

## Structure

```
resume/
├── resume.tex          # Main LaTeX entry point
├── resume.sty          # Resume style package
├── sections/           # Modular resume section files
│   ├── header.tex
│   ├── summary.tex
│   ├── experience.tex
│   ├── publications.tex
│   ├── education.tex
│   └── skills.tex
├── profiles/           # Profile variant definitions (YAML)
│   ├── ai-infra.yaml
│   ├── platform.yaml
│   ├── research.yaml
│   └── general.yaml
├── assets/             # Images, icons, and other static assets
├── outputs/            # Generated PDF artifacts
├── scripts/
│   └── build.py        # Build script
├── specs/
│   └── resume.spec.md  # Architecture specification
└── .github/
    └── workflows/
        └── build-resume.yml
```

## Building

### Prerequisites

- TeX Live 2023+ (with `latexmk`)
- Python 3.10+

### Build all profile PDFs

```bash
python scripts/build.py
```

The generated PDFs will be placed in:

- `outputs/resume-ai-infra.pdf`
- `outputs/resume-platform.pdf`
- `outputs/resume-research.pdf`
- `outputs/resume-general.pdf`

### Build a specific profile PDF

```bash
python scripts/build.py --profile platform
```

If the requested profile does not exist, the build will fail with the list of available profiles.

### Build with latexmk directly

```bash
latexmk -pdf -halt-on-error -interaction=nonstopmode -r .latexmkrc resume.tex
```

## Quality Gates

Run repository validation checks locally:

```bash
python scripts/quality_gates.py validate-profiles
python scripts/quality_gates.py check-placeholders
```

Validate ATS extraction after generating a PDF:

```bash
python scripts/quality_gates.py validate-ats --pdf outputs/resume.pdf
```

## Profiles

Profile YAML files in `profiles/` define the profile name, summary variant, section ordering, included sections, and keyword emphasis for a given resume variant.

| Profile | Description |
| --- | --- |
| `ai-infra.yaml` | AI infrastructure and ML platform roles |
| `platform.yaml` | Platform engineering and SRE roles |
| `research.yaml` | Research and academic roles |
| `general.yaml` | General software engineering roles |

## Specification

See [`specs/resume.spec.md`](specs/resume.spec.md) for the full architecture specification.

## Governance

See [`specs/governance.md`](specs/governance.md) for repository publication, audit, profile, and artifact governance workflows.

## License

Apache-2.0
