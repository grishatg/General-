---
name: precision-engineering
description: Apply precision engineering practices to software projects. Use when reviewing code, planning PRs, setting up testing strategies, configuring CI quality gates, or discussing code review practices. Triggers include: 'code review', 'PR size', 'test coverage', 'TDD', 'quality gate', 'defensive programming', 'regression', 'lint', 'code quality', 'spec-driven'. Do NOT use for deployment, release management, or developer workflow (those are handled by product-delivery and dev-productivity skills).
license: MIT
---

# Precision Engineering

Concrete practices that reduce defect rates in large, long-lived codebases. All recommendations are grounded in 2026 benchmarks.

## PR Size: The Single Highest-Leverage Lever

**Target**: ≤ 300 LOC per PR. Hard ceiling: 400 LOC.

Why it matters: Defect detection rate drops 66–75% once a PR exceeds 400 LOC. Reviewer attention saturates at ~1 hour; sessions beyond that degrade quality regardless of size.

Enforcement:
- Add a PR size check to CI (fail if diff > 400 LOC, warn if > 300)
- Split by layer (API → service → data), not by feature
- If a PR must be large (e.g., schema migration), use stacked PRs with a base branch
- **Review pickup target**: < 2 hours; **merge target (75th percentile)**: < 6 hours

## Automate Objective Checks Before Human Review

Remove ~40% of review comments from human reviewers by automating everything mechanical:

```
Pre-commit (local, fast):
  lint         → ESLint / Pylint / Black / Prettier
  formatting   → enforced, not suggested
  secrets scan → detect-secrets or TruffleHog (pre-push)

CI (blocking gates):
  SAST         → static security analysis (Semgrep, CodeQL)
  type check   → tsc --strict, mypy --strict
  dead code    → no unreachable functions in PRs
  test suite   → all tests pass
  coverage     → fail if < 80% on changed files
```

Human review then focuses exclusively on: design decisions, business logic correctness, edge cases, architectural impact.

## TDD and Coverage

**Minimum gate**: 80% code coverage on changed files. This is the industry baseline, not a ceiling.

TDD workflow:
1. Write a failing test that expresses the spec
2. Write minimum code to make it pass
3. Refactor (green bar must stay)

Outcomes when followed: 40% reduction in debugging time, 30% reduction in defect density vs non-TDD (industry studies).

**Coverage nuance**: 100% coverage with 0% correctness is possible. Use mutation testing (Stryker, mutmut) for high-risk paths to verify tests actually catch real bugs. Don't gate on mutation score — just run it on auth/payment/data-deletion paths.

**Defect density benchmarks**:
- Elite teams: 0.5–1.0 bugs per KLOC
- Industry average: 2–3 bugs per KLOC
- Achievable with TDD + automated gates: < 1.0 bugs per KLOC

## Defensive Programming (At Boundaries Only)

Validate at system boundaries — user input, external APIs, file reads, network responses. Trust internal function contracts.

```
Boundary rule: validate here
  - HTTP request body/params
  - CLI argument parsing
  - External API responses (JSON schema check)
  - File/database reads at app startup

Trust here (no extra validation):
  - Internal function calls between modules you own
  - Framework guarantees (ORM result types, typed language contracts)
```

Defensive pattern checklist:
- [ ] Null/undefined guards at every external data entry point
- [ ] Explicit error types (not generic `Error`); never swallow exceptions silently
- [ ] Immutable data structures for shared state where possible
- [ ] Fail fast on bad config at startup (not at runtime)
- [ ] Timeouts on all outbound network calls

## Code Review Protocol

**Tiered reviewer model** (standard at Google, Meta, Linux kernel):

| Finding Severity | Reviewer Level | Action |
|---|---|---|
| Critical / Security | Senior + 2nd reviewer | Block merge; must fix |
| High / Design | Senior | Block merge; must discuss |
| Medium / Logic | Any | Block merge; should fix |
| Low / Nit | Any | Non-blocking; author discretion |
| Suggestion | Any | Non-blocking; informational |

Reviewer fatigue rule: Cap review sessions at 60 minutes. Schedule second session rather than extending. After 1 hour, miss rate increases sharply.

## Smart Test Selection for Large Codebases

Running the full test suite on every PR is unsustainable past ~5,000 tests. Modern smart-selection tools (Trunk, Launchable, BuildPulse) map code changes to affected test files and run only relevant tests.

Result: Regression suite execution from hours → minutes with same defect-detection confidence.

Target metrics:
- **CI feedback time**: < 10 minutes for PR builds
- **Full suite**: Nightly, not per-PR
- **Flaky test rate**: < 1% (fix immediately; flaky tests destroy trust in the suite)

## Reference

See [practices.md](references/practices.md) for implementation checklists, tool recommendations, and benchmark sources.
