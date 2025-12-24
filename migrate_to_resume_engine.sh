#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# migrate_to_resume_engine.sh
#
# Migrates current repo into a "resume engine" + "resume variants" architecture,
# and adds a GitHub Pages deployment pipeline.
#
# Assumptions:
# - Repo name is "resume" (for https://szmyty.github.io/resume/)
# - Default branch is "main"
# - GitHub Pages uses Actions deployment (recommended)
# -----------------------------------------------------------------------------

REPO_ROOT="$(pwd)"
TIMESTAMP="$(date "+%Y%m%d_%H%M%S")"
ARCHIVE_DIR="archive/legacy_${TIMESTAMP}"

require_command() {
  local command_name="$1"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "ERROR: Missing required command: ${command_name}"
    exit 1
  fi
}

echo "==> Checking prerequisites..."
require_command "git"
require_command "python3"

echo "==> Verifying this is a git repository..."
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository."
  exit 1
fi

echo "==> Verifying working tree is clean..."
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: Working tree has uncommitted changes."
  echo "Please commit or stash changes, then rerun."
  exit 1
fi

echo "==> Creating archive directory: ${ARCHIVE_DIR}"
mkdir -p "${ARCHIVE_DIR}"

# -----------------------------------------------------------------------------
# Archive existing legacy files (pdf2htmlEX and older top-level artifacts)
# -----------------------------------------------------------------------------
echo "==> Archiving legacy artifacts (if present)..."

move_if_exists() {
  local source_path="$1"
  local target_dir="$2"
  if [ -e "${source_path}" ]; then
    echo "    - Moving ${source_path} -> ${target_dir}/"
    mkdir -p "${target_dir}"
    git mv "${source_path}" "${target_dir}/" 2>/dev/null || mv "${source_path}" "${target_dir}/"
  fi
}

# Top-level legacy files frequently present in your repo
move_if_exists "resume.html" "${ARCHIVE_DIR}"
move_if_exists "resume.md" "${ARCHIVE_DIR}"
move_if_exists "resume.pdf" "${ARCHIVE_DIR}"

# docs/ legacy (we will replace docs with site deployment)
# Keep README.md at root; keep docs/.gitkeep if you want, but we're moving docs/ aside.
move_if_exists "docs" "${ARCHIVE_DIR}"

# pdf2htmlEX output folder called "resume/"
move_if_exists "resume" "${ARCHIVE_DIR}"

echo "==> Creating new repo structure..."
mkdir -p "engine/latex/sections"
mkdir -p "engine/latex/styles"
mkdir -p "engine/html"
mkdir -p "resumes/career_center"
mkdir -p "scripts"
mkdir -p ".github/workflows"
mkdir -p "site"

# -----------------------------------------------------------------------------
# requirements.txt
# -----------------------------------------------------------------------------
echo "==> Writing requirements.txt"
cat <<'EOF' > "requirements.txt"
jinja2==3.1.4
pyyaml==6.0.2
EOF

# -----------------------------------------------------------------------------
# Engine: LaTeX styles (base + default + compact)
# -----------------------------------------------------------------------------
echo "==> Writing LaTeX styles..."

cat <<'EOF' > "engine/latex/styles/base.sty"
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

cat <<'EOF' > "engine/latex/styles/default.sty"
\ProvidesPackage{default}

\usepackage{base}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

\linespread{1.05}
EOF

cat <<'EOF' > "engine/latex/styles/compact.sty"
\ProvidesPackage{compact}

\usepackage{base}

\linespread{0.96}
\setlength{\parskip}{4pt}
\setlist[itemize]{itemsep=2pt}
EOF

# -----------------------------------------------------------------------------
# Engine: LaTeX templates (Jinja2)
# -----------------------------------------------------------------------------
echo "==> Writing LaTeX templates..."

