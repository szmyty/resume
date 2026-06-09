<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Infrastructure

The canonical publication release pipeline is:

```
.github/workflows/publication.yml
```

All release packaging now stages artifacts into one authoritative directory:

```text
release/
└── reflector-vX.Y.Z/
    ├── reflector.pdf
    ├── reflector-magazine.pdf
    ├── reflector-magazine-print.pdf
    ├── reflector-arxiv-vX.Y.Z.zip
    ├── reflector-arxiv-vX.Y.Z.tar.gz
    ├── source.zip
    ├── publication.json
    ├── publication-readiness.md
    ├── chktex-audit.md
    ├── zenodo-readiness.md
    ├── release-notes.md
    ├── checksums.txt
    └── release-manifest.json
```

## Path Rules

- Resolve artifact paths to absolute paths internally.
- Convert paths back to repository-relative form only for human-readable output.
- Treat `release/reflector-vX.Y.Z/` as the only supported release staging root.
- Do not copy the repository-root `release-manifest.json` into staged release assets.

## Packaging Contract

| Artifact | Producer | Output path | Validation |
|---|---|---|---|
| `reflector.pdf` | `build-paper` job | `release/reflector-vX.Y.Z/reflector.pdf` | required |
| `reflector-magazine.pdf` | `build-magazine` job | `release/reflector-vX.Y.Z/reflector-magazine.pdf` | required |
| `reflector-magazine-print.pdf` | `build-magazine` job | `release/reflector-vX.Y.Z/reflector-magazine-print.pdf` | required |
| `reflector-arxiv-vX.Y.Z.zip` | `package` job | `release/reflector-vX.Y.Z/reflector-arxiv-vX.Y.Z.zip` | required |
| `reflector-arxiv-vX.Y.Z.tar.gz` | `package` job | `release/reflector-vX.Y.Z/reflector-arxiv-vX.Y.Z.tar.gz` | required |
| `source.zip` | `package` job | `release/reflector-vX.Y.Z/source.zip` | required |
| `publication.json` | `package` job | `release/reflector-vX.Y.Z/publication.json` | required |
| `publication-readiness.md` | `validate` job artifact | `release/reflector-vX.Y.Z/publication-readiness.md` | required |
| `chktex-audit.md` | `audit-chktex` job artifact | `release/reflector-vX.Y.Z/chktex-audit.md` | required |
| `zenodo-readiness.md` | `package` job | `release/reflector-vX.Y.Z/zenodo-readiness.md` | required |
| `release-notes.md` | `package` job | `release/reflector-vX.Y.Z/release-notes.md` | required |
| `checksums.txt` | `scripts/stage-publication-release.py` | `release/reflector-vX.Y.Z/checksums.txt` | generated after all required artifacts exist |
| `release-manifest.json` | `scripts/stage-publication-release.py` | `release/reflector-vX.Y.Z/release-manifest.json` | generated after checksums complete |

## Checksums and Manifest

`scripts/stage-publication-release.py` is the canonical release inventory generator.

It:

1. validates the required staged artifacts,
2. writes deterministic SHA-256 checksums in filename order,
3. writes `release-manifest.json` with artifact inventory, checksum inventory, and release URLs,
4. embeds DOI metadata (canonical version DOI + concept DOI) for publication/citation tooling,
5. fails with explicit expected-path diagnostics when a staged artifact is missing.

## DOI Synchronization Contract

The canonical DOI fields are sourced from:

- `metadata/publication.yaml` (`identifiers.doi`, `identifiers.zenodo_concept_doi`)
- `metadata/repository.yaml` (`future_integrations.doi`, `future_integrations.zenodo`)

These values must remain synchronized with:

- `CITATION.cff`
- `.zenodo.json`
- `codemeta.json`
- `release-manifest.json` (repository metadata)
- staged `release-manifest.json` generated in `release/reflector-vX.Y.Z/`

Validation is enforced by `scripts/validate-metadata.py`.

## Dry Run and Smoke Testing

- Remote dry run: dispatch `.github/workflows/publication.yml` with `dry_run: true`.
- Local smoke test: run `pytest -q tests/test_stage_publication_release.py`.

The smoke test exercises the same staging/manifest/checksum path logic used by the packaging workflow without creating a GitHub release.
