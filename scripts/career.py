#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Canonical career-ledger loading, privacy projection, and validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CAREER_LEDGER = REPOSITORY_ROOT / "content" / "career.json"
APPLICATION_CONTACT_FIELDS = frozenset({"email", "phone", "location"})
REQUIRED_PROVENANCE_FIELDS = frozenset({"source", "status", "reviewed_on"})
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[+()\d\s.-]{7,}$")
PUBLIC_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    flags=re.IGNORECASE,
)
PUBLIC_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)


class CareerValidationError(ValueError):
    """Raised when canonical career content violates its publication contract."""


def load_ledger(path: Path = CAREER_LEDGER) -> dict[str, Any]:
    """Load and validate the canonical public career ledger."""
    if not path.exists():
        raise FileNotFoundError(f"Career ledger not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CareerValidationError("Career ledger must be a JSON object.")
    validate_ledger(data)
    return data


def validate_ledger(data: dict[str, Any]) -> None:
    """Validate chronology, provenance, privacy, claims, and evidence links."""
    errors: list[str] = []

    required_top_level = {
        "schema_version",
        "reviewed_on",
        "canonical_lane",
        "identity",
        "privacy",
        "roles",
        "claims",
        "research_artifacts",
        "education",
        "skill_groups",
    }
    missing = sorted(required_top_level - set(data))
    if missing:
        errors.append(f"Missing top-level field(s): {', '.join(missing)}")

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1.")
    if data.get("canonical_lane") != "platform-devex":
        errors.append("canonical_lane must remain 'platform-devex' for this baseline.")

    identity = mapping(data.get("identity"), "identity", errors)
    public_links = identity.get("public_links", []) if identity else []
    seen_link_ids: set[str] = set()
    if not isinstance(public_links, list) or not public_links:
        errors.append("identity.public_links must be a non-empty list.")
    else:
        for index, link in enumerate(public_links):
            if not isinstance(link, dict):
                errors.append(f"identity.public_links[{index}] must be an object.")
                continue
            link_id = str(link.get("id", ""))
            if not link_id or link_id in seen_link_ids:
                errors.append(f"identity.public_links[{index}] has a missing or duplicate id.")
            seen_link_ids.add(link_id)
            validate_https_url(str(link.get("url", "")), f"public link '{link_id}'", errors)
            audiences = link.get("audiences")
            if not isinstance(audiences, list) or not set(audiences).issubset(
                {"public", "application"}
            ):
                errors.append(f"public link '{link_id}' has invalid audiences.")

    privacy = mapping(data.get("privacy"), "privacy", errors)
    public_policy = mapping(privacy.get("public") if privacy else None, "privacy.public", errors)
    application_policy = mapping(
        privacy.get("application") if privacy else None,
        "privacy.application",
        errors,
    )
    if public_policy:
        allowed_public = set(public_policy.get("allowed_contact_fields", []))
        if allowed_public != {"public_location", "public_links"}:
            errors.append(
                "privacy.public.allowed_contact_fields must be exactly public_location and public_links."
            )
        forbidden_types = set(public_policy.get("forbidden_contact_types", []))
        if forbidden_types != {"email", "phone", "precise_city"}:
            errors.append(
                "privacy.public.forbidden_contact_types must be exactly email, phone, and precise_city."
            )
    if application_policy:
        allowed_application = set(application_policy.get("allowed_contact_fields", []))
        if allowed_application != APPLICATION_CONTACT_FIELDS:
            errors.append(
                "privacy.application.allowed_contact_fields must be exactly email, phone, and location."
            )
        if application_policy.get("requires_contact_overlay") is not True:
            errors.append("privacy.application.requires_contact_overlay must be true.")

    roles = mapping(data.get("roles"), "roles", errors)
    for role_id, role in roles.items() if roles else []:
        if not isinstance(role, dict):
            errors.append(f"roles.{role_id} must be an object.")
            continue
        validate_date_range(role, f"roles.{role_id}", errors)
        validate_provenance(role.get("provenance"), f"roles.{role_id}", errors)

    incompris = roles.get("incompris", {}) if roles else {}
    if incompris.get("category") != "independent-engineering-research":
        errors.append(
            "Incompris must remain categorized as independent-engineering-research until owner verification."
        )
    if incompris.get("overlap_qualifier") is not None:
        errors.append("Incompris overlap_qualifier must remain null until owner verification.")
    unverified_status_words = re.compile(
        r"\b(part[- ]?time|full[- ]?time|consult(?:ing|ant)|nights? and weekends?)\b",
        flags=re.IGNORECASE,
    )
    incompris_blob = json.dumps(incompris, ensure_ascii=False)
    if unverified_status_words.search(incompris_blob):
        errors.append("Incompris contains an unverified employment-status qualifier.")

    claims = mapping(data.get("claims"), "claims", errors)
    for claim_id, claim in claims.items() if claims else []:
        if not isinstance(claim, dict):
            errors.append(f"claims.{claim_id} must be an object.")
            continue
        if claim.get("subject") not in roles:
            errors.append(f"claims.{claim_id} references an unknown role subject.")
        for projection in ("application_text", "public_text"):
            text = claim.get(projection)
            if not isinstance(text, str) or not text.strip():
                errors.append(f"claims.{claim_id}.{projection} must be non-empty text.")
        validate_provenance(claim.get("provenance"), f"claims.{claim_id}", errors)
        metric = claim.get("metric")
        if metric is not None:
            if not isinstance(metric, dict):
                errors.append(f"claims.{claim_id}.metric must be an object.")
            else:
                qualifiers = metric.get("required_qualifiers", [])
                for projection in ("application_text", "public_text"):
                    projected = str(claim.get(projection, "")).casefold()
                    for qualifier in qualifiers:
                        if str(qualifier).casefold() not in projected:
                            errors.append(
                                f"claims.{claim_id}.{projection} is missing required qualifier '{qualifier}'."
                            )
        public_text = str(claim.get("public_text", ""))
        for leak in find_public_contact_leaks(public_text):
            errors.append(f"claims.{claim_id}.public_text exposes public {leak} data.")

    education = data.get("education")
    if not isinstance(education, list) or not education:
        errors.append("education must be a non-empty list.")
    else:
        for index, entry in enumerate(education):
            if not isinstance(entry, dict):
                errors.append(f"education[{index}] must be an object.")
                continue
            validate_date_range(entry, f"education[{index}]", errors)
            validate_provenance(entry.get("provenance"), f"education[{index}]", errors)

    artifacts = mapping(data.get("research_artifacts"), "research_artifacts", errors)
    reflector = artifacts.get("reflector", {}) if artifacts else {}
    if reflector.get("status") != "Independent DOI-backed research artifact":
        errors.append("Reflector status must be 'Independent DOI-backed research artifact'.")
    if reflector.get("concept_doi") != "10.5281/zenodo.20477044":
        errors.append("Reflector must use the version-independent concept DOI.")
    validate_https_url(
        str(reflector.get("concept_url", "")),
        "Reflector concept URL",
        errors,
    )
    validate_provenance(reflector.get("provenance"), "research_artifacts.reflector", errors)

    skill_groups = mapping(data.get("skill_groups"), "skill_groups", errors)
    for group_id, group in skill_groups.items() if skill_groups else []:
        if not isinstance(group, dict):
            errors.append(f"skill_groups.{group_id} must be an object.")
            continue
        items = group.get("items")
        evidence = group.get("evidence")
        if not isinstance(items, list) or not items:
            errors.append(f"skill_groups.{group_id}.items must be non-empty.")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"skill_groups.{group_id}.evidence must be non-empty.")
        else:
            unknown = sorted(set(evidence) - set(claims))
            if unknown:
                errors.append(
                    f"skill_groups.{group_id} references unknown claim(s): {', '.join(unknown)}"
                )

    if errors:
        raise CareerValidationError("\n".join(errors))


