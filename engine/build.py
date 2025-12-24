from __future__ import annotations

import os
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
    try:
        template = JINJA_ENV.get_template(template_path)
        rendered_content = template.render(**context)
        output_path.write_text(rendered_content, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(
            f"Failed to render template '{template_path}' → '{output_path}': {e}"
        ) from e

def run_command(
    command: list[str],
    working_directory: Path | None = None,
    env: dict | None = None,
) -> None:
    result = subprocess.run(
        command,
        cwd=str(working_directory) if working_directory else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}"
        )

def build_pdf_with_tectonic(build_dir: Path, tex_filename: str = "resume.tex") -> Path:
    """
    Deterministic Tectonic PDF build suitable for CI.

    - Uses explicit bundle
    - Uses environment-based bundle cache
    - Uses absolute path to input .tex file (avoids CI cwd issues)
    """
    pdf_filename = "resume.pdf"
    bundle_cache = os.environ.get(
        "TECTONIC_BUNDLE_CACHE",
        os.path.expanduser("~/.cache/Tectonic"),
    )

    ensure_directory_exists(Path(bundle_cache))

    tex_path = (build_dir / tex_filename).resolve()

    if not tex_path.exists():
        raise RuntimeError(f"Tectonic input file not found: {tex_path}")

    run_command(
        [
            "tectonic",
            "--print",
            "--synctex",
            "--keep-logs",
            "--bundle",
            "latest",
            str(tex_path),
        ],
        working_directory=build_dir,
        env={
            **os.environ,
            "TEXINPUTS": f"{build_dir}/engine/styles:",
            "TECTONIC_BUNDLE_CACHE": bundle_cache,
        },
    )

    pdf_path = build_dir / pdf_filename
    if not pdf_path.exists():
        raise RuntimeError("PDF build succeeded but resume.pdf was not found.")

    return pdf_path


def normalize_variant_name(variant_directory: Path) -> str:
    return variant_directory.name

def build_variant(variant_directory: Path) -> None:
    variant_name = normalize_variant_name(variant_directory)

    print("\n" + "=" * 60)
    print(f"Building variant: {variant_name}")
    print("=" * 60)

    config_path = variant_directory / "resume.yaml"
    if not config_path.exists():
        print(f"⚠ Skipping {variant_name}: no resume.yaml found")
        return

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config.setdefault("style", {"base": "default", "override": None})

        build_dir = variant_directory / "build"
        output_dir = variant_directory / "output"

        ensure_directory_exists(build_dir)
        ensure_directory_exists(output_dir)

        # Copy engine into build dir
        shutil.copytree(ENGINE_DIR, build_dir / "engine", dirs_exist_ok=True)

        context = {"config": config}

        print("  → Rendering templates...")
        render_template("engine/latex/resume.tex.j2", build_dir / "resume.tex", context)
        render_template("engine/latex/sections/header.tex.j2", build_dir / "engine/latex/sections/header.tex", context)
        render_template("engine/latex/sections/mission.tex.j2", build_dir / "engine/latex/sections/mission.tex", context)
        render_template("engine/latex/sections/experience.tex.j2", build_dir / "engine/latex/sections/experience.tex", context)
        render_template("engine/latex/sections/education.tex.j2", build_dir / "engine/latex/sections/education.tex", context)
        render_template("engine/latex/sections/interests.tex.j2", build_dir / "engine/latex/sections/interests.tex", context)

        print("  → Rendering HTML...")
        render_template("engine/html/resume.html.j2", output_dir / "resume.html", context)

        print("  → Rendering Markdown...")
        (output_dir / "resume.md").write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("  → Building PDF with Tectonic...")
        pdf_path = build_pdf_with_tectonic(build_dir, "resume.tex")
        shutil.copy2(pdf_path, output_dir / "resume.pdf")

        print(f"  → Publishing to site/{variant_name}/...")
        variant_site_dir = SITE_DIR / variant_name
        ensure_directory_exists(variant_site_dir)
        shutil.copy2(output_dir / "resume.pdf", variant_site_dir / "resume.pdf")
        shutil.copy2(output_dir / "resume.html", variant_site_dir / "index.html")

        print(f"  ✓ Variant '{variant_name}' built successfully")

    except Exception as e:
        print(f"\n✗ ERROR building variant '{variant_name}':")
        print(f"  {type(e).__name__}: {e}")
        raise

def write_site_index(variant_names: list[str]) -> None:
    ensure_directory_exists(SITE_DIR)

    links = "\n".join(
        [f'<li><a href="{name}/">{name}</a></li>' for name in sorted(variant_names)]
    )

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
    print("\n" + "=" * 60)
    print("Starting resume build pipeline")
    print("=" * 60)

    ensure_directory_exists(SITE_DIR)
    variant_names: list[str] = []

    for variant_dir in RESUMES_DIR.iterdir():
        if variant_dir.is_dir() and (variant_dir / "resume.yaml").exists():
            build_variant(variant_dir)
            variant_names.append(variant_dir.name)

    print("\n" + "=" * 60)
    print("Generating site index...")
    print("=" * 60)

    write_site_index(variant_names)

    print(f"\n✓ Build complete! Generated {len(variant_names)} variant(s):")
    for name in sorted(variant_names):
        print(f"  - {name}")
    print()

if __name__ == "__main__":
    main()
