# Licensing

This document describes the REUSE/SPDX licensing infrastructure used by the
reflector repository.

---

## License

reflector is licensed under the **Apache License, Version 2.0**.

- **SPDX identifier**: `Apache-2.0`
- **License text**: [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt)
- **Canonical root**: [`LICENSE`](../LICENSE)

---

## REUSE Compliance

This repository follows the [REUSE specification](https://reuse.software/spec/) for
machine-readable, deterministic copyright and license metadata.

REUSE ensures that every file in the repository carries:
- a **copyright notice** (`SPDX-FileCopyrightText`)
- a **license identifier** (`SPDX-License-Identifier`)

This metadata is either embedded as inline headers within source files or declared
via [`REUSE.toml`](../REUSE.toml) using glob-pattern annotations.

---

## SPDX Header Conventions

### Python

```python
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
```

### Shell

```bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
```

### YAML / GitHub Actions

```yaml
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
```

### LaTeX / TeX

```tex
% SPDX-FileCopyrightText: 2026 Alan Szmyt
% SPDX-License-Identifier: Apache-2.0
```

### Markdown (when inline headers are used)

```html
<!--
SPDX-FileCopyrightText: 2026 Alan Szmyt
SPDX-License-Identifier: Apache-2.0
-->
```

---

## File Coverage Strategy

| File Type | Coverage Method |
|-----------|----------------|
| Python (`.py`) | Inline SPDX header |
| Shell (`.sh`) | Inline SPDX header |
| GitHub Actions (`.yml`) | Inline SPDX header |
| LaTeX (`.tex`, `.sty`) | Inline SPDX header (key files) |
| Markdown (`.md`) | `REUSE.toml` annotation |
| JSON (`.json`) | `REUSE.toml` annotation (JSON has no comment syntax) |
| TOML (`.toml`) | `REUSE.toml` annotation |
| YAML config (`.yaml`) | `REUSE.toml` annotation |
| Binary assets (`.png`, etc.) | `REUSE.toml` annotation |
| License texts | `LICENSES/` directory (excluded from annotation) |

---

## REUSE.toml

The [`REUSE.toml`](../REUSE.toml) file at the repository root declares copyright and
license metadata for all files via glob-pattern annotations. This is the primary
fallback for files where inline SPDX headers are impractical (e.g., JSON, binary
assets, generated files).

See the [REUSE 3.0 specification](https://reuse.software/spec/) for full details.

---

## LICENSES Directory

The [`LICENSES/`](../LICENSES/) directory contains the canonical SPDX license text:

- `Apache-2.0.txt` — Apache License, Version 2.0

This directory must contain the full text of every license referenced by an
`SPDX-License-Identifier` field in the repository.

---

## Automated Validation

REUSE compliance is validated automatically via GitHub Actions on every push and
pull request targeting the `main` branch:

- **Workflow**: [`.github/workflows/reuse.yml`](../.github/workflows/reuse.yml)
- **Action**: [`fsfe/reuse-action@v5`](https://github.com/fsfe/reuse-action)
- **Check**: Runs `reuse lint` to verify that all files are covered

---

## Contributing

When adding new files to the repository:

1. **Source files** (Python, shell, YAML workflows): Add an inline SPDX header at
   the top of the file using the appropriate comment syntax.

2. **Other files** (JSON, Markdown, binary): Ensure the file matches an existing
   glob pattern in `REUSE.toml`, or add a new annotation block.

3. **New license texts**: If a file uses a different SPDX identifier, add the
   corresponding license text to the `LICENSES/` directory.

The automated REUSE workflow will report any uncovered files on pull requests.

---

## References

- [REUSE specification](https://reuse.software/spec/)
- [SPDX license list](https://spdx.org/licenses/)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- [fsfe/reuse-action](https://github.com/fsfe/reuse-action)