def load_application_contact(path: Path, *, allow_empty: bool = False) -> dict[str, str]:
    """Load the ignored application-only contact overlay."""
    if not path.exists():
        raise FileNotFoundError(f"Application contact overlay not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise CareerValidationError("Application contact overlay must be a JSON object.")

    unknown = sorted(set(raw) - APPLICATION_CONTACT_FIELDS)
    if unknown:
        raise CareerValidationError(
            f"Unsupported application contact field(s): {', '.join(unknown)}"
        )

    contact = {key: str(value).strip() for key, value in raw.items()}
    if not allow_empty and not any(contact.get(key) for key in ("email", "phone")):
        raise CareerValidationError(
            "Application contact overlay must include an approved email or phone number."
        )
    if contact.get("email") and not EMAIL_PATTERN.fullmatch(contact["email"]):
        raise CareerValidationError("Application contact email is not valid.")
    if contact.get("phone") and not PHONE_PATTERN.fullmatch(contact["phone"]):
        raise CareerValidationError("Application contact phone is not valid.")
    return contact


def destination_links(data: dict[str, Any], audience: str) -> list[dict[str, Any]]:
    """Return only allowlisted recruiter destinations for an audience."""
    return [
        link
        for link in data["identity"]["public_links"]
        if audience in link.get("audiences", [])
    ]


def projected_claims(
    data: dict[str, Any],
    claim_ids: tuple[str, ...],
    *,
    subject: str,
    audience: str,
) -> list[str]:
    """Project selected canonical claims into audience-approved wording."""
    key = "public_text" if audience == "public" else "application_text"
    projected: list[str] = []
    for claim_id in claim_ids:
        claim = data["claims"][claim_id]
        if claim["subject"] == subject:
            projected.append(str(claim[key]).strip())
    return projected


def find_public_contact_leaks(value: str) -> list[str]:
    """Return private contact types present in public-facing text."""
    leaks: list[str] = []
    if PUBLIC_EMAIL_PATTERN.search(value):
        leaks.append("email")
    if PUBLIC_PHONE_PATTERN.search(value):
        leaks.append("phone")
    return leaks


def latex_escape(value: str) -> str:
    """Escape user-facing canonical text for LaTeX without changing meaning."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def mapping(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object.")
        return {}
    return value


def validate_provenance(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{name}.provenance must be an object.")
        return
    missing = sorted(REQUIRED_PROVENANCE_FIELDS - set(value))
    if missing:
        errors.append(f"{name}.provenance missing field(s): {', '.join(missing)}")
    if value.get("status") != "verified":
        errors.append(f"{name}.provenance.status must be verified.")


def validate_date_range(value: dict[str, Any], name: str, errors: list[str]) -> None:
    start = value.get("start")
    end = value.get("end")
    if not isinstance(start, str) or not DATE_PATTERN.fullmatch(start):
        errors.append(f"{name}.start must use YYYY-MM.")
    if end is not None and (not isinstance(end, str) or not DATE_PATTERN.fullmatch(end)):
        errors.append(f"{name}.end must be null or use YYYY-MM.")
    if isinstance(start, str) and isinstance(end, str) and start > end:
        errors.append(f"{name}.start must not be after end.")


def validate_https_url(value: str, name: str, errors: list[str]) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"{name} must be an absolute HTTPS URL.")
