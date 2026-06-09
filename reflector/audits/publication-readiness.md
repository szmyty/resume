# Publication Readiness Audit Report

Generated at: `2026-05-30T18:16:45Z`

## Executive Summary

- Total checks: **30**
- Pass: **29**
- Warn: **0**
- Fail: **1**

Overall result: ❌ **Not publication-ready**

## Goal Checklist

- [x] Validate arXiv compatibility
- [x] Validate publication structure
- [x] Validate bibliography integrity
- [x] Validate figure references
- [x] Validate GitHub Pages deployment
- [x] Validate metadata consistency
- [ ] Validate deterministic builds
- [x] Generate publication readiness report

## Detailed Checks

### Bibliography integrity

| Check | Result | Details |
| --- | --- | --- |
| All citation keys resolve to bibliography entries | ✅ PASS | All 15 citation keys resolve in references.bib. |
| Bibliography keys are unique | ✅ PASS | All 15 bibliography keys are unique. |
| Bibliography entries include core metadata | ✅ PASS | All bibliography entries contain at least author and title fields. |
| Bibliography entry structure is parseable | ✅ PASS | All bibliography entries have parseable field structure. |
| DOI fields use canonical BibLaTeX value format | ✅ PASS | All DOI fields use canonical DOI values (no URL/doi: prefixes). |
| DOI URLs match DOI field values | ✅ PASS | All DOI URLs resolve to the canonical https://doi.org/<doi> form. |
| arXiv metadata is canonical | ✅ PASS | All arXiv entries use canonical eprinttype/eprint/url metadata. |

### Deterministic builds

| Check | Result | Details |
| --- | --- | --- |
| Build configuration declares deterministic controls | ✅ PASS | .latexmkrc declares deterministic max repeat and fixed output/aux directories. |
| Build script uses repository orchestration | ✅ PASS | scripts/build-paper.sh invokes the root .latexmkrc orchestration config. |

### Figure integrity

| Check | Result | Details |
| --- | --- | --- |
| All referenced figure files exist | ✅ PASS | All 17 figure references resolve to files. |
| Figure file formats are render-safe | ✅ PASS | All figure files use supported render-safe image formats. |
| Referenced figures have prompt-preservation files | ✅ PASS | All referenced figures have prompt files in paper/figures/prompts/. |
| Prompt files include recursive metadata headings | ✅ PASS | All figure prompt files contain required recursive-metadata headings. |
| Referenced PNG dimensions are canonical | ✅ PASS | All referenced PNG figures match canonical dimensions. |
| Figure blocks include captions | ✅ PASS | All 17 figure blocks include captions. |
| Figure blocks include fig: labels | ✅ PASS | All 17 figure blocks include fig: labels. |
| Referenced figures are listed in figures/manifest.md | ✅ PASS | All referenced figures are represented in figures/manifest.md. |

### GitHub Pages deployment

| Check | Result | Details |
| --- | --- | --- |
| Pages workflow deploys publication artifacts | ✅ PASS | Pages workflow includes build, synchronization, verification, and deploy steps. |
| docs landing page links publication artifacts | ✅ PASS | docs/index.html links canonical publication artifacts. |

### LaTeX and build validation

| Check | Result | Details |
| --- | --- | --- |
| Paper compiles cleanly | ❌ FAIL | ./scripts/build-paper.sh paper failed: Building: /home/runner/work/reflector/reflector/paper/paper.tex
Output:   /home/runner/work/reflector/reflector/paper/.cache/out/
Rc files read:
  /etc/LatexMk
  /home/runner/work/reflector/reflector/.latexmkrc
Latexmk: Run number 1 of rule 'pdflatex'
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) (preloaded format=pdflatex)
 \write18 enabled.
entering extended mode
Latexmk: Getting log file '.cache/aux/paper.log'
Collected error summary (may duplicate other messages):
  pdflatex: Command for 'pdflatex' gave return code 1
      Refer to '.cache/aux/paper.log' and/or above output for details

