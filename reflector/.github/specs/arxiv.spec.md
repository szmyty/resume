# arXiv Publishing Infrastructure Specification

## Metadata

* Spec Identifier: `arxiv.spec.md`
* Repository: `egohygiene/papers`
* Intended Location: `.github/specs/arxiv.spec.md`
* Specification Style: SpecKit-inspired
* Status: Draft
* Owner: Alan Szmyt
* Scope: Deterministic, publisher-agnostic scholarly publishing infrastructure with first-class arXiv support

---

# Purpose

This specification defines the architectural, operational, and scholarly requirements for the arXiv publishing infrastructure within the `egohygiene/papers` repository.

The goal is to establish a deterministic, reproducible, publisher-agnostic scholarly release pipeline capable of:

* producing arXiv-compatible submission artifacts
* preserving semantic and machine-readable document structure
* supporting accessibility-aware publishing workflows
* generating deterministic release bundles
* validating publisher compliance automatically
* supporting future publisher targets beyond arXiv
* separating canonical source content from derived publication artifacts

This specification treats scholarly publishing as a reproducible software release process.

---

# Problem Statement

Modern scholarly publishing pipelines are fragmented, inconsistent, and frequently rely upon:

* manual release preparation
* ad-hoc formatting workflows
* non-deterministic compilation environments
* hidden local tooling assumptions
* publisher-specific manual cleanup
* inconsistent metadata handling
* inaccessible document structures
* poor reproducibility guarantees

arXiv submission workflows historically required substantial manual intervention, particularly regarding:

* TeX source preparation
* bibliography handling
* file flattening
* figure compatibility
* ancillary file organization
* compiler configuration
* package compatibility
* accessibility compliance
* moderation-safe formatting

The repository SHALL implement a structured publication infrastructure capable of transforming canonical scholarly sources into deterministic publisher-specific release artifacts.

---

# Architectural Principles

## Canonical Source Principle

The repository SHALL maintain a single canonical scholarly source representation.

Canonical source content SHALL:

* prioritize semantic structure over visual formatting
* remain publisher-independent
* preserve accessibility metadata
* preserve machine-readable structure
* support future transformations
* avoid publisher-specific hacks whenever possible

Publisher release artifacts SHALL be derived outputs.

The canonical source SHALL NOT be modified directly for individual publisher constraints.

---

## Deterministic Build Principle

All publication artifacts SHALL be reproducible.

Deterministic publication builds SHALL include:

* pinned TeXLive versions
* deterministic bibliography generation
* explicit compiler selection
* reproducible release manifests
* normalized file structures
* stable output naming
* isolated staging workspaces
* explicit release metadata

Generated publication artifacts SHOULD be byte-for-byte reproducible whenever possible.

---

## Publisher Adapter Principle

Publisher-specific requirements SHALL be implemented as transformation layers.

Publisher adapters MAY include:

* formatting transforms
* spacing transforms
* bibliography transforms
* metadata transforms
* file flattening
* artifact cleanup
* compliance validation
* package substitution
* release manifest generation

Publisher adapters SHALL NOT mutate canonical scholarly source files.

---

## Accessibility Principle

The publication system SHALL prioritize accessibility-aware authoring.

Accessibility requirements include:

* semantic sectioning
* machine-readable PDFs
* alt text support for figures
* structured metadata
* supported LaTeXML-compatible packages where practical
* Unicode-safe output
* embedded outline fonts
* avoidance of rasterized text

Visual formatting hacks SHALL be avoided when semantic alternatives exist.

---

## Scholarly Integrity Principle

All generated publication artifacts SHALL conform to accepted scholarly communication standards.

Submissions SHALL:

* maintain neutral professional tone
* include complete references
* preserve author attribution
* avoid misleading metadata
* disclose significant generative AI tooling where appropriate
* avoid ideological or non-scholarly framing
* remain self-contained and refereeable

The infrastructure SHALL optimize for moderation-safe scholarly presentation.

