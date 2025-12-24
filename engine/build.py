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
