#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Pure-Python tests for facts, privacy, profiles, and build resolution."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import build  # noqa: E402
import career  # noqa: E402
import quality_gates  # noqa: E402


@pytest.fixture()
def documents() -> dict[str, build.DocumentManifest]:
    return build.load_document_manifests()


@pytest.fixture()
def profiles() -> dict[str, build.ProfileConfig]:
    return build.load_profiles()


@pytest.fixture()
def resume_document(
    documents: dict[str, build.DocumentManifest],
) -> build.DocumentManifest:
    return documents["resume"]


@pytest.fixture()
def general_profile(
    profiles: dict[str, build.ProfileConfig],
) -> build.ProfileConfig:
    return profiles["general"]


@pytest.fixture()
def synthetic_contact() -> dict[str, str]:
    return {
        "email": "applicant@example.invalid",
        "phone": "+1 555-010-0200",
        "location": "Application City, MA",
    }


def test_canonical_ledger_loads_with_verified_sources() -> None:
    ledger = career.load_ledger()
    assert ledger["canonical_lane"] == "platform-devex"
    assert ledger["roles"]["mit-lincoln-laboratory"]["start"] == "2019-04"
    assert ledger["roles"]["mit-lincoln-laboratory"]["end"] == "2025-08"
    assert ledger["roles"]["incompris"]["start"] == "2023-01"
    assert ledger["roles"]["incompris"]["overlap_qualifier"] is None
    assert all(
        claim["provenance"]["status"] == "verified"
        for claim in ledger["claims"].values()
    )


def test_locked_fact_gate_passes() -> None:
    assert quality_gates.validate_facts() == 0


def test_reflector_uses_independent_concept_doi() -> None:
    artifact = career.load_ledger()["research_artifacts"]["reflector"]
    assert artifact["status"] == "Independent DOI-backed research artifact"
    assert artifact["concept_doi"] == "10.5281/zenodo.20477044"
    assert artifact["concept_url"].endswith(artifact["concept_doi"])


def test_metric_wording_keeps_bounded_qualifiers() -> None:
    claim = career.load_ledger()["claims"]["mit-deconfliction-funding"]
    for projection in ("public_text", "application_text"):
        normalized = claim[projection].casefold()
        assert "contributed to" in normalized
        assert "approximately" in normalized


def test_public_contact_policy_contains_no_private_values() -> None:
    ledger = career.load_ledger()
    policy = ledger["privacy"]["public"]
    assert policy["allowed_contact_fields"] == ["public_location", "public_links"]
    assert set(policy["forbidden_contact_types"]) == {
        "email",
        "phone",
        "precise_city",
    }
    assert not career.find_public_contact_leaks(json.dumps(ledger))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("applicant@example.invalid", ["email"]),
        ("+1 555-010-0200", ["phone"]),
        ("Greater Boston, MA", []),
        ("10.5281/zenodo.20477044", []),
        ("0009-0008-5291-9795", []),
    ],
)
def test_public_contact_leak_detection(value: str, expected: list[str]) -> None:
    assert career.find_public_contact_leaks(value) == expected


def test_application_contact_overlay_is_allowlisted(tmp_path: Path) -> None:
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(
        json.dumps(
            {
                "email": "applicant@example.invalid",
                "phone": "+1 555-010-0200",
                "location": "Application City, MA",
            }
        ),
        encoding="utf-8",
    )
    contact = career.load_application_contact(contact_path)
    assert set(contact) == {"email", "phone", "location"}


