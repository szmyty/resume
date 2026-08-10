#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Tests for build configuration resolution, validation, and overlay precedence.

These are pure-Python tests that do not require LaTeX or any generated PDFs.
They validate the configuration layer: document manifests, profile loading,
target overlay precedence, section validation, and error handling.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import build without installation.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build  # noqa: E402  (import after sys.path update)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def documents() -> dict[str, build.DocumentManifest]:
    return build.load_document_manifests()


@pytest.fixture()
def profiles() -> dict[str, build.ProfileConfig]:
    return build.load_profiles()


@pytest.fixture()
def resume_doc(documents: dict[str, build.DocumentManifest]) -> build.DocumentManifest:
    return documents["resume"]


@pytest.fixture()
def cv_doc(documents: dict[str, build.DocumentManifest]) -> build.DocumentManifest:
    return documents["cv"]


@pytest.fixture()
def general_profile(profiles: dict[str, build.ProfileConfig]) -> build.ProfileConfig:
    return profiles["general"]


@pytest.fixture()
def research_profile(profiles: dict[str, build.ProfileConfig]) -> build.ProfileConfig:
    return profiles["research"]


# ---------------------------------------------------------------------------
# Document manifest loading
# ---------------------------------------------------------------------------


def test_load_document_manifests_returns_resume_and_cv(
    documents: dict[str, build.DocumentManifest],
) -> None:
    assert "resume" in documents
    assert "cv" in documents


def test_resume_document_manifest_fields(resume_doc: build.DocumentManifest) -> None:
    assert resume_doc.document_type == "resume"
    assert resume_doc.default_template == "resume"
    assert resume_doc.default_page_size == "letter"
    assert "header" in resume_doc.section_pool
    assert "experience" in resume_doc.section_pool
    assert "projects" not in resume_doc.section_pool  # résumé pool is smaller


def test_cv_document_manifest_fields(cv_doc: build.DocumentManifest) -> None:
    assert cv_doc.document_type == "cv"
    assert cv_doc.default_template == "cv"
    assert "projects" in cv_doc.section_pool
    assert "talks" in cv_doc.section_pool
    assert "awards" in cv_doc.section_pool
    assert "service" in cv_doc.section_pool


def test_cv_section_pool_is_superset_of_resume(
    resume_doc: build.DocumentManifest,
    cv_doc: build.DocumentManifest,
) -> None:
    resume_pool = set(resume_doc.section_pool)
    cv_pool = set(cv_doc.section_pool)
    assert resume_pool.issubset(cv_pool)


# ---------------------------------------------------------------------------
# Profile loading
# ---------------------------------------------------------------------------


def test_load_all_four_profiles(profiles: dict[str, build.ProfileConfig]) -> None:
    assert set(profiles) == {"general", "platform", "research", "ai-infra"}


def test_general_profile_fields(general_profile: build.ProfileConfig) -> None:
    assert general_profile.profile == "general"
    assert "header" in general_profile.included_sections
    assert "experience" in general_profile.included_sections
    assert len(general_profile.keyword_emphasis) >= 1


def test_profile_section_order_contains_included_sections(
    general_profile: build.ProfileConfig,
) -> None:
    included = set(general_profile.included_sections)
    ordered = set(general_profile.section_order)
    assert included.issubset(ordered)


def test_research_profile_includes_publications(research_profile: build.ProfileConfig) -> None:
    assert "publications" in research_profile.included_sections


# ---------------------------------------------------------------------------
# Config resolution — defaults
# ---------------------------------------------------------------------------


