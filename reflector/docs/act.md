# Local GitHub Actions Testing with `act`

This repository includes a canonical `.actrc` for deterministic local workflow testing with [`act`](https://github.com/nektos/act).

## Prerequisites

- Docker Engine (or Docker Desktop) running locally
- `act` installed and available in `PATH`

Install `act`:

```bash
# macOS (Homebrew)
brew install act

# Linux (download script from upstream)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

## Canonical configuration

The root [`/.actrc`](../.actrc) pins default behavior for local execution:

- workflow graph output (`--graph`)
- deterministic local cache paths under `./.cache/act/`
- repository root execution directory (`--directory .`)
- JSON log output (`--json`)
- explicit `ubuntu-latest` image mapping (`--platform ubuntu-latest=node:16-buster-slim`)
- disabled cache server (`--no-cache-server`)

Use `act` from repository root so `.actrc` is picked up automatically.

## Quick start

```bash
# List available jobs
act --list

# Run synchronization workflow jobs for pull_request event
act pull_request -W .github/workflows/synchronization.yml

# Run the paper build job via workflow_dispatch
act workflow_dispatch -W .github/workflows/build-paper.yml -j build
```

## Workflow compatibility boundaries

Recommended local-first workflows:

- `.github/workflows/synchronization.yml`
- `.github/workflows/build-paper.yml`
- `.github/workflows/commitlint.yml`
- `.github/workflows/reuse.yml`

Workflows that may require cloud-only GitHub context, repository permissions, or deployment primitives:

- `.github/workflows/pages.yml` (GitHub Pages deployment)
- `.github/workflows/release-paper.yml` (release publishing)
- `.github/workflows/release-please.yml` (release automation)

## Troubleshooting

### Docker daemon not running

Start Docker and retry:

```bash
docker info
act --list
```

### Architecture/image mismatch

Override image mapping for a single run:

```bash
act pull_request -W .github/workflows/synchronization.yml -P ubuntu-latest=node:18-bullseye
```

### Missing tooling inside containers

Local `act` containers may differ from hosted runners. Prefer the synchronization workflow for fast local feedback, then confirm full parity in GitHub-hosted CI for release and deployment workflows.