---

# Repository Structure

## Canonical Layout

The repository SHOULD evolve toward a structure similar to:

```text
papers/
├── paper/
│   ├── paper.tex
│   ├── references.bib
│   ├── sections/
│   ├── figures/
│   └── metadata/
│
├── publishers/
│   ├── arxiv/
│   ├── zenodo/
│   ├── openreview/
│   └── future_targets/
│
├── resources/
│   └── publishers/
│       └── arxiv/
│           ├── mirror/
│           ├── manifests/
│           ├── schemas/
│           └── extracted/
│
├── scripts/
│   ├── build/
│   ├── release/
│   ├── validate/
│   └── publishers/
│
└── dist/
    └── arxiv/
```

---

# Canonical Source Requirements

## Semantic LaTeX

Canonical LaTeX SHALL:

* use semantic section commands
* use semantic emphasis commands
* avoid visual-only formatting macros where semantic equivalents exist
* avoid unnecessary manual positioning
* avoid unsupported or obsolete figure inclusion packages
* avoid hidden build assumptions

Preferred:

```latex
\section{Introduction}
\emph{important concept}
```

Discouraged:

```latex
{\bfseries Introduction}
{\it important concept}
```

---

## Figure Requirements

Figures SHALL:

* use supported formats
* include alt text when feasible
* avoid runtime conversion dependencies
* avoid JavaScript embedding
* preserve scientific accuracy after conversion

Preferred formats for PDFLaTeX:

* PDF
* PNG
* JPG

The repository SHALL NOT rely upon automatic figure conversion during publisher compilation.

---

## Bibliography Requirements

The repository SHALL support:

* biblatex
* biber
* deterministic .bbl generation
* publisher-compatible bibliography freezing

Release pipelines SHOULD precompile bibliography artifacts.

The release pipeline MAY optionally strip `.bib` files from frozen publisher release artifacts.

Generated `.bbl` files SHALL remain compatible with the target TeXLive version.

---

# arXiv Requirements

## Supported Compiler

The default arXiv compiler SHALL be:

```json
{
  "process": {
    "compiler": "pdflatex"
  }
}
```

The infrastructure SHOULD avoid:

* shell escape dependencies
* runtime external tooling
* hidden cache dependencies
* unsupported TeX engines
* unsupported package assumptions

---

## TeXLive Compatibility

The release system SHALL:

* support arXiv-supported TeXLive versions
* validate bibliography compatibility
* validate package compatibility
* validate font embedding requirements

The release pipeline SHOULD support configurable TeXLive targeting.

---

## Hidden File Constraints

arXiv removes hidden files and directories during announcement.

The release pipeline SHALL:

* strip hidden directories
* strip hidden build caches
* avoid runtime hidden-path dependencies
* avoid packages depending on hidden runtime state

The canonical repository MAY continue using hidden local build directories.

Publisher release bundles SHALL NOT depend on them.

---

## Submission Constraints

arXiv release bundles SHALL:

* contain no unnecessary files
* contain no auxiliary artifacts except required preserved artifacts
* contain no referee markup
* contain no line numbering
* contain no obstructive watermarks
* contain no margin notes
* contain no embedded JavaScript
* contain no advertisements
* contain no unsupported filenames

Submission bundles SHALL preserve:

* authorship
* references
* machine readability
* minimum margin requirements
* acceptable font requirements

---

## File Naming Constraints

Generated release filenames SHALL only use:

```text
a-z A-Z 0-9 _ + - . , =
```

Release tooling SHALL sanitize incompatible filenames automatically.

---

# Release Pipeline

## Release Staging

The release pipeline SHALL create an isolated staging workspace.

The staging workspace SHALL:

* flatten publisher artifacts if required
* normalize filenames
* remove unused assets
* remove auxiliary files
* preserve required generated artifacts
* validate compilation
* generate deterministic bundles

Canonical source directories SHALL remain untouched.

---

