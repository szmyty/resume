<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# DOI Metadata Audit

Generated: 2026-06-03

## Canonical DOI Values

- Version DOI: `10.5281/zenodo.20477044`
- Version DOI URL: `https://doi.org/10.5281/zenodo.20477044`
- Concept DOI: `10.5281/zenodo.20477045`
- Concept DOI URL: `https://doi.org/10.5281/zenodo.20477045`

## DOI Surface Audit

| Surface | Field(s) | Status |
| --- | --- | --- |
| `metadata/publication.yaml` | `identifiers.doi`, `doi_url`, `zenodo_concept_doi`, `zenodo_concept_doi_url` | In sync |
| `CITATION.cff` | `doi`, `url`, `preferred-citation.doi`, `preferred-citation.url` | In sync |
| `.zenodo.json` | `doi`, `conceptdoi` | In sync |
| `codemeta.json` | `identifier` | In sync |
| `publication.json` | `future.doi_generation.*` | In sync |
| `release-manifest.json` | `future_integrations.doi.*` | In sync |

## Validation Rules (Implemented)

`scripts/validate-metadata.py` enforces DOI synchronization and validates:

1. Canonical DOI format validity.
2. DOI URL canonical mapping (`https://doi.org/<doi>`).
3. Cross-file DOI equality across all publication metadata surfaces.
4. Presence of required DOI fields.

Audit execution:

- `python3 scripts/validate-metadata.py` → pass

## Drift Risk Assessment

- Current risk: **Low** (automated validation catches DOI drift pre-release).
- Residual risk: DOI changes after Zenodo minting still require coordinated metadata update
  and release of synchronized metadata.

## Recommendations

1. Keep DOI synchronization validation as a required release gate.
2. Add post-Zenodo-mint update checklist that regenerates and revalidates all DOI surfaces.
3. Add destination-level DOI validation (GitHub Release notes + Pages metadata references)
   as a final publication check.