def test_application_contact_overlay_rejects_unknown_fields(tmp_path: Path) -> None:
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(
        json.dumps({"email": "applicant@example.invalid", "employer": "Example"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unsupported application contact field"):
        career.load_application_contact(contact_path)


def test_application_contact_overlay_requires_email_or_phone(tmp_path: Path) -> None:
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(
        json.dumps({"location": "Application City, MA"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="approved email or phone"):
        career.load_application_contact(contact_path)


def test_document_manifests_keep_resume_and_cv_distinct(
    documents: dict[str, build.DocumentManifest],
) -> None:
    assert set(documents) == {"resume", "cv"}
    assert set(documents["resume"].section_pool).issubset(
        documents["cv"].section_pool
    )
    assert "projects" not in documents["resume"].section_pool
    assert "projects" in documents["cv"].section_pool


def test_exact_application_role_profile_set(
    profiles: dict[str, build.ProfileConfig],
) -> None:
    assert set(profiles) == {
        "general",
        "platform",
        "research",
        "mobile-geospatial",
    }
    assert profiles["general"].output_label == "Platform-DevEx"
    assert profiles["research"].output_label == "Research-AI-Systems"
    assert profiles["mobile-geospatial"].output_label == "Mobile-Geospatial"


def test_every_profile_uses_evidenced_claims_and_skill_groups(
    profiles: dict[str, build.ProfileConfig],
) -> None:
    ledger = career.load_ledger()
    for profile in profiles.values():
        effective_profile = "platform" if profile.profile == "general" else profile.profile
        for claim_id in profile.claim_ids:
            assert effective_profile in ledger["claims"][claim_id]["profiles"]
        for group_id in profile.skill_group_ids:
            evidence = set(ledger["skill_groups"][group_id]["evidence"])
            assert evidence.intersection(profile.claim_ids)


def test_public_baseline_resolution_has_intentional_name(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    assert config.audience == "public"
    assert config.output_basename == "Alan-Szmyt-Resume"
    assert config.page_size == "letter"
    assert config.contact == {}


def test_application_role_resolution_has_intentional_name(
    resume_document: build.DocumentManifest,
    profiles: dict[str, build.ProfileConfig],
    synthetic_contact: dict[str, str],
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=profiles["research"],
        target=None,
        page_size_override=None,
        audience="application",
        contact=synthetic_contact,
    )
    assert config.output_basename == "Alan-Szmyt-Resume-Research-AI-Systems"
    assert config.audience == "application"
    assert config.contact == synthetic_contact


def test_cv_filename_preserves_uppercase_initialism(
    documents: dict[str, build.DocumentManifest],
    profiles: dict[str, build.ProfileConfig],
) -> None:
    config = build.resolve_config(
        document=documents["cv"],
        profile=profiles["research"],
        target=None,
        page_size_override=None,
    )
    assert config.output_basename == "Alan-Szmyt-CV-Research-AI-Systems-Public"


def test_application_resolution_requires_contact(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    with pytest.raises(ValueError, match="require approved contact"):
        build.resolve_config(
            document=resume_document,
            profile=general_profile,
            target=None,
            page_size_override=None,
            audience="application",
        )


def test_invalid_audience_is_rejected(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    with pytest.raises(ValueError, match="Unsupported audience"):
        build.resolve_config(
            document=resume_document,
            profile=general_profile,
            target=None,
            page_size_override=None,
            audience="internal",
        )


def test_target_and_cli_precedence(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    target = build.load_target(REPOSITORY_ROOT / "targets" / "example.yaml")
    target_config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=target,
        page_size_override="a4",
    )
    assert target_config.page_size == "a4"
    assert target_config.section_order == target.section_order
    assert target_config.output_basename.endswith("-example")


def test_target_declared_profile_mismatch_is_rejected(
    resume_document: build.DocumentManifest,
    profiles: dict[str, build.ProfileConfig],
) -> None:
    target = build.load_target(REPOSITORY_ROOT / "targets" / "example.yaml")
    with pytest.raises(ValueError, match="requires profile 'general'"):
        build.resolve_config(
            document=resume_document,
            profile=profiles["research"],
            target=target,
            page_size_override=None,
        )


def test_unknown_section_is_rejected(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    invalid_profile = replace(
        general_profile,
        section_order=(*general_profile.section_order, "unknown"),
    )
    with pytest.raises(ValueError, match="not in pool"):
        build.resolve_config(
            document=resume_document,
            profile=invalid_profile,
            target=None,
            page_size_override=None,
        )


def test_duplicate_section_is_rejected(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    invalid_profile = replace(
        general_profile,
        section_order=(*general_profile.section_order, "header"),
    )
    with pytest.raises(ValueError, match="Duplicate section"):
        build.resolve_config(
            document=resume_document,
            profile=invalid_profile,
            target=None,
            page_size_override=None,
        )


def test_public_render_uses_sanitized_projection(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    rendered = build.render_document(config)
    assert "Greater Boston, MA" in rendered
    assert "humanitarian commodity monitoring" in rendered
    assert "USAID" not in rendered
    assert "mailto:" not in rendered
    assert "tel:" not in rendered
    assert not career.find_public_contact_leaks(rendered)


def test_general_baseline_keeps_independent_role_together(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    rendered = build.render_document(config)
    assert "Founder \\& Systems Architect (continued)" not in rendered
    assert rendered.index("\\item Designed AI-assisted workflow architectures") < (
        rendered.index("\\newpage\n\\setlength{\\parskip}{0.9em}")
    )
    assert rendered.index("\\newpage\n\\setlength{\\parskip}{0.9em}") < (
        rendered.index("\\section{Research Artifact}")
    )


def test_application_render_uses_approved_contact_and_claim_projection(
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
    synthetic_contact: dict[str, str],
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=None,
        page_size_override=None,
        audience="application",
        contact=synthetic_contact,
    )
    rendered = build.render_document(config)
    assert "applicant@example.invalid" in rendered
    assert "+1 555-010-0200" in rendered
    assert "Application City, MA" in rendered
    assert "USAID" in rendered


def test_build_publishes_latexmk_generated_suffix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    resume_document: build.DocumentManifest,
    general_profile: build.ProfileConfig,
) -> None:
    config = build.resolve_config(
        document=resume_document,
        profile=general_profile,
        target=None,
        page_size_override=None,
    )
    repository_root = tmp_path / "repository"
    out_dir = repository_root / ".cache" / "out"
    aux_dir = repository_root / ".cache" / "aux"
    outputs_dir = repository_root / "outputs"
    dist_dir = repository_root / "dist"
    for directory in (repository_root, out_dir, aux_dir, outputs_dir, dist_dir):
        directory.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(build, "REPOSITORY_ROOT", repository_root)
    monkeypatch.setattr(build, "OUT_DIR", out_dir)
    monkeypatch.setattr(build, "AUX_DIR", aux_dir)
    monkeypatch.setattr(build, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(build, "DIST_DIR", dist_dir)
    monkeypatch.setattr(build, "render_document", lambda _: "generated source")

    def fake_run(*_: object, **__: object) -> SimpleNamespace:
        expected = out_dir / f"{config.output_basename}.generated.pdf"
        expected.write_bytes(b"%PDF-test")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(build.subprocess, "run", fake_run)
    result = build.build_document(config)
    assert result.name == "Alan-Szmyt-Resume.pdf"
    assert result.read_bytes() == b"%PDF-test"
    assert (outputs_dir / "Alan-Szmyt-Resume.pdf").exists()


def test_latex_escape_preserves_safe_text_and_escapes_specials() -> None:
    assert career.latex_escape("R&D 100%") == r"R\&D 100\%"


def test_nonexistent_target_fails() -> None:
    with pytest.raises(FileNotFoundError):
        build.load_target(REPOSITORY_ROOT / "targets" / "does-not-exist.yaml")