cat <<'EOF' > "engine/latex/resume.tex.j2"
\documentclass[11pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage{hyperref}

\usepackage{engine/latex/styles/{{ config.style.base }}}
{% if config.style.override %}
\usepackage{engine/latex/styles/{{ config.style.override }}}
{% endif %}

\begin{document}

\input{engine/latex/sections/header.tex}
\input{engine/latex/sections/mission.tex}
\input{engine/latex/sections/experience.tex}
\input{engine/latex/sections/education.tex}
\input{engine/latex/sections/interests.tex}

\end{document}
EOF

cat <<'EOF' > "engine/latex/sections/header.tex.j2"
\begin{center}
{\Large \textbf{ {{ config.name }} }} \\[6pt]
{{ config.contact.address }} \\
{{ config.contact.phone }} \\
\href{mailto:{{ config.contact.email }}}{{ config.contact.email }} \\
\href{https://{{ config.contact.github }}}{{ config.contact.github }}
\end{center}

\vspace{10pt}
EOF

cat <<'EOF' > "engine/latex/sections/mission.tex.j2"
\section*{Mission Statement}

{{ config.mission }}
EOF

cat <<'EOF' > "engine/latex/sections/experience.tex.j2"
\section*{Work Experience}

{% for role in config.experience %}
\subsection*{ {{ role.company }}, {{ role.location }} — {{ role.title }} \hfill {{ role.dates }} }

{{ role.summary }}

\textbf{Highlights included:}
\begin{itemize}[leftmargin=1.2em]
{% for bullet in role.highlights %}
  \item {{ bullet }}
{% endfor %}
\end{itemize}

{% endfor %}
EOF

cat <<'EOF' > "engine/latex/sections/education.tex.j2"
\section*{Education}

{% for edu in config.education %}
\subsection*{ {{ edu.school }} — {{ edu.degree }} \hfill {{ edu.dates }} }

{% if edu.details %}
\begin{itemize}[leftmargin=1.2em]
{% for bullet in edu.details %}
  \item {{ bullet }}
{% endfor %}
\end{itemize}
{% endif %}

{% endfor %}
EOF

cat <<'EOF' > "engine/latex/sections/interests.tex.j2"
\section*{Interests}

{{ config.interests }}
EOF

# -----------------------------------------------------------------------------
# Engine: HTML template (Jinja2) - simple, print-friendly, reference-like
# -----------------------------------------------------------------------------
echo "==> Writing HTML template..."

cat <<'EOF' > "engine/html/resume.html.j2"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ config.name }} - Resume</title>
  <style>
    body { font-family: "Times New Roman", Times, serif; max-width: 800px; margin: 0 auto; padding: 48px 56px; color: #111; line-height: 1.35; }
    h1 { text-align: center; font-size: 28px; margin: 0; }
    .contact { text-align: center; margin-top: 10px; margin-bottom: 18px; }
    h2 { font-size: 16px; font-weight: bold; margin-top: 18px; margin-bottom: 6px; }
    .role { margin-top: 10px; }
    .role-title { font-weight: bold; }
    .role-meta { font-weight: normal; }
    p { margin: 6px 0; text-align: justify; }
    ul { margin: 6px 0 10px 22px; }
    li { margin: 4px 0; }
    .tech { margin-top: 6px; }
    .section-rule { border: none; border-top: 1px solid #999; margin: 14px 0; }
    a { color: #111; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>

  <h1>{{ config.name }}</h1>
  <div class="contact">
    {{ config.contact.address }}<br>
    {{ config.contact.phone }}<br>
    <a href="mailto:{{ config.contact.email }}">{{ config.contact.email }}</a><br>
    <a href="https://{{ config.contact.github }}">{{ config.contact.github }}</a>
  </div>

  <h2>Mission Statement</h2>
  <p>{{ config.mission }}</p>

  <h2>Work Experience</h2>
  {% for role in config.experience %}
    <div class="role">
      <div class="role-title">
        {{ role.company }}, {{ role.location }} – {{ role.title }}
        <span class="role-meta">{{ role.dates }}</span>
      </div>
      <p>{{ role.summary }}</p>
      <div><strong>Highlights included:</strong></div>
      <ul>
        {% for bullet in role.highlights %}
          <li>{{ bullet }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endfor %}

  <h2>Education</h2>
  {% for edu in config.education %}
    <div class="role">
      <div class="role-title">
        {{ edu.school }} – {{ edu.degree }} <span class="role-meta">{{ edu.dates }}</span>
      </div>
      {% if edu.details %}
        <ul>
          {% for bullet in edu.details %}
            <li>{{ bullet }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    </div>
  {% endfor %}

  <h2>Interests</h2>
  <p>{{ config.interests }}</p>

</body>
</html>
EOF

# -----------------------------------------------------------------------------
# First resume variant YAML (career_center) using your current content
# -----------------------------------------------------------------------------
echo "==> Writing initial resume variant: resumes/career_center/resume.yaml"

cat <<'EOF' > "resumes/career_center/resume.yaml"
name: "Alan Szmyt"

contact:
  address: "3233 Avalon Drive, Wilmington, MA 01887"
  phone: "(978) 491-8932"
  email: "szmyty@gmail.com"
  github: "github.com/szmyty"

style:
  base: "default"
  override: null

mission: >
  To design and engineer intelligent, adaptable, and elegantly built systems — blending software, data,
  and creative technology into experiences that are efficient, expressive, and human-centered.

experience:
  - company: "MIT Lincoln Laboratory"
    location: "Lexington, MA"
    title: "Software Engineer, Associate Staff"
    dates: "April 2019 – Present"
    summary: >
      Developed full-stack geospatial and decision-support systems for research sponsors, integrating modern data
      engineering, visualization, and automation technologies.
    highlights:
      - "Led Android mobile app development for USAID to track commodities using barcode scanning and offline-first synchronization in low-connectivity environments; successfully field tested the pilot in Texas for shipments to Africa, providing end-to-end supply chain visibility."
      - "Developed an Android prototype for humanitarian deconfliction notifications, enabling GIS visualization of no-strike zones and encrypted submissions via blockchain-based audit trails; the proof of concept represented one of the first Ethereum transactions at MIT Lincoln Laboratory and received approximately $1M in follow-on funding."
      - "Built a counter–human-trafficking investigation tool for law enforcement to triage large volumes of digital evidence and reduce time to actionable investigative leads."
      - "Created Python-based data triage pipelines using Elasticsearch, Apache Tika, and Stanford CoreNLP to improve document indexing, semantic tagging, and content discovery across structured and unstructured datasets."
      - "Designed and implemented REST and GraphQL APIs backed by PostgreSQL (PostGIS) and TileDB to support scalable geospatial queries."
      - "Architected containerized DevOps infrastructure using Docker, Kubernetes, Pulumi, MinIO, and automated CI/CD pipelines to support reproducible deployments."
      - "Extended QGroundControl (C++) to integrate custom drone-tracking APIs and provided international technical support and training for deployed systems."

  - company: "Incompris LLC"
    location: "Independent"
    title: "Founder & Music Business Architect"
    dates: "2023 – Present"
    summary: >
      Founded a digital music label and automation studio integrating music production, AI-assisted workflows, and software tooling.
    highlights:
      - "Designed automated royalty and income tracking workflows using DistroKid, ASCAP, and SongTrust."
      - "Built AI-assisted mastering pipelines using Dockerized audio processing tools."
      - "Developed a cohesive digital presence integrating generative visuals and music branding."
      - "Automated business operations using ZenBusiness, Notion, and GitHub-based documentation systems."

  - company: "Taylor Networks"
    location: "Billerica, MA"
    title: "IT Support Technician"
    dates: "October 2017 – September 2018"
    summary: >
      Provided IT infrastructure and support services for small business clients.
    highlights:
      - "Configured Cisco ASA firewalls and implemented site-to-site VPNs."
      - "Maintained Windows Server environments and managed user permissions."
      - "Delivered on-site and remote support for network, hardware, and software issues."
      - "Performed HTML/CSS updates and website migrations."

education:
  - school: "Boston University"
    degree: "Master of Science in Software Development"
    dates: "April 2023"
    details:
      - "Focused on software engineering, full-stack development, and system architecture."
      - "Capstone projects included a WAV metadata parser in Python, an Android beatmaker app using JNI and C++, and a personalized music recommendation system."

  - school: "University of Massachusetts Lowell"
    degree: "Bachelor of Science in Computer Science (Minor in Mathematics)"
    dates: "January 2017"
    details:
      - "Coursework included Operating Systems, Data Structures, Algorithms, Computer Graphics, and Discrete Mathematics."
      - "Participated in independent blockchain research on decentralized networks."

interests: >
  AI-assisted music production, creative automation, open-source development, geospatial visualization,
  and building expressive human–machine interfaces.
EOF

# -----------------------------------------------------------------------------
# Engine build script: renders templates, builds PDF, produces site/<variant>/ outputs
# Uses dockerized tectonic for deterministic LaTeX builds on GitHub Actions.
# -----------------------------------------------------------------------------
echo "==> Writing engine/build.py"

cat <<'EOF' > "engine/build.py"
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "engine"
RESUMES_DIR = REPO_ROOT / "resumes"
SITE_DIR = REPO_ROOT / "site"

JINJA_ENV = Environment(
    loader=FileSystemLoader(str(REPO_ROOT)),
    autoescape=False,
)

def ensure_directory_exists(directory_path: Path) -> None:
    directory_path.mkdir(parents=True, exist_ok=True)

def render_template(template_path: str, output_path: Path, context: dict) -> None:
    template = JINJA_ENV.get_template(template_path)
    output_path.write_text(template.render(**context), encoding="utf-8")

def run_command(command: list[str], working_directory: Path | None = None) -> None:
    result = subprocess.run(
        command,
        cwd=str(working_directory) if working_directory else None,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")

def build_pdf_with_tectonic_docker(output_directory: Path, tex_filename: str = "resume.tex") -> Path:
    # Build inside docker for deterministic CI builds
    # Requires docker available (GitHub runners support this).
    pdf_filename = "resume.pdf"
    ensure_directory_exists(output_directory)

    command = [
        "docker",
        "run",
        "--rm",
        "--volume",
        f"{output_directory}:/work",
        "--workdir",
        "/work",
        "ghcr.io/tectonic-typesetting/tectonic:latest",
        "tectonic",
        "--print",
        "--synctex",
        "--keep-logs",
        tex_filename,
    ]
    run_command(command)
    pdf_path = output_directory / pdf_filename
    if not pdf_path.exists():
        raise RuntimeError("PDF build succeeded but resume.pdf was not found.")
    return pdf_path

def normalize_variant_name(variant_directory: Path) -> str:
    return variant_directory.name

def build_variant(variant_directory: Path) -> None:
    config_path = variant_directory / "resume.yaml"
    if not config_path.exists():
        return

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if "style" not in config:
        config["style"] = {"base": "default", "override": None}

    build_dir = variant_directory / "build"
    output_dir = variant_directory / "output"
    ensure_directory_exists(build_dir)
    ensure_directory_exists(output_dir)

    # Render LaTeX sections
    ensure_directory_exists(build_dir / "engine/latex/sections")
    ensure_directory_exists(build_dir / "engine/latex/styles")
    ensure_directory_exists(build_dir / "engine/html")

    # Copy engine into build dir (so LaTeX can \usepackage{engine/...})
    shutil.copytree(ENGINE_DIR, build_dir / "engine", dirs_exist_ok=True)

    context = {"config": config}

    render_template("engine/latex/resume.tex.j2", build_dir / "resume.tex", context)
    render_template("engine/latex/sections/header.tex.j2", build_dir / "engine/latex/sections/header.tex", context)
    render_template("engine/latex/sections/mission.tex.j2", build_dir / "engine/latex/sections/mission.tex", context)
    render_template("engine/latex/sections/experience.tex.j2", build_dir / "engine/latex/sections/experience.tex", context)
    render_template("engine/latex/sections/education.tex.j2", build_dir / "engine/latex/sections/education.tex", context)
    render_template("engine/latex/sections/interests.tex.j2", build_dir / "engine/latex/sections/interests.tex", context)

    # Render HTML
    rendered_html_path = output_dir / "resume.html"
    render_template("engine/html/resume.html.j2", rendered_html_path, context)

    # Render Markdown (simple canonical output)
    rendered_md_path = output_dir / "resume.md"
    rendered_md_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Build PDF from LaTeX using tectonic docker
    pdf_path = build_pdf_with_tectonic_docker(build_dir, "resume.tex")
    shutil.copy2(pdf_path, output_dir / "resume.pdf")

    # Publish to site/<variant>/
    variant_name = normalize_variant_name(variant_directory)
    variant_site_dir = SITE_DIR / variant_name
    ensure_directory_exists(variant_site_dir)

    shutil.copy2(output_dir / "resume.pdf", variant_site_dir / "resume.pdf")
    shutil.copy2(output_dir / "resume.html", variant_site_dir / "index.html")

def write_site_index(variant_names: list[str]) -> None:
    ensure_directory_exists(SITE_DIR)
    links = "\n".join([f'<li><a href="{name}/">{name}</a></li>' for name in sorted(variant_names)])

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Resume Variants</title>
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; max-width: 800px; margin: 0 auto; padding: 48px; color: #111; }}
    h1 {{ margin-bottom: 8px; }}
    ul {{ margin-top: 12px; }}
    a {{ color: #004080; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Resume Variants</h1>
  <p>Select a resume variant:</p>
  <ul>
    {links}
  </ul>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")

def main() -> None:
    ensure_directory_exists(SITE_DIR)
    variant_names: list[str] = []

    for variant_dir in RESUMES_DIR.iterdir():
      if variant_dir.is_dir() and (variant_dir / "resume.yaml").exists():
          build_variant(variant_dir)
          variant_names.append(variant_dir.name)

    write_site_index(variant_names)

if __name__ == "__main__":
    main()
EOF

# -----------------------------------------------------------------------------
# GitHub Actions workflow: Build + Deploy GitHub Pages (Actions-based)
# Produces URLs like:
#   https://szmyty.github.io/resume/
#   https://szmyty.github.io/resume/career_center/
# -----------------------------------------------------------------------------
echo "==> Writing GitHub Actions workflow: .github/workflows/build-and-deploy-pages.yml"

cat <<'EOF' > ".github/workflows/build-and-deploy-pages.yml"
name: Build and Deploy Resumes to GitHub Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: "read"
  pages: "write"
  id-token: "write"

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: "ubuntu-latest"
    steps:
      - name: "Checkout"
        uses: "actions/checkout@v4"

      - name: "Set up Python"
        uses: "actions/setup-python@v5"
        with:
          python-version: "3.12"

      - name: "Install Python dependencies"
        run: |
          python -m pip install --upgrade pip
          python -m pip install --requirement "requirements.txt"

      - name: "Build resume site"
        run: |
          python "engine/build.py"

      - name: "Configure Pages"
        uses: "actions/configure-pages@v5"

      - name: "Upload Pages artifact"
        uses: "actions/upload-pages-artifact@v3"
        with:
          path: "site"

  deploy:
    needs: "build"
    runs-on: "ubuntu-latest"
    environment:
      name: "github-pages"
      url: "${{ steps.deployment.outputs.page_url }}"
    steps:
      - name: "Deploy to GitHub Pages"
        id: "deployment"
        uses: "actions/deploy-pages@v4"
EOF

# -----------------------------------------------------------------------------
# Root README.md (simple instructions)
# -----------------------------------------------------------------------------
echo "==> Writing README.md"

cat <<'EOF' > "README.md"
# Resume
EOF
