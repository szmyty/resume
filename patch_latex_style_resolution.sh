#!/usr/bin/env bash
set -euo pipefail

echo "==> Patching LaTeX style resolution (TEXINPUTS + flat styles)..."

# Safety checks
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: Working tree has uncommitted changes."
  echo "Please commit or stash changes before running this script."
  exit 1
fi

# ------------------------------------------------------------------------------
# 1. Move styles to engine/styles
# ------------------------------------------------------------------------------
echo "==> Moving styles to engine/styles..."

mkdir -p engine/styles

if [ -d engine/latex/styles ]; then
  git mv engine/latex/styles/*.sty engine/styles/ || true
  git rm -r engine/latex/styles || true
fi

# ------------------------------------------------------------------------------
# 2. Write base.sty
# ------------------------------------------------------------------------------
echo "==> Writing engine/styles/base.sty..."

cat <<'EOF' > engine/styles/base.sty
\ProvidesPackage{base}

\usepackage{enumitem}
\usepackage{titlesec}

\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

\setlist[itemize]{leftmargin=1.2em}

\titleformat{\section}
  {\normalfont\large\bfseries}
  {}
  {0pt}
  {}

\titleformat{\subsection}
  {\normalfont\bfseries}
  {}
  {0pt}
  {}
EOF

# ------------------------------------------------------------------------------
# 3. Write default.sty
# ------------------------------------------------------------------------------
echo "==> Writing engine/styles/default.sty..."

cat <<'EOF' > engine/styles/default.sty
\ProvidesPackage{default}

\usepackage{base}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

\linespread{1.05}
EOF

# ------------------------------------------------------------------------------
# 4. Write compact.sty
# ------------------------------------------------------------------------------
echo "==> Writing engine/styles/compact.sty..."

cat <<'EOF' > engine/styles/compact.sty
\ProvidesPackage{compact}

\usepackage{base}

\linespread{0.96}
\setlength{\parskip}{4pt}
\setlist[itemize]{itemsep=2pt}
EOF

# ------------------------------------------------------------------------------
# 5. Patch resume.tex.j2 to load styles by name
# ------------------------------------------------------------------------------
echo "==> Patching engine/latex/resume.tex.j2..."

RESUME_TEX="engine/latex/resume.tex.j2"

python3 <<'EOF'
from pathlib import Path
import re

path = Path("engine/latex/resume.tex.j2")
text = path.read_text(encoding="utf-8")

text = re.sub(
    r"\\usepackage\{engine/latex/styles/\{\{\s*config\.style\.base\s*\}\}\}",
    r"\\usepackage{{{ config.style.base }}}",
    text,
)

text = re.sub(
    r"\\usepackage\{engine/latex/styles/\{\{\s*config\.style\.override\s*\}\}\}",
    r"\\usepackage{{{ config.style.override }}}",
    text,
)

path.write_text(text, encoding="utf-8")
EOF

# ------------------------------------------------------------------------------
# 6. Patch engine/build.py to set TEXINPUTS
# ------------------------------------------------------------------------------
echo "==> Patching engine/build.py..."

BUILD_PY="engine/build.py"

python3 <<'EOF'
from pathlib import Path
import re

path = Path("engine/build.py")
text = path.read_text(encoding="utf-8")

if "import os" not in text:
    text = "import os\n" + text

text = re.sub(
    r"run_command\(\s*\[\s*\"tectonic\"[\s\S]*?\]\s*,\s*working_directory=build_dir\s*\)",
    """run_command(
        [
            "tectonic",
            "--print",
            "--synctex",
            "--keep-logs",
            tex_filename,
        ],
        working_directory=build_dir,
        env={**os.environ, "TEXINPUTS": f"{build_dir}/engine/styles:"},
    )""",
    text,
    flags=re.MULTILINE,
)

path.write_text(text, encoding="utf-8")
EOF

echo ""
echo "==> Patch complete."
echo ""
echo "Next steps:"
echo "  git add engine"
echo "  git commit -m \"Fix LaTeX style resolution via TEXINPUTS\""
echo "  git push"
echo ""
echo "Then watch GitHub Actions — PDF build should succeed."