def test_resolve_config_defaults(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    assert config.document_type == "resume"
    assert config.profile == "general"
    assert config.page_size == "letter"
    assert config.template == "resume"
    assert config.target is None
    assert config.output_basename == "alan-szmyt-resume-general"


def test_resolve_config_cv_defaults(
    cv_doc: build.DocumentManifest,
    research_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=cv_doc,
        profile=research_profile,
        target=None,
        page_size_override=None,
    )
    assert config.document_type == "cv"
    assert config.profile == "research"
    assert config.output_basename == "alan-szmyt-cv-research"


# ---------------------------------------------------------------------------
# Config resolution — page-size override
# ---------------------------------------------------------------------------


def test_cli_page_size_override(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=None,
        page_size_override="a4",
    )
    assert config.page_size == "a4"


# ---------------------------------------------------------------------------
# Target overlay
# ---------------------------------------------------------------------------


@pytest.fixture()
def example_target() -> build.TargetConfig:
    return build.load_target(REPO_ROOT / "targets" / "example.yaml")


def test_load_example_target(example_target: build.TargetConfig) -> None:
    assert example_target.target == "example"
    assert example_target.document_type == "resume"
    assert example_target.profile == "general"
    assert example_target.page_size == "letter"
    assert example_target.section_order is not None


def test_target_section_order_overrides_profile(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
    example_target: build.TargetConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=example_target,
        page_size_override=None,
    )
    # Example target puts skills before experience.
    skill_idx = list(config.section_order).index("skills")
    exp_idx = list(config.section_order).index("experience")
    assert skill_idx < exp_idx


def test_target_page_size_overrides_document_default(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    target = build.TargetConfig(
        target="test",
        description="test",
        page_size="a4",
    )
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=target,
        page_size_override=None,
    )
    assert config.page_size == "a4"


def test_cli_overrides_target_page_size(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    target = build.TargetConfig(
        target="test",
        description="test",
        page_size="a4",
    )
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=target,
        page_size_override="letter",
    )
    assert config.page_size == "letter"


def test_target_output_basename_in_config(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
    example_target: build.TargetConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=example_target,
        page_size_override=None,
    )
    # Should include target in basename.
    assert "example" in config.output_basename
    assert config.target == "example"


# ---------------------------------------------------------------------------
# Deterministic output naming
# ---------------------------------------------------------------------------


def test_output_basename_format_no_target(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    assert config.output_basename == "alan-szmyt-resume-general"


def test_output_basename_format_with_target(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
    example_target: build.TargetConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=example_target,
        page_size_override=None,
    )
    assert config.output_basename == "alan-szmyt-resume-general-example"


# ---------------------------------------------------------------------------
# Section ordering and inclusion
# ---------------------------------------------------------------------------


def test_included_sections_subset_of_section_order(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_doc,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    included = set(config.included_sections)
    ordered = set(config.section_order)
    assert included.issubset(ordered)


def test_optional_section_omitted_when_not_in_profile(
    cv_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    """'projects' is in the CV pool but not in general profile's included_sections."""
    config = build.resolve_config(
        document=cv_doc,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    assert "projects" not in config.included_sections
    assert "talks" not in config.included_sections


# ---------------------------------------------------------------------------
# Error handling — unknown / invalid inputs
# ---------------------------------------------------------------------------


def test_unknown_section_in_section_order_fails(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    bad_profile = build.ProfileConfig(
        profile="general",
        name="General",
        section_order=("header", "summary", "nonexistent"),
        included_sections=("header", "summary"),
        keyword_emphasis=("test",),
    )
    with pytest.raises(ValueError, match="not in pool"):
        build.resolve_config(
            document=resume_doc,
            profile=bad_profile,
            target=None,
            page_size_override=None,
        )


def test_included_section_missing_from_order_fails(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    bad_profile = build.ProfileConfig(
        profile="general",
        name="General",
        section_order=("header",),
        included_sections=("header", "summary"),  # summary not in order
        keyword_emphasis=("test",),
    )
    with pytest.raises(ValueError, match="missing from section_order"):
        build.resolve_config(
            document=resume_doc,
            profile=bad_profile,
            target=None,
            page_size_override=None,
        )


def test_duplicate_section_in_order_fails(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    bad_profile = build.ProfileConfig(
        profile="general",
        name="General",
        section_order=("header", "summary", "header"),  # duplicate
        included_sections=("header", "summary"),
        keyword_emphasis=("test",),
    )
    with pytest.raises(ValueError, match="Duplicate section"):
        build.resolve_config(
            document=resume_doc,
            profile=bad_profile,
            target=None,
            page_size_override=None,
        )


def test_cv_section_in_resume_pool_fails(
    resume_doc: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    """'projects' is a CV section; using it in a résumé build should fail."""
    bad_profile = build.ProfileConfig(
        profile="general",
        name="General",
        section_order=("header", "summary", "projects"),
        included_sections=("header", "summary", "projects"),
        keyword_emphasis=("test",),
    )
    with pytest.raises(ValueError, match="not in pool"):
        build.resolve_config(
            document=resume_doc,
            profile=bad_profile,
            target=None,
            page_size_override=None,
        )


def test_nonexistent_target_file_fails() -> None:
    with pytest.raises(FileNotFoundError):
        build.load_target(REPO_ROOT / "targets" / "nonexistent.yaml")


def test_unknown_document_type_in_manifest_fails(tmp_path: Path) -> None:
    bad_manifest = tmp_path / "badtype.yaml"
    bad_manifest.write_text(
        "document_type: badtype\n"
        "default_template: resume\n"
        "default_page_size: letter\n"
        "section_pool:\n  - header\n"
        "default_section_order:\n  - header\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unsupported document_type"):
        build.load_document_manifest(bad_manifest)


def test_unknown_page_size_in_manifest_fails(tmp_path: Path) -> None:
    bad_manifest = tmp_path / "resume.yaml"
    bad_manifest.write_text(
        "document_type: resume\n"
        "default_template: resume\n"
        "default_page_size: legal\n"
        "section_pool:\n  - header\n"
        "default_section_order:\n  - header\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unsupported page size"):
        build.load_document_manifest(bad_manifest)


# ---------------------------------------------------------------------------
# Section pool constants
# ---------------------------------------------------------------------------


def test_resume_sections_constant() -> None:
    assert build.RESUME_SECTIONS == frozenset({
        "header", "summary", "experience", "publications", "education", "skills"
    })


def test_cv_sections_is_superset_of_resume_sections() -> None:
    assert build.RESUME_SECTIONS.issubset(build.CV_SECTIONS)
    assert {"projects", "talks", "awards", "service"}.issubset(build.CV_SECTIONS)


def test_document_section_pools_mapping() -> None:
    assert "resume" in build.DOCUMENT_SECTION_POOLS
    assert "cv" in build.DOCUMENT_SECTION_POOLS
    assert build.DOCUMENT_SECTION_POOLS["resume"] == build.RESUME_SECTIONS
    assert build.DOCUMENT_SECTION_POOLS["cv"] == build.CV_SECTIONS
