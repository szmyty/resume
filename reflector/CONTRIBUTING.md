# Contributing

Thank you for your interest in contributing to this repository.

## Repository Structure

The paper uses a publisher-agnostic publication architecture that separates
semantic content, metadata, rendering style, and build infrastructure:

```
paper/
├── paper.tex           # Thin orchestration wrapper
├── references.bib      # BibTeX bibliography
├── README.md           # Paper overview
├── abstract.md         # Abstract draft (plain text)
├── outline.md          # Section outline
├── notes.md            # Research notes and brainstorming
├── roadmap.md          # Development roadmap
├── macros/
│   └── metadata.tex    # Paper metadata commands (\papertitle, \paperauthor, etc.)
├── styles/
│   └── reflector.sty   # Publication style (packages, colors, layout, typography)
├── sections/           # LaTeX section files (semantic content)
├── figures/            # Generated figures and exports
├── diagrams/           # Source diagram files (Excalidraw, etc.)
├── assets/             # Static assets (images, logos, etc.)
├── references/         # Reference documents and PDFs
└── examples/           # Example artifacts and code snippets
```

### Publication Architecture Layers

| Layer | Location | Purpose |
|-------|----------|---------|
| Content | `sections/` | Semantic paper content |
| Metadata | `macros/metadata.tex` | Author, title, version, repository |
| Style | `styles/reflector.sty` | Packages, colors, layout, typography |
| Build | `.latexmkrc`, `scripts/` | Compilation and packaging |

Future publisher targets (IEEE, ACM, etc.) can be supported by adding a new
`.sty` file under `styles/` and updating the `\usepackage` line in `paper.tex`.

## Adding a New Paper

1. Use the canonical `paper/` directory
2. Use `./scripts/scaffold-paper.sh paper` to scaffold/refresh paper structure
3. Update `paper/README.md` with paper metadata
4. Add sections under `paper/sections/`
5. Update the root `README.md` to list the new paper

## Building Papers

```bash
# Bootstrap local setup
task setup

# Build the paper
task build

# Build all papers
./scripts/build-paper.sh --all

# Watch and auto-rebuild during development
./scripts/watch-paper.sh paper
```

## Local Testing and CLI Verification

```bash
# Run lint and local validation hooks
task lint

# Run test workflow
task test

# Verify local CLI behavior
task doctor
task version
task run
task examples

# Run GitHub Actions workflows locally with act
act --list
act pull_request -W .github/workflows/synchronization.yml
```

See [`docs/act.md`](./docs/act.md) for canonical `.actrc` defaults, workflow boundaries, and troubleshooting.

## Style Guidelines

- Use spaces (not tabs) for indentation
- LaTeX files use 2-space indentation
- Markdown files follow standard CommonMark
- Section filenames use `snake_case.tex`
- Diagram source files use `kebab-case.excalidraw`
- Figure exports use `kebab-case.pdf` or `kebab-case.png`; reserve `hero.png` as the canonical publication preview asset

## Pre-Commit Hooks

Install and run hooks locally:

```bash
task setup
uv run pre-commit install
uv run pre-commit run --all-files
```

The hook set keeps checks lightweight and focused on repository hygiene,
YAML/JSON/workflow validation, release metadata consistency, and LaTeX formatting.

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add milestone synchronization section
fix: correct bibliography citation keys
docs: update reflector abstract
chore: update build workflow dependencies
research: document recursive drift case study findings
spec: align release metadata schema
sync: reconcile publication routes and release artifacts
audit: verify release manifest checksums
```

Commit messages are validated in CI using `commitlint`.

## Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Ensure the paper builds successfully: `./scripts/build-paper.sh paper`
5. Open a pull request with a clear description

## License

By contributing, you agree that your contributions will be licensed under the repository's [LICENSE](./LICENSE).
