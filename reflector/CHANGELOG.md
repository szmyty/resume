# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0](https://github.com/egohygiene/reflector/compare/v0.0.1...v0.1.0) (2026-05-30)


### Features

* add arXiv, build reproducibility, and TeXLive validation scripts and reports ([1b7cb8f](https://github.com/egohygiene/reflector/commit/1b7cb8f183a5b50fe93a42d2d1fc848f588e90a4))
* add canonical arXiv 00README.json publication manifest ([9476086](https://github.com/egohygiene/reflector/commit/9476086dfcdcdd0c743bb58bcc1dc33c67e382ec))
* add canonical metadata layer under metadata/ ([fe3b4d9](https://github.com/egohygiene/reflector/commit/fe3b4d95f7dfcf99488752de411db5ac152ccd7d))
* add production-grade Dev Container environment ([216d7a8](https://github.com/egohygiene/reflector/commit/216d7a8908f281b799c54e26d1f92ac3a7e11a9c))
* add publication quality pipeline with ChkTeX integration ([b494367](https://github.com/egohygiene/reflector/commit/b494367260701c20108a19d3c63b58d2a811d1df))
* add publication readiness audit report generator ([e9da3d4](https://github.com/egohygiene/reflector/commit/e9da3d49aa5c3333e93f7c36112287cfe6a51584))
* add standalone magazine PDF build pipeline ([f494ca9](https://github.com/egohygiene/reflector/commit/f494ca965aaba1af0dcb8bc9490d879326091f81))
* add synchronization validation workflow ([012064d](https://github.com/egohygiene/reflector/commit/012064d6304bbaca3337398f502f387264c3b102))
* add Taskfile-based local development workflow ([a8ae6f6](https://github.com/egohygiene/reflector/commit/a8ae6f6c5cb33fb0b447d3b4dd5b8c511194487e))
* **audits:** add holistic audit script and generate final audit report ([d04f533](https://github.com/egohygiene/reflector/commit/d04f533a4d6037c80fecc4797e9d95ee4daaf7cc))
* centralize paper title in paper/config/title.tex with canonical lowercase formatting ([38c5af2](https://github.com/egohygiene/reflector/commit/38c5af2cf2058771a9b3765be8ea66bf12816d35))
* **cli:** add sync alias and Hugging Face scaffold command ([bc660b4](https://github.com/egohygiene/reflector/commit/bc660b4fb2f6a32df2022e687960fbdc7d5fd4a2))
* create canonical figure manifest, caption registry, and figure management README ([c2d2628](https://github.com/egohygiene/reflector/commit/c2d2628ffd07a38beb54c12d21b9f790991a5a47))
* formalize deterministic figure lifecycle workflow ([488edf2](https://github.com/egohygiene/reflector/commit/488edf2c113649d975d90193bf350b8700ef6fae))
* implement REUSE/SPDX licensing infrastructure ([ccf6ad5](https://github.com/egohygiene/reflector/commit/ccf6ad51c7e89ca7d7239d27daeb0314630d2479))
* improve CITATION.cff, Zenodo metadata, and publication metadata for academic indexing ([1bf07ac](https://github.com/egohygiene/reflector/commit/1bf07ac1a8a95f0bfc89bf7aedf2312a4e4fe7ca))
* install and validate TeXLive 2025 toolchain for deterministic builds ([f242e17](https://github.com/egohygiene/reflector/commit/f242e17977342ed098fcb835febe29a990925959))
* migrate local task python workflow to uv ([cd5ca3e](https://github.com/egohygiene/reflector/commit/cd5ca3ea89b847895b8f6c16228e6873666d7c00))
* **paper:** write and finalize appendix section ([9a84481](https://github.com/egohygiene/reflector/commit/9a84481517c383dbb360eb65977f3979c9cc65d9))
* **paper:** write and finalize case_studies.tex section ([b69cf1e](https://github.com/egohygiene/reflector/commit/b69cf1e0a171305af470da2d2df6825b46ce1630))
* **paper:** write and finalize implementation_examples.tex section ([0082f78](https://github.com/egohygiene/reflector/commit/0082f78d47b595c254f89d62bd0b6f409a7a5393))
* **paper:** write mixed-initiative recursive systems section ([ac414ac](https://github.com/egohygiene/reflector/commit/ac414acbe4617c739a958e85531d55b40fe9970d))
* **paper:** write publication-ready introduction section ([c3087d9](https://github.com/egohygiene/reflector/commit/c3087d981bc968266516705a4c681af8c3da7171))
* **paper:** write reflector framework architecture section ([d722481](https://github.com/egohygiene/reflector/commit/d72248198ab68ed4b582e3bb7c84fd936908b1b5))
* publish magazine alongside reflector paper ([8428abf](https://github.com/egohygiene/reflector/commit/8428abfabf56a43dc222745a50128a4bf6601d39))
* refactor paper into publisher-agnostic publication architecture ([b68d387](https://github.com/egohygiene/reflector/commit/b68d387b7887b3f57f695b2488bffe4f2318ffd2))
* scaffold reflector-cli with CLI, schemas, synchronization, audits, orchestration, and workflows ([7a80b6c](https://github.com/egohygiene/reflector/commit/7a80b6ce39fa9918832da9cca9e47f4abcbc61fd))


### Bug Fixes

* add print PDF verification check to pages deployment workflow ([e833fdb](https://github.com/egohygiene/reflector/commit/e833fdb7963a87ad7771ca674ff3c083988df7f3))
* address code review — import os at module level, fix quote example formatting ([4752ef8](https://github.com/egohygiene/reflector/commit/4752ef833a3fe028207e9bee08ed343254700a05))
* **audits:** address code review feedback on audit-holistic.py ([ddb4653](https://github.com/egohygiene/reflector/commit/ddb4653d4bd0650515e4968734f98ed0c20ae78f))
* **cli:** normalize huggingface status table output ([3386e57](https://github.com/egohygiene/reflector/commit/3386e571eb6d4a5ffacfd02b5c89aa94b5ef8e3b))
* correct Optional type annotations and spelling in CLI and workflow runner ([6a9518d](https://github.com/egohygiene/reflector/commit/6a9518db70757336dd17dbf207a3b5b94ceb141c))
* eliminate redundant dict lookup in validate-metadata.py ([b69d76a](https://github.com/egohygiene/reflector/commit/b69d76aa6dc84afa070ab770fedfd7e95c912878))
* harden pre-commit metadata and latex hook behavior ([f48048a](https://github.com/egohygiene/reflector/commit/f48048aa6757e1ee94e0b036d8a4f275fcae5949))
* harden publication audit edge checks ([7854ba9](https://github.com/egohygiene/reflector/commit/7854ba98fb540d0d78cb22f930ca716405883bf8))
* improve metadata error reporting and latex backup cleanup ([d668380](https://github.com/egohygiene/reflector/commit/d6683809decdecc74c76c1ddf8823a636b72457a))
* improve metadata validator error handling ([fb2dd3c](https://github.com/egohygiene/reflector/commit/fb2dd3cbbf2449ad0f3580c6d53c242a2429ad7b))
* remove placeholder language from all figure captions and sync registries ([83b55ab](https://github.com/egohygiene/reflector/commit/83b55ab8b4dbe713cd2cc60b85030918caf98158))
* stabilize publication checklist semantics ([fe8b7e8](https://github.com/egohygiene/reflector/commit/fe8b7e897e4b416e4c8dca0535905dd8bea5e7d5))
* sync ci workflows and scripts to paper topology ([7d7aab2](https://github.com/egohygiene/reflector/commit/7d7aab250b52ae5d7b86a9e915bbbf9ce30ad507))
* tighten figure prompt and dimension audit checks ([39c9159](https://github.com/egohygiene/reflector/commit/39c9159571a08298d55c1ea5f1418fc410ea52d5))

## [0.0.1] - 2026-05-22

### Added

- Initial repository structure for the reflector paper and publication pipeline.
- LaTeX build and GitHub Actions automation scaffolding.
- Release metadata plumbing (`VERSION`, `CITATION.cff`, release manifests).
