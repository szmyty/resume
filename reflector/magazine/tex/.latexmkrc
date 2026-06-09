# Magazine latexmkrc
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

$pdf_mode = 1;
$dvi_mode = 0;
$postscript_mode = 0;
$force_mode = 1;

# Keep magazine build artifacts isolated from paper build outputs.
$aux_dir = '../.cache/aux';
$out_dir = '../.cache/out';

$max_repeat = 10;
$silent = 0;

$pdflatex = 'pdflatex %O -interaction=nonstopmode -file-line-error -halt-on-error %S';

@generated_exts = qw(
  aux bbl bcf blg fdb_latexmk fls log out run.xml synctex.gz toc lof lot
);
