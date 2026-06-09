# arXiv Packaging Validation Report

Generated at: `2026-05-28T00:28:58Z`

## Executive Summary

- Total checks: **31**
- Pass: **31**
- Warn: **0**
- Fail: **0**

Overall result: ✅ **arXiv upload-ready**

## Goal Checklist

- [x] Validate arXiv manifest (00README.json)
- [x] Validate source declarations
- [x] Validate upload structure
- [x] Validate figure format compatibility
- [x] Validate bibliography compatibility

## Detailed Checks

### Bibliography

| Check | Result | Details |
| --- | --- | --- |
| Bibliography file is non-empty | ✅ PASS | references.bib contains 15 bibliography entries. |
| Compiler/bibliography combination is compatible | ✅ PASS | Compiler 'pdflatex' + bibliography 'biber' is a known-compatible combination. |
| biblatex uses biber backend | ✅ PASS | biblatex is configured with backend=biber. |

### Figure compatibility

| Check | Result | Details |
| --- | --- | --- |
| All figure formats are arXiv-safe | ✅ PASS | All 18 figure files use arXiv-safe image formats. |
| All figure files are within arXiv size limits | ✅ PASS | All figure files are within the 10 MB per-file size limit. |
| Total paper bundle within arXiv upload limit | ✅ PASS | Total paper bundle size is 378 KB, within the 50 MB arXiv upload limit. |

### Manifest

| Check | Result | Details |
| --- | --- | --- |
| 00README.json is parseable JSON | ✅ PASS | paper/00README.json is valid JSON. |
| 00README schema references arXiv | ✅ PASS | 00README $schema references the arXiv 00readme schema. |
| 00README required root keys present | ✅ PASS | 00README includes all required root keys. |
| Compiler is declared | ✅ PASS | Compiler declared in process block: 'pdflatex'. |
| Compiler is arXiv-supported | ✅ PASS | Declared compiler 'pdflatex' is supported by arXiv. |
| Bibliography tool is declared | ✅ PASS | Bibliography tool declared: 'biber'. |
| Bibliography tool is supported | ✅ PASS | Declared bibliography tool 'biber' is supported. |
| Deterministic flag is set | ✅ PASS | process.deterministic is true in 00README. |
| TeXLive version declared | ✅ PASS | TeXLive version declared in process block: '2025'. |
| max_repeat declared | ✅ PASS | process.max_repeat declared as 10. |
| Build script declared | ✅ PASS | build.script declared: 'scripts/build-paper.sh'. |
| Orchestration config declared | ✅ PASS | build.orchestration declared: '.latexmkrc'. |

### Source declarations

| Check | Result | Details |
| --- | --- | --- |
| All source usage values are valid | ✅ PASS | All declared source usage values are valid. |
| No absolute source paths | ✅ PASS | All source paths are relative. |
| No path-escaping source declarations | ✅ PASS | No source paths escape the paper/ bundle directory. |
| All declared sources exist on disk | ✅ PASS | All declared sources exist under paper/. |
| All source file types are arXiv-safe | ✅ PASS | All declared source file extensions are arXiv-safe. |
| Exactly one toplevel source declared | ✅ PASS | Exactly one toplevel source is declared. |
| Bibliography file declared in sources | ✅ PASS | A .bib bibliography file is declared in sources. |
| Style file declared in sources | ✅ PASS | A .sty publication style file is declared in sources. |

### Upload structure

| Check | Result | Details |
| --- | --- | --- |
| No symlinks in paper bundle | ✅ PASS | No symlinks found under paper/. |
| No system files in paper bundle | ✅ PASS | No banned system files found under paper/. |
| No build artifacts declared as sources | ✅ PASS | No build artifact paths (.cache/, .aux, .log, .fls) appear in source declarations. |
| Toplevel paper.tex exists | ✅ PASS | paper/paper.tex exists as the toplevel LaTeX entrypoint. |
| references.bib exists | ✅ PASS | paper/references.bib exists. |

## arXiv Upload Checklist

- [x] 00README.json is valid and complete
- [x] All sources declared, present, and arXiv-safe
- [x] Upload bundle is clean (no symlinks, no artifacts, no system files)
- [x] All figures are in arXiv-compatible formats and within size limits
- [x] Bibliography compilation path is arXiv-compatible
