# publication.spec.md

## Purpose
Define a deterministic publication contract for reflector artifacts.

## Inputs
- semantic content (`paper/sections/*.tex`)
- publication metadata (`paper/00README.json` schema-compatible fields)
- figure manifest (`paper/figures/manifest.md`)

## Publication Contract
1. Assemble semantic inputs using an explicit manifest.
2. Render with a declared compiler profile.
3. Emit publication package and compatibility report.
4. Record synchronization evidence in an audit artifact.

## Determinism Constraints
- No implicit file discovery.
- No hidden renderer defaults.
- Build profile must declare TeX stack and repeat limits.

## Completion Criteria
A publication cycle is complete only when build, metadata, and audit artifacts agree on the same source revision.
