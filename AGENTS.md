# AGENTS.md — Public résumé repository

This repository builds and publishes public résumé artifacts. The private
career repository is the authority for facts and evidence as they are reviewed;
cataloged sources alone are not approved claims. `content/career.json` is the
validated, self-contained input to this renderer. Existing public claims
remain the starting baseline, not a new evidence review or migration.

Before changing this repository, read `.github/copilot-instructions.md`,
`specs/resume.spec.md`, `specs/governance.md`, `README.md`, and then
`CONTINUITY.md`. Verify the continuity snapshot against the current branch,
issues, pull requests, CI, and Pages state. New or revised factual claims need
source review and owner approval for the exact projection before they enter
this public repo.

Keep private evidence, private source URLs and paths, contact overlays,
application PDFs, and application state out of public Git and published
artifacts. Public CI and rendering must work from committed public inputs
without private repository access. Follow the documented privacy and quality
gates and do not merge or publish a proposed change on the authority of a
continuity file alone.
