from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_INDEX = REPO_ROOT / "site" / "index.html"
SITE_STYLES = REPO_ROOT / "site" / "styles.css"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "build-resume.yml"


def test_public_site_is_static_and_links_canonical_resume() -> None:
    index = SITE_INDEX.read_text(encoding="utf-8")

    assert 'href="./resume.pdf"' in index
    assert "https://szmyty.vercel.app" in index
    assert "https://github.com/szmyty" in index
    assert "https://orcid.org/0009-0008-5291-9795" in index
    assert "https://github.com/szmyty/resume" in index
    assert "<script" not in index.lower()


def test_public_site_contains_no_application_contact_surface() -> None:
    index = SITE_INDEX.read_text(encoding="utf-8").lower()

    assert "mailto:" not in index
    assert "tel:" not in index
    assert "applicant@example.invalid" not in index
    assert "+1 555" not in index
    assert "application city" not in index


def test_public_site_has_responsive_light_dark_styles() -> None:
    styles = SITE_STYLES.read_text(encoding="utf-8")

    assert "prefers-color-scheme: dark" in styles
    assert "@media (max-width: 760px)" in styles
    assert "prefers-reduced-motion: reduce" in styles


def test_pages_deploys_only_after_validated_build() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "actions/configure-pages@v5" in workflow
    assert "actions/upload-pages-artifact@v3" in workflow
    assert "actions/deploy-pages@v4" in workflow
    assert "needs: build" in workflow
    assert "site-dist/resume.pdf" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
