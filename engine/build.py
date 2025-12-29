from __future__ import annotations

import os
import json
import shutil
import subprocess
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, TemplateNotFound

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "engine"
RESUMES_DIR = REPO_ROOT / "resumes"
SITE_DIR = REPO_ROOT / "site"

# Required fields for resume configuration validation
REQUIRED_CONFIG_FIELDS = ["name", "contact", "experience", "education"]

JINJA_ENV = Environment(
    loader=FileSystemLoader(str(REPO_ROOT)),
    autoescape=False,
)

def ensure_directory_exists(directory_path: Path) -> None:
    directory_path.mkdir(parents=True, exist_ok=True)

def render_template(template_path: str, output_path: Path, context: dict, variant_name: str = "") -> None:
    """
    Render a Jinja2 template to an output file.
    
    Raises detailed error messages for template syntax errors and other rendering issues.
    """
    try:
        template = JINJA_ENV.get_template(template_path)
        rendered_content = template.render(**context)
        output_path.write_text(rendered_content, encoding="utf-8")
    except TemplateSyntaxError as e:
        error_msg = (
            f"Jinja2 template syntax error in '{template_path}'"
        )
        if variant_name:
            error_msg += f" (variant: {variant_name})"
        error_msg += f"\n  Line {e.lineno}: {e.message}"
        if e.filename:
            error_msg += f"\n  File: {e.filename}"
        raise RuntimeError(error_msg) from e
    except TemplateNotFound as e:
        error_msg = f"Template file not found: '{template_path}'"
        if variant_name:
            error_msg += f" (variant: {variant_name})"
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Failed to render template '{template_path}' → '{output_path}'"
        if variant_name:
            error_msg += f" (variant: {variant_name})"
        error_msg += f"\n  {type(e).__name__}: {e}"
        raise RuntimeError(error_msg) from e

