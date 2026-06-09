# TeXLive Compatibility Report

Generated at: `2026-05-27T18:38:12Z`

## Executive Summary

- Total checks: **20**
- Pass: **17**
- Warn: **3**
- Fail: **0**

Overall result: ⚠️ **Conditionally compatible** (non-failing issues remain)

## Goal Checklist

- [x] TeXLive version and toolchain declared
- [x] All packages compatible with TeXLive 2025
- [x] Compiler-specific package configuration validated
- [x] UTF-8 encoding declared and consistent
- [ ] TeXLive toolchain available in environment

## Detailed Checks

### Compiler compatibility

| Check | Result | Details |
| --- | --- | --- |
| inputenc is declared for pdflatex | ✅ PASS | inputenc is declared — required for pdflatex UTF-8 input handling. |
| fontenc with T1 encoding declared | ✅ PASS | fontenc with T1 encoding is declared for proper glyph support. |
| babel language support declared | ✅ PASS | babel language package is declared. |
| biblatex uses biber backend | ✅ PASS | biblatex is configured with backend=biber. |
| lmodern font package used | ✅ PASS | lmodern is used for modern T1-encoded Latin Modern fonts. |
| microtype is declared for typography | ✅ PASS | microtype is declared for pdflatex/lualatex micro-typography. |

### Encoding compatibility

| Check | Result | Details |
| --- | --- | --- |
| paper.tex is valid UTF-8 | ✅ PASS | paper.tex is encoded as valid UTF-8. |
| UTF-8 input encoding declared | ✅ PASS | inputenc[utf8] is declared for UTF-8 source file support. |
| All .tex files are valid UTF-8 | ✅ PASS | All .tex files under paper/ are valid UTF-8. |

### Package compatibility

| Check | Result | Details |
| --- | --- | --- |
| All packages are known in TeXLive 2025 | ✅ PASS | All 34 packages in reflector.sty are listed in the TeXLive 2025 package set. |
| No deprecated packages used | ✅ PASS | No deprecated or superseded packages found in reflector.sty. |
| All packages are pdflatex-compatible | ✅ PASS | All packages in reflector.sty are compatible with pdflatex. |
| No biblatex-incompatible packages used | ✅ PASS | No packages conflicting with biblatex are used. |

### TeXLive declarations

| Check | Result | Details |
| --- | --- | --- |
| TeXLive version declared in 00README.json | ✅ PASS | TeXLive version declared: '2025'. |
| Declared TeXLive version is current (2025+) | ✅ PASS | Declared TeXLive 2025 is a current release (2025 or later). |
| Compiler is declared in 00README.json | ✅ PASS | Compiler declared: 'pdflatex'. |
| Bibliography backend declared in 00README.json | ✅ PASS | Bibliography backend declared: 'biber'. |

### Toolchain availability

| Check | Result | Details |
| --- | --- | --- |
| latexmk is available | ⚠️ WARN | latexmk is not available in PATH — install TeXLive to enable local builds. |
| pdflatex is available | ⚠️ WARN | pdflatex is not available in PATH — install TeXLive to enable local builds. |
| biber is available | ⚠️ WARN | biber is not available in PATH — install TeXLive to enable local builds. |

## Package Compatibility Matrix

Packages declared in `paper/styles/reflector.sty` against TeXLive 2025:

| Package | TeXLive 2025 Collection | pdflatex Compatible | Notes |
| --- | --- | --- | --- |
| `inputenc` | base | ✅ | — |
| `fontenc` | base | ✅ | — |
| `babel` | required | ✅ | — |
| `lmodern` | recommended | ✅ | — |
| `microtype` | recommended | ✅ | — |
| `geometry` | recommended | ✅ | — |
| `setspace` | recommended | ✅ | — |
| `parskip` | recommended | ✅ | — |
| `xcolor` | recommended | ✅ | — |
| `hyperref` | recommended | ✅ | — |
| `bookmark` | recommended | ✅ | — |
| `biblatex` | recommended | ✅ | — |
| `graphicx` | base | ✅ | — |
| `float` | recommended | ✅ | — |
| `caption` | recommended | ✅ | — |
| `subcaption` | recommended | ✅ | — |
| `booktabs` | recommended | ✅ | — |
| `array` | base | ✅ | — |
| `longtable` | recommended | ✅ | — |
| `tabularx` | recommended | ✅ | — |
| `listings` | recommended | ✅ | — |
| `amsmath` | required | ✅ | — |
| `amssymb` | required | ✅ | — |
| `amsthm` | required | ✅ | — |
| `mathtools` | recommended | ✅ | — |
| `bm` | required | ✅ | — |
| `enumitem` | recommended | ✅ | — |
| `csquotes` | recommended | ✅ | — |
| `multirow` | recommended | ✅ | — |
| `makecell` | recommended | ✅ | — |
| `cleveref` | recommended | ✅ | — |
| `tcolorbox` | full | ✅ | — |
| `fancyhdr` | recommended | ✅ | — |
| `titlesec` | recommended | ✅ | — |

## Unresolved Issues

- ⚠️ **Toolchain availability / latexmk is available**: latexmk is not available in PATH — install TeXLive to enable local builds.
- ⚠️ **Toolchain availability / pdflatex is available**: pdflatex is not available in PATH — install TeXLive to enable local builds.
- ⚠️ **Toolchain availability / biber is available**: biber is not available in PATH — install TeXLive to enable local builds.

## Recommended Fixes

- Install `latexmk` via TeXLive (`tlmgr install latexmk`) or install full TeXLive 2025.
- Install `pdflatex` via TeXLive (`tlmgr install pdflatex`) or install full TeXLive 2025.
- Install `biber` via TeXLive (`tlmgr install biber`) or install full TeXLive 2025.

## TeXLive 2025 Compatibility Assessment

**Compatibility confidence: Medium**

The reflector paper style (`reflector.sty`) uses well-established LaTeX packages that have been part of TeXLive for many years and are compatible with TeXLive 2025. The pdflatex + biber + biblatex combination is the recommended arXiv compilation stack.
