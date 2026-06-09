# Crossref Integration and DOI Metadata Opportunities

This note maps the DOI and scholarly metadata ecosystem around reflector and identifies potential future integration options without implementing automation yet.

## Short Summary

- **Crossref** is a DOI Registration Agency (RA) focused on publisher-registered scholarly outputs and rich citation-linked metadata.
- **Zenodo** is a repository that mints DOIs through **DataCite** for deposited artifacts (software, datasets, releases, preprints, reports).
- Crossref and DataCite both register DOIs under the DOI Foundation, but they serve different operational roles and communities.
- reflector can benefit from **read-only metadata enrichment** first (lookup, validation, synchronization support), with write/registration automation deferred.

## DOI Infrastructure: Crossref vs Zenodo/DataCite

### How Crossref DOIs are issued

1. An organization becomes a Crossref member (typically a publisher, society, institution, or platform acting in publisher roles).
2. The member receives DOI prefix management capability via Crossref participation.
3. The member deposits metadata (title, contributors, references, funding, licenses, updates, etc.) to Crossref.
4. Crossref registers the DOI and exposes metadata via APIs and indexing feeds.

### Who can register through Crossref

- Not individual researchers directly in most normal workflows.
- Primarily organizations with publishing responsibility and long-term metadata stewardship.

### Is Crossref primarily for publishers?

- Yes. Crossref is publisher- and registration-workflow-centric.
- It emphasizes persistent scholarly record linking, references, citation relationships, corrections/retractions, and metadata quality obligations.

### How Zenodo interacts with Crossref/DataCite

- Zenodo mints DOIs through **DataCite**, not Crossref.
- Typical software/research artifact releases on Zenodo therefore become DataCite DOI records.
- Downstream systems may ingest both Crossref and DataCite records and reconcile them in broader discovery/citation graphs.

## Comparison Table

| System | Primary role | DOI role | Who controls records | Typical content | API/metadata strengths | Key constraints |
| --- | --- | --- | --- | --- | --- | --- |
| Crossref | Scholarly publishing metadata and linking network | DOI RA (publisher-centric registration) | Publishers/members | Journal articles, proceedings, books, reports, some preprints | Rich references, citation relations, funder/license metadata, update events | Membership/deposit workflow; not a direct self-serve researcher repository |
| Zenodo | Open repository for research outputs | Uses DataCite DOI minting | Depositors (researchers/projects) + Zenodo platform policies | Software releases, datasets, preprints, reports, artifacts | Simple deposit workflow, versioning, GitHub release integration | Metadata depth varies by depositor quality; repository-centric model |
| DataCite | DOI RA for research data/software/institutional repositories | DOI RA (repository/institution-centric registration) | Repositories/institutions/providers | Datasets, software, non-traditional research objects | PID Graph, repository interoperability, broad research object coverage | Record quality and citation linking can vary by source |
| arXiv | Preprint server | No native DOI minting required for all records; may include external DOIs | arXiv + authors | Preprints | High adoption and discoverability in many fields | DOI coverage is partial/linked; metadata may differ from publisher-of-record |
| ORCID | Researcher identity registry | Not a DOI RA | Researchers + trusted-party updates | Person records, works links, affiliations, grants | Persistent author IDs, disambiguation, cross-system linkage | Depends on permissions and source trust; not a citation index |

## Metadata Propagation Map (Practical)

- **Zenodo/DataCite → OpenAIRE/OpenAlex/others**: repository records and DOI metadata are harvested and integrated into open knowledge graphs.
- **Crossref → OpenAlex/Semantic Scholar/Google Scholar (indirectly)**: large share of publisher metadata and references become discovery/citation inputs.
- **ORCID ↔ Crossref/DataCite**: ORCID records can be updated by trusted organizations and can also be author-maintained; DOI-based works act as linking anchors.
- **arXiv ↔ DOI ecosystem**: preprints may later connect to DOI-bearing versions of record; aggregators attempt matching.

Practical implication: propagation is **asynchronous, lossy, and source-dependent**. No single service guarantees perfect, immediate global synchronization.

## Crossref API Opportunities for reflector (Read-Only First)

- **Works lookup** (by DOI, metadata query) for canonical bibliographic enrichment.
- **References/citation-linked metadata** for bibliography normalization and validation.
- **Funder/license/type metadata** for policy-aware publication manifests.
- **Event/relationship metadata** (updates, corrections where available) for drift monitoring.

Useful endpoints to track:

- `https://api.crossref.org/works/{doi}`
- `https://api.crossref.org/works?query=...`
- `https://api.crossref.org/members/{id}`
- `https://api.crossref.org/journals/{issn}`

Companion ecosystem endpoints:

- DataCite REST API (`https://api.datacite.org/dois/...`)
- ORCID public API (`https://pub.orcid.org/`)
- OpenAlex (`https://api.openalex.org/works/...`)
- OpenAIRE Graph APIs
- Semantic Scholar Graph API

## Potential Future reflector Integrations (Not Implemented)

- `reflector references sync` command that resolves DOI metadata from Crossref/DataCite/OpenAlex and normalizes local references.
- DOI auto-enrichment for incomplete bibliography entries.
- Reference validation (DOI format, resolver reachability, metadata consistency checks).
- Citation graph snapshots for literature drift and dependency mapping.
- Recursive synchronization loops that refresh publication manifests with bounded, review-first workflows.

## Automation Opportunities

- Scheduled metadata refresh jobs with deterministic diff output.
- Confidence scoring across multiple metadata sources (Crossref/DataCite/OpenAlex/arXiv).
- Author disambiguation augmentation via ORCID IDs when available.
- Bibliography linting that flags missing DOI, title mismatch, year mismatch, or unresolved references.

## Risks, Limitations, and Publisher Constraints

- **Publisher boundary**: direct Crossref DOI registration is generally an organizational publisher workflow, not an individual CLI action.
- **Metadata inconsistency**: source systems can disagree on titles, author ordering, dates, and work type.
- **Coverage gaps**: preprints, software, and niche outputs may appear in DataCite/arXiv but not Crossref (or vice versa).
- **Rate limits and service policies**: API usage requires respectful client behavior and may need caching/backoff.
- **Identity/permission constraints**: ORCID write/update flows require explicit trust scopes and user/org permissions.
- **False precision risk**: fully automatic synchronization can introduce silent metadata drift if not review-gated.

## Recommendation for reflector Publication Strategy

1. Keep current publication flow unchanged.
2. Add optional, read-only metadata enrichment and validation before any write/publish automation.
3. Prefer a multi-source strategy (Crossref + DataCite + OpenAlex + local truth) with explicit conflict reporting.
4. Treat DOI registration/deposit actions as human-approved governance milestones rather than automatic background steps.
