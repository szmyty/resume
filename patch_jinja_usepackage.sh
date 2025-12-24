#!/usr/bin/env bash
set -euo pipefail

echo "==> Fixing Jinja \\usepackage syntax..."

TEMPLATE="engine/latex/resume.tex.j2"

if [ ! -f "${TEMPLATE}" ]; then
  echo "ERROR: ${TEMPLATE} not found."
  exit 1
fi

python3 <<'EOF'
from pathlib import Path
import re

path = Path("engine/latex/resume.tex.j2")
text = path.read_text(encoding="utf-8")

# Replace triple-brace usepackage with correct Jinja syntax
text = re.sub(
    r"\\usepackage\{\{\{\s*config\.style\.base\s*\}\}\}",
    r"\\usepackage{{ config.style.base }}",
    text,
)

text = re.sub(
    r"\\usepackage\{\{\{\s*config\.style\.override\s*\}\}\}",
    r"\\usepackage{{ config.style.override }}",
    text,
)

path.write_text(text, encoding="utf-8")
EOF

echo ""
echo "==> Patch complete."
echo ""
echo "Next steps:"
echo "  git add engine/latex/resume.tex.j2"
echo "  git commit -m \"Fix Jinja usepackage syntax\""
echo "  git push"