## arXiv Release Artifact

The arXiv release pipeline SHOULD produce:

```text
dist/
└── arxiv/
    ├── source/
    ├── paper.pdf
    ├── submission.tar.gz
    ├── manifest.json
    ├── checksums.txt
    └── logs/
```

---

## Release Manifest

Each release SHOULD generate structured metadata including:

```json
{
  "publisher": "arxiv",
  "compiler": "pdflatex",
  "texlive_version": "2025",
  "generated_at": "ISO-8601",
  "license": "CC-BY-4.0",
  "artifact_hashes": {},
  "source_revision": "git-sha"
}
```

---

# Accessibility Requirements

The publication infrastructure SHOULD support:

* figure alt text
* semantic headings
* machine-readable PDFs
* embedded fonts
* proper Unicode output
* accessible metadata
* future HTML conversion compatibility

The repository SHOULD prioritize packages compatible with LaTeXML when feasible.

---

# Moderation-Safe Publication Guidelines

arXiv-targeted papers SHALL:

* maintain professional scholarly tone
* avoid manifesto-style framing
* avoid political or ideological digressions
* avoid autobiographical emphasis unrelated to research
* remain technically grounded
* preserve clear category relevance
* remain self-contained

Papers SHOULD:

* emphasize systems architecture
* emphasize methodology
* emphasize reproducibility
* emphasize engineering implementation
* emphasize scholarly archival value

---

# Ancillary Files

The release infrastructure SHALL support ancillary artifacts.

Ancillary files MAY include:

* datasets
* source code
* images
* supplementary diagrams
* spreadsheets
* reproducibility tooling

Ancillary files SHALL:

* live under `/anc/` in release bundles
* avoid TeX source placement
* avoid runtime submission dependencies
* avoid JavaScript embedding

Ancillary artifacts SHALL be treated as supplementary archival artifacts.

---

# Publisher-Agnostic Design

The infrastructure SHALL support future publisher targets.

Potential targets include:

* arXiv
* Zenodo
* OpenReview
* HAL
* OSF Preprints
* GitHub Pages
* EPUB
* journal-specific release pipelines

Publisher adapters SHOULD share:

* canonical metadata schemas
* validation interfaces
* release manifest formats
* deterministic build abstractions

---

# Validation Requirements

The infrastructure SHOULD eventually support automated validation for:

* arXiv compatibility
* bibliography compatibility
* TeXLive compatibility
* filename safety
* hidden file detection
* machine readability
* accessibility metadata
* figure compatibility
* package compatibility
* moderation-sensitive formatting
* ancillary file structure

---

# Future Enhancements

Potential future capabilities include:

* automatic 00README generation
* publisher capability matrices
* semantic figure metadata schemas
* release signing
* reproducible CI/CD publication workflows
* HTML-native scholarly releases
* accessibility linting
* moderation preflight analysis
* automated publisher transform pipelines
* scholarly metadata normalization

---

# Non-Goals

The infrastructure SHALL NOT:

* automate submission clicks or browser interactions
* attempt to bypass moderation systems
* attempt to manipulate endorsement systems
* generate deceptive affiliations or metadata
* rely upon unsupported TeX behavior
* prioritize visual formatting over semantic structure

---

# Success Criteria

The system SHALL be considered successful when:

* canonical scholarly sources remain publisher-independent
* arXiv release artifacts compile deterministically
* release bundles require minimal manual intervention
* generated PDFs remain machine-readable
* release workflows remain reproducible
* publisher constraints are encoded structurally
* accessibility metadata survives transformations
* moderation-safe scholarly presentation is preserved

---

# References

This specification was informed by:

* arXiv Submission System 1.5 documentation
* arXiv moderation policies
* arXiv format requirements
* arXiv ancillary file documentation
* arXiv 00README specification
* arXiv accessibility and HTML conversion guidance
* arXiv TeX submission requirements
* scholarly publishing reproducibility practices
* semantic publishing principles