def run_command(
    command: list[str],
    working_directory: Path | None = None,
    env: dict | None = None,
    error_context: str = "",
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
        logs = []

        if working_directory:
            for log_name in ("resume.log", "texput.log"):
                log_path = Path(working_directory) / log_name
                if log_path.exists():
                    logs.append(f"\n===== {log_name} =====\n{log_path.read_text()}")

        error_msg = "Command failed"
        if error_context:
            error_msg = error_context

        error_msg += f"\nCommand: {' '.join(command)}"
        error_msg += f"\nExit code: {result.returncode}"
        error_msg += f"\nOutput:\n{result.stdout}"

        if logs:
            error_msg += "\n\nLaTeX logs:\n" + "\n".join(logs)

        raise RuntimeError(error_msg)

def resolve_tectonic_executable() -> str:
    """
    Resolve the Tectonic executable using shutil.which().
    
    Returns:
        Absolute path to the Tectonic executable.
        
    Raises:
        RuntimeError: If Tectonic is not found on PATH.
    """
    tectonic_path = shutil.which("tectonic")
    if tectonic_path is None:
        raise RuntimeError(
            "Tectonic executable not found on PATH.\n"
            "  Please install Tectonic: https://tectonic-typesetting.github.io/install.html\n"
            "  Or ensure it is available in your PATH environment variable."
        )
    return tectonic_path

def build_pdf_with_tectonic(build_dir: Path, tex_filename: str = "resume.tex", variant_name: str = "") -> Path:
    r"""
    Build PDF from LaTeX source using Tectonic.

    IMPORTANT:
    - Tectonic must be invoked with a RELATIVE input path.
    - working_directory must be the directory containing the .tex file.
    - Style files (.sty) are copied to build_dir for direct resolution.
    - TEXINPUTS includes engine subdirectories for \input{engine/...} statements.
    """
    # Resolve Tectonic executable and fail fast if not found
    tectonic_executable = resolve_tectonic_executable()
    
    pdf_filename = "resume.pdf"
    bundle_cache = os.environ.get(
        "TECTONIC_BUNDLE_CACHE",
        os.path.expanduser("~/.cache/Tectonic"),
    )

    ensure_directory_exists(Path(bundle_cache))

    tex_path = build_dir / tex_filename
    if not tex_path.exists():
        raise RuntimeError(
            f"LaTeX source file not found: {tex_path}"
            + (f" (variant: {variant_name})" if variant_name else "")
        )

    error_context = f"LaTeX compilation failed for '{tex_filename}'"
    if variant_name:
        error_context += f" (variant: {variant_name})"

    run_command(
        [
            tectonic_executable,
            "--print",
            "--synctex",
            "--keep-logs",
            tex_filename,  # ← RELATIVE PATH
        ],
        working_directory=build_dir,
        env={
            **os.environ,
            # Current directory includes style files and serves as base for \input{engine/...}
            # The '::' suffix preserves default TeX search paths
            "TEXINPUTS": ".::",
            "TECTONIC_BUNDLE_CACHE": bundle_cache,
        },
        error_context=error_context,
    )

    pdf_path = build_dir / pdf_filename
    if not pdf_path.exists():
        raise RuntimeError(
            "PDF build succeeded but resume.pdf was not found"
            + (f" (variant: {variant_name})" if variant_name else "")
        )

    return pdf_path

def normalize_variant_name(variant_directory: Path) -> str:
    return variant_directory.name

def validate_resume_config(config: dict, variant_name: str, config_path: Path) -> None:
    """
    Validate the resume configuration has required fields.
    
    Args:
        config: The loaded YAML configuration
        variant_name: Name of the variant being validated
        config_path: Path to the config file for error messages
    
    Raises:
        RuntimeError: If validation fails
    """
    missing_fields = [field for field in REQUIRED_CONFIG_FIELDS if field not in config]
    
    if missing_fields:
        raise RuntimeError(
            f"Invalid resume configuration for variant '{variant_name}'\n"
            f"  Config file: {config_path}\n"
            f"  Missing required fields: {', '.join(missing_fields)}"
        )
    
    # Validate style configuration
    if "style" in config:
        style = config["style"]
        if not isinstance(style, dict):
            raise RuntimeError(
                f"Invalid style configuration for variant '{variant_name}'\n"
                f"  Config file: {config_path}\n"
                f"  'style' must be a dictionary"
            )
        
        style_base = style.get("base", "default")
        style_file = ENGINE_DIR / "styles" / f"{style_base}.sty"
        if not style_file.exists():
            available_styles = [f.stem for f in (ENGINE_DIR / "styles").glob("*.sty")]
            raise RuntimeError(
                f"Style file not found for variant '{variant_name}'\n"
                f"  Config file: {config_path}\n"
                f"  Requested style: '{style_base}'\n"
                f"  Available styles: {', '.join(sorted(available_styles))}"
            )

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
        # Load and validate configuration
        print(f"  → Loading configuration from {config_path.name}...")
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            raise RuntimeError(
                f"YAML parsing error in configuration for variant '{variant_name}'\n"
                f"  Config file: {config_path}\n"
                f"  Error: {e}"
            ) from e
        
        config.setdefault("style", {"base": "default", "override": None})

        print(f"  → Validating configuration...")
        validate_resume_config(config, variant_name, config_path)

        build_dir = variant_directory / "build"
        output_dir = variant_directory / "output"

        ensure_directory_exists(build_dir)
        ensure_directory_exists(output_dir)

        # Copy engine into build dir
        shutil.copytree(ENGINE_DIR, build_dir / "engine", dirs_exist_ok=True)

        # Copy style files to build root for LaTeX to find them
        # This ensures \usepackage{default} works without complex TEXINPUTS configuration
        styles_source = ENGINE_DIR / "styles"
        if not styles_source.exists():
            raise RuntimeError(
                f"Style directory not found: {styles_source}\n"
                f"This is a repository structure issue."
            )
        
        style_files = list(styles_source.glob("*.sty"))
        if not style_files:
            raise RuntimeError(
                f"No .sty files found in {styles_source}\n"
                f"This is a repository structure issue."
            )
        
        for style_file in style_files:
            shutil.copy2(style_file, build_dir / style_file.name)

        context = {"config": config}

        # Render Jinja templates
        print("  → Rendering Jinja templates...")
        print("     - resume.tex")
        render_template("engine/latex/resume.tex.j2", build_dir / "resume.tex", context, variant_name)
        print("     - header.tex")
        render_template("engine/latex/sections/header.tex.j2", build_dir / "engine/latex/sections/header.tex", context, variant_name)
        print("     - mission.tex")
        render_template("engine/latex/sections/mission.tex.j2", build_dir / "engine/latex/sections/mission.tex", context, variant_name)
        print("     - experience.tex")
        render_template("engine/latex/sections/experience.tex.j2", build_dir / "engine/latex/sections/experience.tex", context, variant_name)
        print("     - education.tex")
        render_template("engine/latex/sections/education.tex.j2", build_dir / "engine/latex/sections/education.tex", context, variant_name)
        print("     - interests.tex")
        render_template("engine/latex/sections/interests.tex.j2", build_dir / "engine/latex/sections/interests.tex", context, variant_name)

        print("  → Rendering HTML...")
        render_template("engine/html/resume.html.j2", output_dir / "resume.html", context, variant_name)

        print("  → Writing configuration as JSON...")
        (output_dir / "resume.md").write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("  → Compiling LaTeX to PDF with Tectonic...")
        pdf_path = build_pdf_with_tectonic(build_dir, "resume.tex", variant_name)
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
