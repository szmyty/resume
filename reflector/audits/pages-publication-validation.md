<!--
SPDX-FileCopyrightText: 2026 Alan Szmyt
SPDX-License-Identifier: Apache-2.0
-->

# Pages Publication URL Validation

## Validation targets

- `/reflector.pdf`
- `/reflector-magazine.pdf`
- `/reflector-magazine-print.pdf`
- `/figures/hero.png`

## Workflow enforcement

A new `Validate published publication URLs` step was added after `actions/deploy-pages@v5`.

Behavior:

- Checks site root + all publication asset URLs from `${{ steps.deployment.outputs.page_url }}`.
- Uses `curl --head --fail` with retries.
- Fails the workflow if any publication URL is unreachable.

## Local validation note

Direct outbound HTTP checks to GitHub Pages endpoints were not available from this sandbox environment (`curl` returned `000`, `web_fetch` failed). URL validation is therefore enforced in CI at deployment time.

## Expected successful outcome

A successful Pages deployment now guarantees:

- publication assets were generated and synchronized,
- publication files were present in uploaded artifact staging,
- published URLs for publication files return success.