::group::LaTeX diagnostics summary
Paper directory: /home/runner/work/reflector/reflector/paper
Aux directory:   /home/runner/work/reflector/reflector/paper/.cache/aux
Output directory: /home/runner/work/reflector/reflector/paper/.cache/out
LaTeX log:       /home/runner/work/reflector/reflector/paper/.cache/aux/paper.log
Biber log:       /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
Partial PDF:     /home/runner/work/reflector/reflector/paper/.cache/out/paper.pdf
Partial PDF not found.
::endgroup::
::group::LATEX LOG TAIL
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) (preloaded format=pdflatex 2026.5.30)  30 MAY 2026 18:16
entering extended mode
 \write18 enabled.
 file:line:error style messages enabled.
 %&-line parsing enabled.
**paper.tex
(./paper.tex
LaTeX2e <2023-11-01> patch level 1
L3 programming layer <2024-01-22>
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2023/05/17 v1.4n Standard LaTeX document class
(/usr/share/texlive/texmf-dist/tex/latex/base/size11.clo
File: size11.clo 2023/05/17 v1.4n Standard LaTeX file (size option)
)
\c@part=\count187
\c@section=\count188
\c@subsection=\count189
\c@subsubsection=\count190
\c@paragraph=\count191
\c@subparagraph=\count192
\c@figure=\count193
\c@table=\count194
\abovecaptionskip=\skip48
\belowcaptionskip=\skip49
\bibindent=\dimen140
) (./macros/metadata.tex (./config/title.tex)) (./styles/reflector.sty
Package: reflector 2025/01/01 reflector Publication Style
(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty
Package: inputenc 2021/02/14 v1.3d Input encoding file
\inpenc@prehook=\toks17
\inpenc@posthook=\toks18
) (/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty
Package: fontenc 2021/04/29 v2.0v Standard LaTeX package
) (/usr/share/texlive/texmf-dist/tex/generic/babel/babel.sty
Package: babel 2024/01/07 v24.1 The Babel package
\babel@savecnt=\count195
\U@D=\dimen141
\l@unhyphenated=\language5
(/usr/share/texlive/texmf-dist/tex/generic/babel/txtbabel.def)
\bbl@readstream=\read2
\bbl@dirlevel=\count196
(/usr/share/texlive/texmf-dist/tex/generic/babel-english/english.ldf
Language: english 2017/06/06 v3.3r English support from the babel system
Package babel Info: Hyphen rules for 'british' set to \l@english
(babel)             (\language0). Reported on input line 82.
Package babel Info: Hyphen rules for 'UKenglish' set to \l@english
(babel)             (\language0). Reported on input line 83.
Package babel Info: Hyphen rules for 'canadian' set to \l@english
(babel)             (\language0). Reported on input line 102.
Package babel Info: Hyphen rules for 'australian' set to \l@english
(babel)             (\language0). Reported on input line 105.
Package babel Info: Hyphen rules for 'newzealand' set to \l@english
(babel)             (\language0). Reported on input line 108.
)) (/usr/share/texlive/texmf-dist/tex/generic/babel/locale/en/babel-english.tex
Package babel Info: Importing font and identification data for english
(babel)             from babel-en.ini. Reported on input line 11.
)

! LaTeX Error: File `lmodern.sty' not found.

Type X to quit or <RETURN> to proceed,
or enter new name. (Default extension: sty)

Enter file name:
./styles/reflector.sty:17: Emergency stop.
<read *>

l.17 \RequirePackage
                    {microtype}^^M
Here is how much of TeX's memory you used:
 1537 strings out of 476182
 24812 string characters out of 5795595
 1922975 words of memory out of 5000000
 23595 multiletter control sequences out of 15000+600000
 559138 words of font info for 38 fonts, out of 8000000 for 9000
 14 hyphenation exceptions out of 8191
 55i,0n,66p,143b,103s stack positions out of 10000i,1000n,20000p,200000b,200000s

./styles/reflector.sty:17:  ==> Fatal error occurred, no output PDF file produc
ed!
::endgroup::
::group::LIKELY LATEX FAILURES
59:! LaTeX Error: File `lmodern.sty' not found.
65:./styles/reflector.sty:17: Emergency stop.
79:./styles/reflector.sty:17:  ==> Fatal error occurred, no output PDF file produc
::endgroup::
::group::MISSING FILES OR INCLUDES
59:! LaTeX Error: File `lmodern.sty' not found.
::endgroup::
::group::REFERENCE WARNINGS
No matches found.
::endgroup::
::group::BIBER OUTPUT
Not found: /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
::endgroup::
::group::BIBER WARNINGS
Not found: /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
::endgroup::
Failure to make '.cache/out/paper.pdf'
LaTeX build failed. Printing focused diagnostics... |

### Metadata consistency

| Check | Result | Details |
| --- | --- | --- |
| Cross-file metadata validation | ✅ PASS | scripts/validate-metadata.py passed. |

### Publication structure

| Check | Result | Details |
| --- | --- | --- |
| Required publication files | ✅ PASS | All required publication and workflow files are present. |
| Section source files exist | ✅ PASS | Found 18 section .tex files under paper/sections. |

### arXiv compatibility

| Check | Result | Details |
| --- | --- | --- |
| 00README.json is parseable JSON | ✅ PASS | paper/00README.json is valid JSON. |
| 00README schema points to arXiv | ✅ PASS | 00README schema matches arXiv 00readme schema URL. |
| 00README required root keys | ✅ PASS | 00README includes required manifest root keys. |
| Source usage values are supported | ✅ PASS | All declared source usage values are supported. |
| Declared sources exist | ✅ PASS | All sources listed in 00README exist under paper/. |
| Declared source file types are upload-safe | ✅ PASS | Declared source file extensions are arXiv-safe. |
| Single toplevel source declared | ✅ PASS | Exactly one toplevel source is declared in 00README. |

## arXiv Compatibility Report

- ✅ **00README.json is parseable JSON** — paper/00README.json is valid JSON.
- ✅ **00README schema points to arXiv** — 00README schema matches arXiv 00readme schema URL.
- ✅ **00README required root keys** — 00README includes required manifest root keys.
- ✅ **Source usage values are supported** — All declared source usage values are supported.
- ✅ **Declared sources exist** — All sources listed in 00README exist under paper/.
- ✅ **Declared source file types are upload-safe** — Declared source file extensions are arXiv-safe.
- ✅ **Single toplevel source declared** — Exactly one toplevel source is declared in 00README.

## Unresolved Issues

- FAIL: LaTeX and build validation — Paper compiles cleanly: ./scripts/build-paper.sh paper failed: Building: /home/runner/work/reflector/reflector/paper/paper.tex
Output:   /home/runner/work/reflector/reflector/paper/.cache/out/
Rc files read:
  /etc/LatexMk
  /home/runner/work/reflector/reflector/.latexmkrc
Latexmk: Run number 1 of rule 'pdflatex'
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) (preloaded format=pdflatex)
 \write18 enabled.
entering extended mode
Latexmk: Getting log file '.cache/aux/paper.log'
Collected error summary (may duplicate other messages):
  pdflatex: Command for 'pdflatex' gave return code 1
      Refer to '.cache/aux/paper.log' and/or above output for details

::group::LaTeX diagnostics summary
Paper directory: /home/runner/work/reflector/reflector/paper
Aux directory:   /home/runner/work/reflector/reflector/paper/.cache/aux
Output directory: /home/runner/work/reflector/reflector/paper/.cache/out
LaTeX log:       /home/runner/work/reflector/reflector/paper/.cache/aux/paper.log
Biber log:       /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
Partial PDF:     /home/runner/work/reflector/reflector/paper/.cache/out/paper.pdf
Partial PDF not found.
::endgroup::
::group::LATEX LOG TAIL
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) (preloaded format=pdflatex 2026.5.30)  30 MAY 2026 18:16
entering extended mode
 \write18 enabled.
 file:line:error style messages enabled.
 %&-line parsing enabled.
**paper.tex
(./paper.tex
LaTeX2e <2023-11-01> patch level 1
L3 programming layer <2024-01-22>
(/usr/share/texlive/texmf-dist/tex/latex/base/article.cls
Document Class: article 2023/05/17 v1.4n Standard LaTeX document class
(/usr/share/texlive/texmf-dist/tex/latex/base/size11.clo
File: size11.clo 2023/05/17 v1.4n Standard LaTeX file (size option)
)
\c@part=\count187
\c@section=\count188
\c@subsection=\count189
\c@subsubsection=\count190
\c@paragraph=\count191
\c@subparagraph=\count192
\c@figure=\count193
\c@table=\count194
\abovecaptionskip=\skip48
\belowcaptionskip=\skip49
\bibindent=\dimen140
) (./macros/metadata.tex (./config/title.tex)) (./styles/reflector.sty
Package: reflector 2025/01/01 reflector Publication Style
(/usr/share/texlive/texmf-dist/tex/latex/base/inputenc.sty
Package: inputenc 2021/02/14 v1.3d Input encoding file
\inpenc@prehook=\toks17
\inpenc@posthook=\toks18
) (/usr/share/texlive/texmf-dist/tex/latex/base/fontenc.sty
Package: fontenc 2021/04/29 v2.0v Standard LaTeX package
) (/usr/share/texlive/texmf-dist/tex/generic/babel/babel.sty
Package: babel 2024/01/07 v24.1 The Babel package
\babel@savecnt=\count195
\U@D=\dimen141
\l@unhyphenated=\language5
(/usr/share/texlive/texmf-dist/tex/generic/babel/txtbabel.def)
\bbl@readstream=\read2
\bbl@dirlevel=\count196
(/usr/share/texlive/texmf-dist/tex/generic/babel-english/english.ldf
Language: english 2017/06/06 v3.3r English support from the babel system
Package babel Info: Hyphen rules for 'british' set to \l@english
(babel)             (\language0). Reported on input line 82.
Package babel Info: Hyphen rules for 'UKenglish' set to \l@english
(babel)             (\language0). Reported on input line 83.
Package babel Info: Hyphen rules for 'canadian' set to \l@english
(babel)             (\language0). Reported on input line 102.
Package babel Info: Hyphen rules for 'australian' set to \l@english
(babel)             (\language0). Reported on input line 105.
Package babel Info: Hyphen rules for 'newzealand' set to \l@english
(babel)             (\language0). Reported on input line 108.
)) (/usr/share/texlive/texmf-dist/tex/generic/babel/locale/en/babel-english.tex
Package babel Info: Importing font and identification data for english
(babel)             from babel-en.ini. Reported on input line 11.
)

! LaTeX Error: File `lmodern.sty' not found.

Type X to quit or <RETURN> to proceed,
or enter new name. (Default extension: sty)

Enter file name:
./styles/reflector.sty:17: Emergency stop.
<read *>

l.17 \RequirePackage
                    {microtype}^^M
Here is how much of TeX's memory you used:
 1537 strings out of 476182
 24812 string characters out of 5795595
 1922975 words of memory out of 5000000
 23595 multiletter control sequences out of 15000+600000
 559138 words of font info for 38 fonts, out of 8000000 for 9000
 14 hyphenation exceptions out of 8191
 55i,0n,66p,143b,103s stack positions out of 10000i,1000n,20000p,200000b,200000s

./styles/reflector.sty:17:  ==> Fatal error occurred, no output PDF file produc
ed!
::endgroup::
::group::LIKELY LATEX FAILURES
59:! LaTeX Error: File `lmodern.sty' not found.
65:./styles/reflector.sty:17: Emergency stop.
79:./styles/reflector.sty:17:  ==> Fatal error occurred, no output PDF file produc
::endgroup::
::group::MISSING FILES OR INCLUDES
59:! LaTeX Error: File `lmodern.sty' not found.
::endgroup::
::group::REFERENCE WARNINGS
No matches found.
::endgroup::
::group::BIBER OUTPUT
Not found: /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
::endgroup::
::group::BIBER WARNINGS
Not found: /home/runner/work/reflector/reflector/paper/.cache/aux/paper.blg
::endgroup::
Failure to make '.cache/out/paper.pdf'
LaTeX build failed. Printing focused diagnostics...

## Recommended Fixes

- Resolve: **LaTeX and build validation / Paper compiles cleanly**.

## Final Publication Checklist

- [ ] Paper deemed structurally publication-ready
- [x] arXiv compatibility verified
- [x] unresolved publication blockers identified
- [ ] deterministic build confidence improved
- [x] repository publication architecture validated
