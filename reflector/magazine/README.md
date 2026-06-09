# Magazine

The `magazine/` artifact is a visual companion renderer for the reflector paper.
It assembles preserved full-page PNG outputs into reproducible digital and print PDFs.

## Directory structure

```text
magazine/
├── outline.md
├── spec.md
├── prompts/                 # canonical prompt provenance (page01...page14)
├── pages/                   # canonical full-page PNG assets (page01...page14)
├── tex/
│   ├── magazine.tex         # digital/screen PDF entrypoint (2:3 portrait, full-page)
│   ├── magazine-print.tex   # print PDF entrypoint (2:3 portrait, full-page)
│   └── .latexmkrc           # isolated magazine latexmk configuration
├── .cache/                  # local auxiliary/output build intermediates
└── dist/
    ├── reflector-magazine.pdf
    └── reflector-magazine-print.pdf
```

## Build workflow

Use Task targets:

```bash
task magazine:doctor
task magazine:build
task magazine:build:print
```

Equivalent script usage:

```bash
./scripts/build-magazine.sh doctor
./scripts/build-magazine.sh build
./scripts/build-magazine.sh build-print
```

### Output paths

- Digital PDF: `magazine/dist/reflector-magazine.pdf`
- Print PDF: `magazine/dist/reflector-magazine-print.pdf`

### Print layout strategy

The print variant uses the same edge-to-edge `8in x 12in` full-page image layout as
the digital variant so each source PNG is rendered as a full document page.

## Adding a new page

1. Add `magazine/pages/pageNN-name.png`.
2. Add `magazine/prompts/pageNN-*.prompt.md` with the same `pageNN-` prefix.
3. Update page lists in:
   - `magazine/tex/magazine.tex`
   - `magazine/tex/magazine-print.tex`
   - `scripts/build-magazine.sh` (`PAGE_FILES` array)
4. Re-run:

```bash
task magazine:doctor
task magazine:build
task magazine:build:print
```

## Cleaning

```bash
task magazine:clean
```
