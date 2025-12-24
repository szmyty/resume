#!/usr/bin/env bash
set -euo pipefail

echo "==> Updating resume build to use local tectonic (no Docker)..."

# -----------------------------------------------------------------------------
# Safety checks
# -----------------------------------------------------------------------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: Working tree has uncommitted changes."
  echo "Please commit or stash changes before running this script."
  exit 1
fi

# -----------------------------------------------------------------------------
# Update engine/build.py
# -----------------------------------------------------------------------------
BUILD_PY="engine/build.py"

if [ ! -f "${BUILD_PY}" ]; then
  echo "ERROR: ${BUILD_PY} not found."
  exit 1
fi

echo "==> Patching ${BUILD_PY}..."

python3 <<'EOF'
from pathlib import Path
import re

path = Path("engine/build.py")
text = path.read_text(encoding="utf-8")

# Remove docker-based function
text = re.sub(
    r"def build_pdf_with_tectonic_docker[\s\S]+?return pdf_path\n",
    "",
    text,
    flags=re.MULTILINE,
)

# Insert local tectonic function
if "def build_pdf_with_tectonic(" not in text:
    insert_point = text.find("def normalize_variant_name")
    tectonic_func = """
def build_pdf_with_tectonic(build_dir: Path, tex_filename: str = "resume.tex") -> Path:
    pdf_filename = "resume.pdf"

    run_command(
        [
            "tectonic",
            "--print",
            "--synctex",
            "--keep-logs",
            tex_filename,
        ],
        working_directory=build_dir,
    )

    pdf_path = build_dir / pdf_filename
    if not pdf_path.exists():
        raise RuntimeError("PDF build succeeded but resume.pdf was not found.")

    return pdf_path

"""
    text = text[:insert_point] + tectonic_func + text[insert_point:]

# Replace call site
text = text.replace(
    "build_pdf_with_tectonic_docker(build_dir, \"resume.tex\")",
    "build_pdf_with_tectonic(build_dir, \"resume.tex\")",
)

path.write_text(text, encoding="utf-8")
EOF

# -----------------------------------------------------------------------------
# Update GitHub Actions workflow
# -----------------------------------------------------------------------------
WORKFLOW=".github/workflows/build-and-deploy-pages.yml"

if [ ! -f "${WORKFLOW}" ]; then
  echo "ERROR: ${WORKFLOW} not found."
  exit 1
fi

echo "==> Updating ${WORKFLOW} to install tectonic..."

if ! grep -q "Install Tectonic" "${WORKFLOW}"; then
  python3 <<'EOF'
from pathlib import Path

path = Path(".github/workflows/build-and-deploy-pages.yml")
lines = path.read_text().splitlines()

out = []
inserted = False

for line in lines:
    out.append(line)
    if line.strip() == "python -m pip install --requirement \"requirements.txt\"" and not inserted:
        out.extend([
            "",
            "      - name: Install Tectonic",
            "        run: |",
            "          sudo apt-get update",
            "          sudo apt-get install -y tectonic",
        ])
        inserted = True

path.write_text("\n".join(out))
EOF
else
  echo "    - Tectonic install step already present; skipping."
fi

# -----------------------------------------------------------------------------
# Final status
# -----------------------------------------------------------------------------
echo ""
echo "==> Update complete."
echo ""
echo "Next steps:"
echo "  git add engine/build.py .github/workflows/build-and-deploy-pages.yml"
echo "  git commit -m \"Switch PDF build to local tectonic (no Docker)\""
echo "  git push"
echo ""
echo "After push, check Actions → the workflow should go green."

