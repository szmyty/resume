# Toolchain Requirements

This document describes the local development toolchain required to build the reflector manuscript deterministically.

## Required Executables

| Tool | Purpose | Minimum Version |
| --- | --- | --- |
| `latexmk` | Orchestrates multi-pass LaTeX compilation | 4.75+ |
| `pdflatex` | Compiles `.tex` source to PDF | TeXLive 2025 |
| `biber` | Processes bibliography via biblatex/biber backend | 2.19+ |
| `uv` | Manages local Python environments and dependencies | 0.11+ |

These executables must be available in `PATH` to build and develop locally.

## Installing TeXLive 2025

### Ubuntu / Debian (recommended for CI parity)

```bash
sudo apt-get update
sudo apt-get install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    biber \
    latexmk
```

This installs all packages declared in `paper/styles/reflector.sty` and aligns with the GitHub Actions Ubuntu environment.

### macOS (Homebrew)

```bash
brew install --cask mactex
```

Or for a minimal install:

```bash
brew install basictex
sudo tlmgr update --self
sudo tlmgr install \
    latexmk \
    biber \
    biblatex \
    logreq \
    collection-latexrecommended \
    collection-latexextra \
    collection-fontsrecommended
```

### Windows

Download and install [TeXLive for Windows](https://tug.org/texlive/windows.html) or [MiKTeX](https://miktex.org/download).

After installation, ensure `latexmk`, `pdflatex`, and `biber` are on `PATH`.

### tlmgr (any platform with existing TeXLive)

```bash
tlmgr install latexmk biber biblatex logreq
```

## Validating the Toolchain

After installation, verify each executable is available and reports a version:

```bash
latexmk --version
pdflatex --version
biber --version
```

Expected outputs (versions may vary):

```
Latexmk, John Collins, 28 August 2023. Version 4.80
...
pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023)
...
biber version: 2.20
```

You can also run the automated compatibility validation script:

```bash
python3 scripts/validate-texlive-compatibility.py
```

All `Toolchain availability` checks should pass.

## Building Locally

Once the toolchain is installed, build the paper with:

```bash
./scripts/build-paper.sh paper
```

The output PDF is written to `paper/.cache/out/paper.pdf`.

To open the PDF automatically after building:

```bash
./scripts/build-paper.sh paper --open
```

To copy the PDF into `docs/` for publication:

```bash
./scripts/build-paper.sh paper --publish
```

### Build Configuration

Build behavior is controlled by the root `.latexmkrc` file:

- Output directory: `paper/.cache/out/`
- Auxiliary directory: `paper/.cache/aux/`
- Compiler: `pdflatex` (`$pdf_mode = 1`)
- Bibliography: `biber` with fixed input/output directories
- Max iterations: `$max_repeat = 10`
- TEXINPUTS: `./config//`, `./styles//`, `./macros//`, `./sections//`, `./figures//`, `./diagrams//`

## CI/CD Build

CI builds use the [`xu-cheng/latex-action@v4`](https://github.com/xu-cheng/latex-action) GitHub Actions action, which provides a full TeXLive environment in Docker.

The CI toolchain is equivalent to the recommended local install:

- pdflatex (TeXLive full)
- biber (via `extra_system_packages: "biber"`)
- latexmk (included in TeXLive)

CI workflow: `.github/workflows/build-paper.yml`

## Determinism and Reproducibility

The build pipeline is designed to be deterministic:

- `.latexmkrc` fixes output/aux directories and TEXINPUTS paths
- `latexmk -gg` forces a full clean rebuild each run
- `biber` is configured with fixed `--input-directory` and `--output-directory`
- Build artifacts are isolated in `paper/.cache/` (git-ignored)

For maximum reproducibility, use the same TeXLive version (2025) as declared in `00README.json`.

The declared TeXLive version can be verified with:

```bash
python3 scripts/validate-texlive-compatibility.py
```

## Troubleshooting

### `latexmk: command not found`

Install `latexmk` via your package manager (see [Installing TeXLive 2025](#installing-texlive-2025) above).

### `biber: command not found`

On Ubuntu/Debian, `biber` is a separate package:

```bash
sudo apt-get install -y biber
```

On macOS with MacTeX/BasicTeX:

```bash
sudo tlmgr install biber
```

### Build fails with missing package errors

If `pdflatex` reports `! LaTeX Error: File '...sty' not found`, install the missing TeXLive collection:

```bash
sudo tlmgr install <package-name>
```

For a full install (recommended for parity with CI):

```bash
# Ubuntu/Debian
sudo apt-get install -y texlive-full

# macOS
brew install --cask mactex
```

### Diagnostics

Build failure diagnostics are printed automatically by `scripts/build-paper.sh`. For more detail, run:

```bash
LATEX_LOG_TAIL_LINES=200 ./scripts/build-paper.sh paper
```

Or directly invoke the diagnostics script:

```bash
./scripts/print-latex-diagnostics.sh paper
```

## References

- [TeXLive 2025](https://tug.org/texlive/)
- [latexmk documentation](https://ctan.org/pkg/latexmk)
- [biblatex/biber documentation](https://ctan.org/pkg/biblatex)
- [arXiv TeX compatibility](https://info.arxiv.org/help/submit_tex.html)
- Repository compatibility report: `publication/compatibility-report.md`
- Repository reproducibility audit: `audits/build-reproducibility.md`
