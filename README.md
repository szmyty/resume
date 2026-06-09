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
│   └── fullstack.yaml
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

### Build the resume PDF

```bash
python scripts/build.py
```

The generated PDF will be placed in `outputs/resume.pdf`.

### Build with latexmk directly

```bash
latexmk -pdf -halt-on-error -interaction=nonstopmode -r .latexmkrc resume.tex
```

## Profiles

Profile YAML files in `profiles/` define which sections and content are included for a given resume variant. Future profile-targeted builds will select sections and tailor content based on the active profile.

| Profile | Description |
| --- | --- |
| `ai-infra.yaml` | AI infrastructure and ML platform roles |
| `platform.yaml` | Platform engineering and SRE roles |
| `research.yaml` | Research and academic roles |
| `fullstack.yaml` | Full-stack engineering roles |

## Specification

See [`specs/resume.spec.md`](specs/resume.spec.md) for the full architecture specification.

## License

Apache-2.0
