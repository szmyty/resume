#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
MISSING = object()

# Canonical paper title — single source of truth for title consistency checks.
# Must match the value defined in paper/config/title.tex (\papertitlefull) and
# metadata/publication.yaml (title.full).
CANONICAL_TITLE = (
    "reflector: reflective synchronization systems for recursive AI-assisted software engineering"
)

# Canonical ORCID identifier — must match metadata/authors.yaml and all downstream surfaces.
CANONICAL_ORCID = "0009-0008-5291-9795"


def load_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {path}.")
    except json.JSONDecodeError as error:
        log_error(f"Invalid JSON in {path}: {error}.")
    return None


def load_yaml(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {path}.")
        return None
    except yaml.YAMLError as error:
        log_error(f"Invalid YAML in {path}: {error}.")
        return None

    if not isinstance(data, dict):
        log_error(f"Expected mapping at root of {path}.")
        return None
    return data


def load_latex_title(path: Path) -> str | None:
    """Extract the \\papertitlefull expansion from a LaTeX title config file.

    Reads \\papertitlemain and \\papertitlesubtitle definitions and assembles
    the full title as ``<main>: <subtitle>`` so that the Python representation
    matches the LaTeX \\papertitlefull macro without requiring a live TeX run.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        log_error(f"Missing required title config: {path}.")
        return None

    def extract_command(name: str) -> str | None:
        pattern = re.compile(
            rf"\\newcommand{{\\{name}}}{{%\n\s*(.*?)%\n}}",
            re.DOTALL,
        )
        match = pattern.search(content)
        if not match:
            return None
        return " ".join(match.group(1).split())

    main = extract_command("papertitlemain")
    subtitle = extract_command("papertitlesubtitle")
    if main is None or subtitle is None:
        log_error(
            f"Could not parse \\papertitlemain or \\papertitlesubtitle in {path}."
        )
        return None
    return f"{main}: {subtitle}"


def log_error(message: str) -> None:
    print(f"[metadata] {message}", file=sys.stderr)


def _normalise_title(value: object) -> object:
    """Collapse multi-line YAML title strings to a single normalised line.

    YAML ``>-`` block scalars fold newlines into spaces, but the resulting
    string may still contain extra internal whitespace.  This helper collapses
    any run of whitespace to a single space so that the comparison against the
    canonical title is whitespace-agnostic.
    """
    if value is MISSING or not isinstance(value, str):
        return value
    return " ".join(value.split())


def _extract_citation_orcid(citation: dict) -> object:
    """Extract the bare ORCID identifier from CITATION.cff authors[0].

    The CFF spec stores orcid as a full URL (https://orcid.org/XXXX-XXXX-XXXX-XXXX).
    This helper returns only the bare identifier portion so it can be compared
    against CANONICAL_ORCID.
    """
    authors = citation.get("authors", [])
    if not isinstance(authors, list) or not authors:
        return MISSING
    orcid_url = authors[0].get("orcid", MISSING)
    if orcid_url is MISSING or not isinstance(orcid_url, str):
        return MISSING
    prefix = "https://orcid.org/"
    if orcid_url.startswith(prefix):
        return orcid_url[len(prefix):]
    return orcid_url


def _extract_zenodo_orcid(zenodo: dict) -> object:
    """Extract the bare ORCID identifier from .zenodo.json creators[0]."""
    creators = zenodo.get("creators", [])
    if not isinstance(creators, list) or not creators:
        return MISSING
    return creators[0].get("orcid", MISSING)


def _normalise_doi(value: object) -> object:
    if value is MISSING or value is None:
        return MISSING
    if not isinstance(value, str):
        return value
    doi = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi


def main() -> int:
    repository_root = Path(__file__).resolve().parent.parent

    version_path = repository_root / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        log_error(f"Missing required metadata file: {version_path}.")
        return 1
    if not SEMVER_PATTERN.fullmatch(version):
        log_error(f"VERSION must be semantic version MAJOR.MINOR.PATCH, got '{version}'.")
        return 1

    # ---------------------------------------------------------------------------
    # Canonical metadata layer — metadata/ is the primary source of truth.
    # ---------------------------------------------------------------------------

    meta_publication = load_yaml(repository_root / "metadata" / "publication.yaml")
    meta_repository = load_yaml(repository_root / "metadata" / "repository.yaml")
    meta_authors = load_yaml(repository_root / "metadata" / "authors.yaml")
    meta_citations = load_yaml(repository_root / "metadata" / "citations.yaml")
    meta_renderers = load_yaml(repository_root / "metadata" / "renderers.yaml")
    if any(
        item is None
        for item in (meta_publication, meta_repository, meta_authors, meta_citations, meta_renderers)
    ):
        return 1

    has_error = False

    # Validate canonical publication title.
    title_block = meta_publication.get("title")
    canonical_title_full = title_block.get("full", MISSING) if isinstance(title_block, dict) else MISSING
    if canonical_title_full is MISSING:
        has_error = True
        log_error("Missing required field: metadata/publication.yaml title.full.")
    elif _normalise_title(canonical_title_full) != CANONICAL_TITLE:
        has_error = True
        log_error(
            f"metadata/publication.yaml title.full does not match canonical title.\n"
            f"  expected: '{CANONICAL_TITLE}'\n"
            f"  found:    '{_normalise_title(canonical_title_full)}'"
        )

    # Validate canonical publication version agrees with VERSION file.
    canonical_version = meta_publication.get("version", MISSING)
    if canonical_version is MISSING:
        log_error("Missing required field: metadata/publication.yaml version.")
        return 1
    if str(canonical_version) != version:
        log_error(
            f"metadata/publication.yaml version must equal VERSION ('{version}'), "
            f"found '{canonical_version}'."
        )
        return 1

    # Validate canonical author ORCID.
    _raw_authors = meta_authors.get("authors")
    canonical_authors = _raw_authors if isinstance(_raw_authors, list) else []
    if not canonical_authors:
        has_error = True
        log_error("metadata/authors.yaml authors list is missing or empty.")
    else:
        first_author_orcid = canonical_authors[0].get("orcid", MISSING)
        if first_author_orcid is MISSING:
            has_error = True
            log_error("metadata/authors.yaml authors[0].orcid is missing.")
        elif str(first_author_orcid) != CANONICAL_ORCID:
            has_error = True
            log_error(
                f"metadata/authors.yaml authors[0].orcid does not match canonical ORCID.\n"
                f"  expected: '{CANONICAL_ORCID}'\n"
                f"  found:    '{first_author_orcid}'"
            )

    # Validate canonical repository URLs are present.
    canonical_repo_github_url = meta_repository.get("github_url", MISSING)
    canonical_repo_pages_url = meta_repository.get("pages_url", MISSING)
    for field_name, field_value in [
        ("metadata/repository.yaml github_url", canonical_repo_github_url),
        ("metadata/repository.yaml pages_url", canonical_repo_pages_url),
    ]:
        if field_value is MISSING:
            has_error = True
            log_error(f"Missing required field: {field_name}.")

    # ---------------------------------------------------------------------------
    # Downstream metadata files — must remain consistent with metadata/ layer.
    # ---------------------------------------------------------------------------

    publication = load_json(repository_root / "publication.json")
    release_manifest = load_json(repository_root / "release-manifest.json")
    release_please_manifest = load_json(repository_root / ".release-please-manifest.json")
    citation = load_yaml(repository_root / "CITATION.cff")
    zenodo = load_json(repository_root / ".zenodo.json")
    codemeta = load_json(repository_root / "codemeta.json")
    readme_json = load_json(repository_root / "paper" / "00README.json")
    if any(
        item is None
        for item in (publication, release_manifest, release_please_manifest, citation, zenodo, codemeta, readme_json)
    ):
        return 1

    checks = [
        ("publication.json.version", publication.get("version", MISSING)),
        ("publication.json.release_tag", publication.get("release_tag", MISSING)),
        ("release-manifest.json.current_version", release_manifest.get("current_version", MISSING)),
        (".release-please-manifest.json['.']", release_please_manifest.get(".", MISSING)),
        ("CITATION.cff.version", citation.get("version", MISSING)),
    ]

    expected_values = {
        "publication.json.release_tag": f"v{version}",
    }

    for name, actual_value in checks:
        if actual_value is MISSING:
            has_error = True
            log_error(f"Missing required metadata field: {name}.")
            continue

        expected = expected_values.get(name, version)
        if actual_value != expected:
            has_error = True
            print(
                f"[metadata] {name} must equal '{expected}' (found '{actual_value}').",
                file=sys.stderr,
            )

    # ---------------------------------------------------------------------------
    # Title consistency — every metadata surface must carry the canonical title.
    # ---------------------------------------------------------------------------

    latex_title = load_latex_title(repository_root / "paper" / "config" / "title.tex")
    if latex_title is None:
        has_error = True
    elif latex_title != CANONICAL_TITLE:
        has_error = True
        log_error(
            f"paper/config/title.tex title does not match canonical title.\n"
            f"  expected: '{CANONICAL_TITLE}'\n"
            f"  found:    '{latex_title}'"
        )

    title_checks = [
        ("CITATION.cff.title", _normalise_title(citation.get("title", MISSING))),
        (".zenodo.json.title", zenodo.get("title", MISSING)),
        ("paper/00README.json.publication.title", readme_json.get("publication", {}).get("title", MISSING)),
    ]

    for name, actual_title in title_checks:
        if actual_title is MISSING:
            has_error = True
            log_error(f"Missing required title field: {name}.")
            continue
        if actual_title != CANONICAL_TITLE:
            has_error = True
            log_error(
                f"{name} does not match canonical title.\n"
                f"  expected: '{CANONICAL_TITLE}'\n"
                f"  found:    '{actual_title}'"
            )

    # ---------------------------------------------------------------------------
    # ORCID consistency — canonical ORCID must match all downstream surfaces.
    # ---------------------------------------------------------------------------

    orcid_checks = [
        ("CITATION.cff.authors[0].orcid", _extract_citation_orcid(citation)),
        (".zenodo.json.creators[0].orcid", _extract_zenodo_orcid(zenodo)),
    ]

    for name, actual_orcid in orcid_checks:
        if actual_orcid is MISSING:
            has_error = True
            log_error(f"Missing required ORCID field: {name}.")
            continue
        if actual_orcid != CANONICAL_ORCID:
            has_error = True
            log_error(
                f"{name} does not match canonical ORCID.\n"
                f"  expected: '{CANONICAL_ORCID}'\n"
                f"  found:    '{actual_orcid}'"
            )

    # ---------------------------------------------------------------------------
    # DOI consistency — canonical DOI must match all publication metadata surfaces.
    # ---------------------------------------------------------------------------

    publication_identifiers = meta_publication.get("identifiers", {})
    canonical_doi = (
        _normalise_doi(publication_identifiers.get("doi", MISSING))
        if isinstance(publication_identifiers, dict)
        else MISSING
    )
    canonical_doi_url = (
        publication_identifiers.get("doi_url", MISSING)
        if isinstance(publication_identifiers, dict)
        else MISSING
    )
    canonical_concept_doi = (
        _normalise_doi(publication_identifiers.get("zenodo_concept_doi", MISSING))
        if isinstance(publication_identifiers, dict)
        else MISSING
    )

    for field_name, field_value in [
        ("metadata/publication.yaml identifiers.doi", canonical_doi),
        ("metadata/publication.yaml identifiers.doi_url", canonical_doi_url),
        ("metadata/publication.yaml identifiers.zenodo_concept_doi", canonical_concept_doi),
    ]:
        if field_value is MISSING:
            has_error = True
            log_error(f"Missing required DOI field: {field_name}.")

    if canonical_doi is not MISSING and not DOI_PATTERN.fullmatch(str(canonical_doi)):
        has_error = True
        log_error(f"metadata/publication.yaml identifiers.doi is not a valid DOI: '{canonical_doi}'.")
    if (
        canonical_doi is not MISSING
        and canonical_doi_url is not MISSING
        and canonical_doi_url != f"https://doi.org/{canonical_doi}"
    ):
        has_error = True
        log_error(
            "metadata/publication.yaml identifiers.doi_url does not match canonical DOI.\n"
            f"  expected: 'https://doi.org/{canonical_doi}'\n"
            f"  found:    '{canonical_doi_url}'"
        )

    if canonical_doi is not MISSING:
        doi_checks = [
            ("CITATION.cff.doi", _normalise_doi(citation.get("doi", MISSING))),
            (".zenodo.json.doi", _normalise_doi(zenodo.get("doi", MISSING))),
            ("publication.json.future.doi_generation.doi", _normalise_doi(
                publication.get("future", {}).get("doi_generation", {}).get("doi", MISSING)
            )),
            ("release-manifest.json.future_integrations.doi.canonical_doi", _normalise_doi(
                release_manifest.get("future_integrations", {}).get("doi", {}).get("canonical_doi", MISSING)
            )),
            ("codemeta.json.identifier", _normalise_doi(codemeta.get("identifier", MISSING))),
        ]
        for name, actual_doi in doi_checks:
            if actual_doi is MISSING:
                has_error = True
                log_error(f"Missing required DOI field: {name}.")
                continue
            if actual_doi != canonical_doi:
                has_error = True
                log_error(
                    f"{name} does not match canonical DOI.\n"
                    f"  expected: '{canonical_doi}'\n"
                    f"  found:    '{actual_doi}'"
                )

        doi_url_checks = [
            ("publication.json.future.doi_generation.doi_url", publication.get("future", {}).get("doi_generation", {}).get("doi_url", MISSING)),
            ("release-manifest.json.future_integrations.doi.canonical_doi_url", release_manifest.get("future_integrations", {}).get("doi", {}).get("canonical_doi_url", MISSING)),
        ]
        for name, actual_url in doi_url_checks:
            if actual_url is MISSING:
                has_error = True
                log_error(f"Missing required DOI URL field: {name}.")
                continue
            expected_url = f"https://doi.org/{canonical_doi}"
            if actual_url != expected_url:
                has_error = True
                log_error(
                    f"{name} does not match canonical DOI URL.\n"
                    f"  expected: '{expected_url}'\n"
                    f"  found:    '{actual_url}'"
                )

    repository_zenodo = meta_repository.get("future_integrations", {}).get("zenodo", {})
    repository_concept_doi = _normalise_doi(repository_zenodo.get("concept_doi", MISSING))
    if canonical_concept_doi is not MISSING and repository_concept_doi != canonical_concept_doi:
        has_error = True
        log_error(
            "metadata/repository.yaml future_integrations.zenodo.concept_doi does not match canonical concept DOI.\n"
            f"  expected: '{canonical_concept_doi}'\n"
            f"  found:    '{repository_concept_doi}'"
        )
    if canonical_concept_doi is not MISSING:
        concept_checks = [
            (".zenodo.json.conceptdoi", _normalise_doi(zenodo.get("conceptdoi", MISSING))),
            ("publication.json.future.doi_generation.concept_doi", _normalise_doi(
                publication.get("future", {}).get("doi_generation", {}).get("concept_doi", MISSING)
            )),
            ("release-manifest.json.future_integrations.zenodo.concept_doi", _normalise_doi(
                release_manifest.get("future_integrations", {}).get("zenodo", {}).get("concept_doi", MISSING)
            )),
        ]
        for name, actual_doi in concept_checks:
            if actual_doi is MISSING:
                has_error = True
                log_error(f"Missing required concept DOI field: {name}.")
                continue
            if actual_doi != canonical_concept_doi:
                has_error = True
                log_error(
                    f"{name} does not match canonical concept DOI.\n"
                    f"  expected: '{canonical_concept_doi}'\n"
                    f"  found:    '{actual_doi}'"
                )

    codemeta_checks = [
        ("codemeta.json.name", codemeta.get("name", MISSING), meta_repository.get("name", MISSING)),
        ("codemeta.json.version", codemeta.get("version", MISSING), version),
        ("codemeta.json.codeRepository", codemeta.get("codeRepository", MISSING), canonical_repo_github_url),
        ("codemeta.json.url", codemeta.get("url", MISSING), canonical_repo_pages_url),
    ]
    for name, actual_value, expected in codemeta_checks:
        if actual_value is MISSING:
            has_error = True
            log_error(f"Missing required codemeta field: {name}.")
            continue
        if expected is not MISSING and actual_value != expected:
            has_error = True
            log_error(
                f"{name} does not match canonical metadata.\n"
                f"  expected: '{expected}'\n"
                f"  found:    '{actual_value}'"
            )

    # ---------------------------------------------------------------------------
    # Repository URL consistency — canonical URLs must match downstream surfaces.
    # ---------------------------------------------------------------------------

    if canonical_repo_github_url is not MISSING and canonical_repo_pages_url is not MISSING:
        repo_url_checks = [
            ("publication.json.repository_url", publication.get("repository_url", MISSING), canonical_repo_github_url),
            ("publication.json.pages_url", publication.get("pages_url", MISSING), canonical_repo_pages_url),
            ("paper/00README.json.publication.repository", readme_json.get("publication", {}).get("repository", MISSING), canonical_repo_github_url),
            ("paper/00README.json.publication.pages_url", readme_json.get("publication", {}).get("pages_url", MISSING), canonical_repo_pages_url),
        ]

        for name, actual_url, expected_url in repo_url_checks:
            if actual_url is MISSING:
                has_error = True
                log_error(f"Missing required URL field: {name}.")
                continue
            if actual_url != expected_url:
                has_error = True
                log_error(
                    f"{name} does not match canonical URL.\n"
                    f"  expected: '{expected_url}'\n"
                    f"  found:    '{actual_url}'"
                )

    if has_error:
        return 1

    print("[metadata] metadata validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
