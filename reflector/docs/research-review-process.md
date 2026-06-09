<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Research Review Process

This document defines the reusable peer-review audit workflow for reflector research manuscripts.

## Authoritative Framework

Use `specs/research-paper-review.spec.md` as the review authority.

## Workflow

1. **Load inputs**
   - Primary manuscript: `paper/paper.tex` + all referenced `paper/sections/*.tex`
   - Review specification: `specs/research-paper-review.spec.md`
   - Existing audits under `audits/` for context

2. **Run structured review categories**
   - Conceptual coherence
   - Structural quality
   - Argument quality
   - Publication readiness
   - Cognitive accessibility
   - Originality and contribution
   - Systems integrity

3. **Evaluate quality dimensions**
   - Research quality (clarity, novelty, contribution, rigor, scope)
   - Technical quality (architecture consistency, terminology, figures, references, reproducibility)
   - Publication quality (organization, flow, readability, professionalism, audience fit)

4. **Simulate reviewer perspectives**
   - Academic reviewer
   - Industry reviewer
   - Software engineering reviewer
   - AI systems reviewer

5. **Produce audit artifacts**
   - `audits/research-peer-review-audit.md`
   - `audits/research-peer-review-tasks.md`

6. **Assess readiness status**
   - `ready for publication`
   - `ready with minor revisions`
   - `requires major revisions`

7. **Re-audit after revisions**
   - Re-run the same framework
   - Compare previous and current findings
   - Track movement in risks, strengths, and readiness recommendation

## Required Output Structure

### `audits/research-peer-review-audit.md`

Must include:
- Executive summary
- Strengths
- Weaknesses
- Publication risks
- Recommended changes
- Reviewer comments
- Publication readiness score
- Final readiness recommendation

### `audits/research-peer-review-tasks.md`

Must include:
- Prioritized fixes
- Severity
- Effort estimate
- Rationale

## Review Quality Rules

- Prefer high-signal findings over style nitpicks.
- Preserve authorial voice while improving rigor and clarity.
- Flag unsupported claims explicitly with file references.
- Distinguish conceptual promise from demonstrated evidence.
- Keep recommendations actionable and ordered by impact.

## Suggested Cadence

- Run once before external sharing.
- Run again before arXiv submission.
- Re-run after any major structural rewrite.
