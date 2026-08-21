#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Career-content, ATS, PDF, privacy, and destination quality gates."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import build
import career


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLACEHOLDER_PATHS = (
    "content/*.json",
    "profiles/*.yaml",
    "documents/*.yaml",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bFIXME\b", flags=re.IGNORECASE),
    re.compile(r"\bplaceholder\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)
DEFAULT_REQUIRED_HEADINGS = ("Summary", "Experience", "Education", "Skills")
REQUIRED_IDENTITY_PHRASES = (
    "Alan Szmyt",
    "MIT Lincoln Laboratory",
    "Incompris LLC",
    "Boston University",
    "University of Massachusetts Lowell",
)
KNOWN_TOKEN_JOIN_PATTERNS = (
    re.compile(r"\bAuthoredreflector\b", flags=re.IGNORECASE),
    re.compile(r"\bAIassisted\b", flags=re.IGNORECASE),
    re.compile(r"\bParadigms:Software\b", flags=re.IGNORECASE),
    re.compile(r"\bEngineering\(2026\)", flags=re.IGNORECASE),
    re.compile(r"[A-Za-z]:[A-Z]"),
)
# A section-aligned two-page résumé can be visually balanced while page two
# carries fewer words (for example, research, education, and skills). This floor
# rejects accidental near-empty spill pages; the independent 58% spatial gate
# remains the stricter layout requirement.
MIN_PAGE_WORD_SHARE = 0.30
MIN_PAGE_VERTICAL_OCCUPANCY = 0.58


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run résumé publication quality gates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-facts", help="Validate the canonical career ledger.")
    subparsers.add_parser("validate-profiles", help="Validate role profile definitions.")
    subparsers.add_parser(
        "validate-documents", help="Validate document manifest definitions."
    )

    placeholders = subparsers.add_parser(
        "check-placeholders",
        help="Fail when unresolved placeholder content is present.",
    )
    placeholders.add_argument(
        "--path",
        action="append",
        default=[],
        help="Glob path relative to the repository root. Repeatable.",
    )

    destinations = subparsers.add_parser(
        "validate-destinations",
        help="Validate every recruiter-facing destination in the ledger.",
    )
    destinations.add_argument(
        "--audience",
        choices=("public", "application"),
        default="public",
    )
    destinations.add_argument(
        "--online",
        action="store_true",
        help="Perform network reachability checks in addition to deterministic URL checks.",
    )

    ats = subparsers.add_parser(
        "validate-ats",
        help="Validate Poppler and pypdf text extraction from a generated PDF.",
    )
    ats.add_argument("--pdf", required=True, help="Generated PDF to validate.")
    ats.add_argument(
        "--require-heading",
        action="append",
        default=[],
        help="Required extracted heading. Repeatable.",
    )
    ats.add_argument(
        "--audience",
        choices=("public", "application"),
        default="public",
    )
    ats.add_argument("--summary-file", default=None)

    pdf = subparsers.add_parser(
        "validate-pdf",
        help="Validate PDF metadata, privacy, links, density, safety, and filename.",
    )
    pdf.add_argument("--pdf", required=True, help="Generated PDF to validate.")
    pdf.add_argument(
        "--audience",
        choices=("public", "application"),
        required=True,
    )
    pdf.add_argument(
        "--contact-file",
        default=None,
        help="Approved application contact overlay used for this artifact.",
    )
    pdf.add_argument("--summary-file", default=None)
    return parser.parse_args()


def validate_facts() -> int:
    try:
        ledger = career.load_ledger()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Career fact validation failed:\n{exc}", file=sys.stderr)
        return 1

    locked = {
        ("canonical_lane",): "platform-devex",
        ("identity", "public_location"): "Greater Boston, MA",
        ("roles", "mit-lincoln-laboratory", "title"): "Software Engineer, Associate Staff",
        ("roles", "mit-lincoln-laboratory", "organization"): "MIT Lincoln Laboratory",
        ("roles", "mit-lincoln-laboratory", "start"): "2019-04",
        ("roles", "mit-lincoln-laboratory", "end"): "2025-08",
        ("roles", "mit-lincoln-laboratory", "display_dates"): "Apr 2019 - Aug 2025",
        ("roles", "incompris", "title"): "Founder & Systems Architect",
        ("roles", "incompris", "start"): "2023-01",
        ("roles", "incompris", "display_dates"): "Jan 2023 - Present",
        ("research_artifacts", "reflector", "status"): "Independent DOI-backed research artifact",
        ("research_artifacts", "reflector", "concept_doi"): "10.5281/zenodo.20477044",
    }
    errors = []
    for path, expected in locked.items():
        value: Any = ledger
        for part in path:
            value = value[part]
        if value != expected:
            errors.append(f"{'.'.join(path)} must remain '{expected}'.")

    education = {entry["id"]: entry for entry in ledger["education"]}
    expected_education = {
        "boston-university-ms": {
            "institution": "Boston University",
            "degree": "M.S., Software Development",
            "start": "2021-09",
            "end": "2023-04",
            "display_dates": "Sep 2021 - Apr 2023",
        },
        "umass-lowell-bs": {
            "institution": "University of Massachusetts Lowell",
            "degree": "B.S., Computer Science; Minor in Mathematics",
            "start": "2012-09",
            "end": "2017-01",
            "display_dates": "Sep 2012 - Jan 2017",
        },
    }
    for education_id, expected in expected_education.items():
        entry = education.get(education_id)
        if entry is None:
            errors.append(f"{education_id} must remain in the canonical ledger.")
            continue
        for key, value in expected.items():
            if entry.get(key) != value:
                errors.append(f"{education_id}.{key} must remain '{value}'.")

    if errors:
        print("Career fact validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Validated canonical career ledger: {len(ledger['roles'])} roles, "
        f"{len(ledger['claims'])} claims, {len(ledger['education'])} education records."
    )
    return 0


def validate_documents() -> int:
    try:
        documents = build.load_document_manifests()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Document validation failed: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for doc_path in sorted(build.DOCUMENTS_DIR.glob("*.yaml")):
        try:
            document = build.load_document_manifest(doc_path)
        except ValueError as exc:
            errors.append(f"{doc_path.name}: {exc}")
            continue
        if document.document_type != doc_path.stem:
            errors.append(
                f"{doc_path}: document_type must match filename '{doc_path.stem}'."
            )
        if not document.default_section_order or not document.section_pool:
            errors.append(f"{doc_path}: section pool and default order must be non-empty.")
        missing = set(document.default_section_order) - set(document.section_pool)
        if missing:
            errors.append(
                f"{doc_path}: default order contains unknown sections: {', '.join(sorted(missing))}."
            )

    if errors:
        print("Document validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Validated {len(documents)} document manifest(s).")
    return 0


def validate_profiles() -> int:
    try:
        profiles = build.load_profiles()
        ledger = career.load_ledger()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Profile validation failed: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    all_known_sections = build.CV_SECTIONS
    all_claim_ids = set(ledger["claims"])
    all_skill_group_ids = set(ledger["skill_groups"])

    for profile_path in sorted(build.PROFILES_DIR.glob("*.yaml")):
        try:
            profile = build.load_profile(profile_path)
        except ValueError as exc:
            errors.append(f"{profile_path.name}: {exc}")
            continue

        if profile.profile != profile_path.stem:
            errors.append(f"{profile_path}: profile id must match its filename.")
        if not profile.keyword_emphasis:
            errors.append(f"{profile_path}: keyword_emphasis must be non-empty.")
        if not profile.headline or not profile.summary:
            errors.append(f"{profile_path}: headline and summary must be non-empty.")
        if re.search(r"\bstaff engineer\b", profile.headline, flags=re.IGNORECASE):
            errors.append(f"{profile_path}: unsupported market-level Staff Engineer wording.")

        unknown_sections = sorted(
            (set(profile.section_order) | set(profile.included_sections))
            - all_known_sections
        )
        if unknown_sections:
            errors.append(
                f"{profile_path.name}: unknown sections: {', '.join(unknown_sections)}."
            )
        missing_order = [
            section
            for section in profile.included_sections
            if section not in profile.section_order
        ]
        if missing_order:
            errors.append(
                f"{profile_path.name}: included sections missing from order: "
                f"{', '.join(missing_order)}."
            )

        unknown_claims = sorted(set(profile.claim_ids) - all_claim_ids)
        if unknown_claims:
            errors.append(
                f"{profile_path.name}: unknown claims: {', '.join(unknown_claims)}."
            )
        unknown_groups = sorted(set(profile.skill_group_ids) - all_skill_group_ids)
        if unknown_groups:
            errors.append(
                f"{profile_path.name}: unknown skill groups: {', '.join(unknown_groups)}."
            )

        effective_profile = "platform" if profile.profile == "general" else profile.profile
        for claim_id in set(profile.claim_ids) & all_claim_ids:
            if effective_profile not in ledger["claims"][claim_id]["profiles"]:
                errors.append(
                    f"{profile_path.name}: claim '{claim_id}' is not approved for this role profile."
                )
        for group_id in set(profile.skill_group_ids) & all_skill_group_ids:
            evidence = set(ledger["skill_groups"][group_id]["evidence"])
            if not evidence.intersection(profile.claim_ids):
                errors.append(
                    f"{profile_path.name}: skill group '{group_id}' has no selected claim evidence."
                )

    required_profiles = {"general", "platform", "research", "mobile-geospatial"}
    if set(profiles) != required_profiles:
        errors.append(
            "Profile set must be exactly general, platform, research, and mobile-geospatial."
        )

    if errors:
        print("Profile validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Validated {len(profiles)} role profile definition(s).")
    return 0


def check_placeholders(paths: list[str]) -> int:
    findings: list[str] = []
    for relative in paths or list(DEFAULT_PLACEHOLDER_PATHS):
        for candidate in sorted(REPOSITORY_ROOT.glob(relative)):
            if not candidate.is_file():
                continue
            for line_number, line in enumerate(
                candidate.read_text(encoding="utf-8").splitlines(), 1
            ):
                stripped = line.strip()
                if not stripped or stripped.startswith(("#", "%")):
                    continue
                if any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS):
                    findings.append(
                        f"{candidate.relative_to(REPOSITORY_ROOT)}:{line_number}: {stripped}"
                    )

    if findings:
        print("Placeholder content detected:")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("No placeholder content detected.")
    return 0


def validate_destinations(audience: str, online: bool) -> int:
    try:
        ledger = career.load_ledger()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Destination validation failed: {exc}", file=sys.stderr)
        return 1

    links = career.destination_links(ledger, audience)
    reflector = ledger["research_artifacts"]["reflector"]
    links = [
        *links,
        {
            "id": "reflector-doi",
            "label": reflector["concept_doi"],
            "url": reflector["concept_url"],
        },
    ]
    errors: list[str] = []
    for link in links:
        url = str(link["url"])
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{link['id']}: expected an absolute HTTPS URL, found {url!r}.")
            continue
        if online:
            error = check_url_online(url)
            if error:
                errors.append(f"{link['id']}: {error}")

    if errors:
        print("Destination validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "online" if online else "deterministic"
    print(f"Validated {len(links)} {audience} destinations ({mode}).")
    return 0


def check_url_online(url: str) -> str | None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "szmyty-resume-link-validator/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
    except (urllib.error.URLError, TimeoutError) as exc:
        return str(exc)
    if status >= 400 and status not in {401, 403}:
        return f"HTTP {status}"
    return None


def validate_ats(
    pdf: Path,
    required_headings: list[str],
    summary_file: str | None,
    audience: str = "public",
) -> int:
    errors: list[str] = []
    if not pdf.exists():
        print(f"ATS validation failed: PDF not found at '{pdf}'.", file=sys.stderr)
        return 1
    if shutil.which("pdftotext") is None:
        print("ATS validation failed: pdftotext is not available.", file=sys.stderr)
        return 1

    try:
        poppler_text = extract_poppler(pdf)
        pypdf_text, _ = extract_pypdf(pdf)
    except RuntimeError as exc:
        print(f"ATS validation failed: {exc}", file=sys.stderr)
        return 1

    headings = required_headings or list(DEFAULT_REQUIRED_HEADINGS)
    for parser_name, text in (("Poppler", poppler_text), ("pypdf", pypdf_text)):
        normalized = normalize_text(text)
        if len(normalized) < 200:
            errors.append(f"{parser_name} extracted fewer than 200 characters.")
        missing_headings = [
            heading
            for heading in headings
            if normalize_text(heading) not in normalized
        ]
        if missing_headings:
            errors.append(
                f"{parser_name} is missing headings: {', '.join(missing_headings)}."
            )
        for phrase in REQUIRED_IDENTITY_PHRASES:
            if normalize_text(phrase) not in normalized:
                errors.append(f"{parser_name} is missing identity phrase '{phrase}'.")
        for pattern in KNOWN_TOKEN_JOIN_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(
                    f"{parser_name} contains joined token '{match.group(0)}'."
                )

    ledger = career.load_ledger()
    if audience == "public":
        for leak in career.find_public_contact_leaks(
            f"{poppler_text}\n{pypdf_text}"
        ):
            errors.append(f"Public extraction exposes {leak} contact data.")

    if summary_file:
        write_summary(
            Path(summary_file),
            "ATS Extraction Validation",
            pdf,
            errors,
            {
                "Poppler characters": len(poppler_text.strip()),
                "pypdf characters": len(pypdf_text.strip()),
                "Audience": audience,
            },
        )
    if errors:
        print("ATS validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"ATS validation passed for '{pdf}' with Poppler and pypdf "
        f"({len(poppler_text.strip())}/{len(pypdf_text.strip())} characters)."
    )
    return 0


def validate_pdf(
    pdf: Path,
    audience: str,
    contact_file: str | None,
    summary_file: str | None,
) -> int:
    errors: list[str] = []
    if not pdf.exists():
        print(f"PDF validation failed: PDF not found at '{pdf}'.", file=sys.stderr)
        return 1

    try:
        from pypdf import PdfReader
    except ImportError:
        print("PDF validation failed: pypdf is not installed.", file=sys.stderr)
        return 1

    reader = PdfReader(str(pdf))
    metadata = reader.metadata or {}
    root = reader.trailer["/Root"]
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    ledger = career.load_ledger()

    if reader.is_encrypted:
        errors.append("PDF must not be encrypted.")
    if len(reader.pages) != 2:
        errors.append(f"Résumé must render as exactly two pages; found {len(reader.pages)}.")
    expected_metadata = {
        "/Author": "Alan Szmyt",
        "/Creator": "szmyty/resume",
    }
    for key, expected in expected_metadata.items():
        if str(metadata.get(key, "")) != expected:
            errors.append(f"PDF metadata {key} must be '{expected}'.")
    for key in ("/Title", "/Subject", "/Keywords"):
        if not str(metadata.get(key, "")).strip():
            errors.append(f"PDF metadata {key} must be non-empty.")
    if str(root.get("/Lang", "")) != "en-US":
        errors.append("PDF catalog language must be en-US.")
    if "/AA" in root:
        errors.append("PDF catalog must not contain additional actions.")
    names = root.get("/Names")
    if isinstance(names, dict) and any(
        unsafe_name in names for unsafe_name in ("/JavaScript", "/EmbeddedFiles")
    ):
        errors.append("PDF catalog must not contain JavaScript or embedded files.")
    if root.get("/AcroForm") is not None:
        errors.append("Résumé PDF must not contain an interactive form.")
    open_action = root.get("/OpenAction")
    if isinstance(open_action, dict) and str(open_action.get("/S", "")) not in {
        "",
        "/GoTo",
    }:
        errors.append("PDF open action must be a harmless page destination.")

    expected_filename = re.compile(r"^Alan-Szmyt-(Resume|CV)(?:-[A-Za-z0-9-]+)?\.pdf$")
    if not expected_filename.fullmatch(pdf.name):
        errors.append(f"Artifact filename is not intentional: {pdf.name}")
    if (
        audience == "public"
        and pdf.name != "Alan-Szmyt-Resume.pdf"
        and "-Public" not in pdf.stem
    ):
        errors.append("Non-baseline public artifacts must include '-Public' in the filename.")
    if audience == "application" and "-Public" in pdf.stem:
        errors.append("Application artifact filename must not include '-Public'.")

    normalized = normalize_text(text)
    approved_contact: dict[str, str] = {}
    if audience == "public":
        for leak in career.find_public_contact_leaks(text):
            errors.append(f"Public PDF exposes {leak} contact data.")
        public_location = ledger["identity"]["public_location"]
        if normalize_text(public_location) not in normalized:
            errors.append("Public PDF is missing the approved broad location.")
    else:
        if not contact_file:
            errors.append("Application PDF validation requires --contact-file.")
        else:
            try:
                contact = career.load_application_contact(Path(contact_file))
            except (FileNotFoundError, ValueError) as exc:
                errors.append(str(exc))
            else:
                approved_contact = contact
                for key in ("email", "phone", "location"):
                    value = contact.get(key)
                    if value and normalize_text(value) not in normalized:
                        errors.append(f"Application PDF is missing approved {key}.")

    page_texts = [page.extract_text() or "" for page in reader.pages]
    word_counts = [
        len(re.findall(r"\b\w[\w/+.-]*\b", page_text)) for page_text in page_texts
    ]
    total_words = sum(word_counts)
    if total_words and min(word_counts) / total_words < MIN_PAGE_WORD_SHARE:
        errors.append(
            f"Page word balance is {word_counts}; each page must carry at least "
            f"{MIN_PAGE_WORD_SHARE:.0%} of words."
        )

    occupancies = extract_vertical_occupancy(pdf)
    if len(occupancies) != len(reader.pages):
        errors.append("Unable to measure vertical occupancy for every PDF page.")
    elif min(occupancies) < MIN_PAGE_VERTICAL_OCCUPANCY:
        formatted = ", ".join(f"{value:.0%}" for value in occupancies)
        errors.append(
            f"Page vertical occupancy is {formatted}; each page must reach "
            f"{MIN_PAGE_VERTICAL_OCCUPANCY:.0%}."
        )

    font_error = validate_embedded_fonts(pdf)
    if font_error:
        errors.append(font_error)

    links = extract_pdf_links(reader)
    expected_links = {
        link["url"] for link in career.destination_links(ledger, audience)
    }
    expected_links.add(ledger["research_artifacts"]["reflector"]["concept_url"])
    if audience == "application":
        if approved_contact.get("email"):
            expected_links.add(f"mailto:{approved_contact['email']}")
        if approved_contact.get("phone"):
            expected_links.add(f"tel:{approved_contact['phone']}")
    missing_links = sorted(expected_links - links)
    if missing_links:
        errors.append(f"PDF is missing recruiter links: {', '.join(missing_links)}.")
    unexpected_links = sorted(links - expected_links)
    if unexpected_links:
        errors.append(
            f"{audience.title()} PDF contains non-allowlisted links: "
            f"{', '.join(unexpected_links)}."
        )

    if summary_file:
        write_summary(
            Path(summary_file),
            "PDF Artifact Validation",
            pdf,
            errors,
            {
                "Pages": len(reader.pages),
                "Words per page": word_counts,
                "Vertical occupancy": [f"{value:.0%}" for value in occupancies],
                "Links": len(links),
                "Audience": audience,
            },
        )
    if errors:
        print("PDF validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"PDF validation passed for '{pdf}' ({word_counts} words; "
        f"{', '.join(f'{value:.0%}' for value in occupancies)} occupancy)."
    )
    return 0


def extract_poppler(pdf: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"pdftotext exited with code {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def extract_pypdf(pdf: Path) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is not installed.") from exc
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(page_texts), page_texts


def normalize_text(value: str) -> str:
    value = value.replace("\u00ad", "")
    value = re.sub(r"-\s*\n\s*", "-", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def extract_vertical_occupancy(pdf: Path) -> list[float]:
    result = subprocess.run(
        ["pdftotext", "-bbox", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    try:
        root = ET.fromstring(result.stdout)
    except ET.ParseError:
        return []
    occupancies: list[float] = []
    for page in root.findall(".//{*}page"):
        height = float(page.attrib.get("height", "0") or 0)
        words = page.findall(".//{*}word")
        if not height or not words:
            occupancies.append(0.0)
            continue
        y_min = min(float(word.attrib["yMin"]) for word in words)
        y_max = max(float(word.attrib["yMax"]) for word in words)
        occupancies.append((y_max - y_min) / height)
    return occupancies


def validate_embedded_fonts(pdf: Path) -> str | None:
    if shutil.which("pdffonts") is None:
        return "pdffonts is not available."
    result = subprocess.run(
        ["pdffonts", str(pdf)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"pdffonts exited with code {result.returncode}."
    rows = [line.split() for line in result.stdout.splitlines()[2:] if line.strip()]
    if not rows:
        return "No PDF fonts were reported."
    if any(len(row) < 6 or row[4].casefold() != "yes" for row in rows):
        return "Every PDF font must be embedded."
    return None


def extract_pdf_links(reader: Any) -> set[str]:
    links: set[str] = set()
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                links.add(str(action["/URI"]))
    return links


def write_summary(
    summary_path: Path,
    heading: str,
    pdf: Path,
    errors: list[str],
    details: dict[str, Any],
) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if not errors else "FAIL"
    with summary_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {heading}\n\n")
        handle.write(f"- Status: {status}\n")
        handle.write(f"- PDF: `{pdf}`\n")
        for key, value in details.items():
            handle.write(f"- {key}: `{value}`\n")
        if errors:
            handle.write("- Errors:\n")
            for error in errors:
                handle.write(f"  - {error}\n")
        handle.write("\n")


def main() -> int:
    args = parse_args()
    if args.command == "validate-facts":
        return validate_facts()
    if args.command == "validate-documents":
        return validate_documents()
    if args.command == "validate-profiles":
        return validate_profiles()
    if args.command == "check-placeholders":
        return check_placeholders(args.path)
    if args.command == "validate-destinations":
        return validate_destinations(args.audience, args.online)
    if args.command == "validate-ats":
        return validate_ats(
            pdf=Path(args.pdf),
            required_headings=args.require_heading,
            summary_file=args.summary_file,
            audience=args.audience,
        )
    if args.command == "validate-pdf":
        return validate_pdf(
            pdf=Path(args.pdf),
            audience=args.audience,
            contact_file=args.contact_file,
            summary_file=args.summary_file,
        )
    raise ValueError(f"Unsupported command '{args.command}'.")


if __name__ == "__main__":
    sys.exit(main())
