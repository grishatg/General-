# Precision Engineering: Implementation Reference

## PR Size Enforcement Tools

### GitHub Actions (copy-paste)
```yaml
# .github/workflows/pr-size.yml
name: PR Size Check
on: [pull_request]
jobs:
  size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Check PR size
        run: |
          ADDITIONS=$(git diff --shortstat origin/${{ github.base_ref }}...HEAD | awk '{print $4}')
          DELETIONS=$(git diff --shortstat origin/${{ github.base_ref }}...HEAD | awk '{print $6}')
          TOTAL=$((ADDITIONS + DELETIONS))
          echo "PR size: +${ADDITIONS} -${DELETIONS} = ${TOTAL} LOC changed"
          if [ "$TOTAL" -gt 400 ]; then
            echo "::error::PR exceeds 400 LOC limit (${TOTAL} LOC). Split into smaller PRs."
            exit 1
          elif [ "$TOTAL" -gt 300 ]; then
            echo "::warning::PR is above 300 LOC target (${TOTAL} LOC). Consider splitting."
          fi
```

## Coverage Gate Tools

### Node.js / Jest
```json
// jest.config.js (add to existing)
{
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    },
    "each": {
      "lines": 70
    }
  }
}
```

### Python / pytest
```ini
# pytest.ini
[pytest]
addopts = --cov=src --cov-fail-under=80 --cov-report=term-missing
```

### Go
```bash
# In CI
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total | awk '{if ($3+0 < 80) exit 1}'
```

## Pre-commit Hook Stack

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff          # Python lint
      - id: ruff-format   # Python format
  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: npx eslint --fix
        language: system
        types: [javascript, typescript]
        pass_filenames: true
      - id: tsc
        name: TypeScript check
        entry: npx tsc --noEmit
        language: system
        pass_filenames: false
```

## SAST Tools (Security Static Analysis)

| Language | Tool | Notes |
|---|---|---|
| Any | Semgrep (community rules) | Free; broad rule coverage |
| JS/TS | ESLint security plugins | eslint-plugin-security |
| Python | Bandit | Focused on Python security patterns |
| Java | SpotBugs + FindSecBugs | Widely adopted |
| Go | gosec | Official Go security analyzer |
| Any | TruffleHog | Secret detection in git history |
| Any | CodeQL | GitHub-native; deep analysis |

## Mutation Testing (High-Risk Paths)

Run mutation testing on auth, payment, and data-deletion logic only. Full-suite mutation testing is too slow for CI.

```bash
# JavaScript/TypeScript
npx stryker run

# Python
pip install mutmut
mutmut run --paths-to-mutate src/auth/ src/billing/ src/data/
mutmut results

# Java
mvn org.pitest:pitest-maven:mutationCoverage
```

## Defect Density Benchmarks (Industry 2026)

| Team Maturity | Bugs per KLOC | Key Practices |
|---|---|---|
| Elite | 0.1–0.5 | TDD, mutation testing, pair programming |
| High | 0.5–1.0 | TDD, automated gates, structured review |
| Medium | 1.0–2.0 | Automated tests, code review |
| Low | 2.0–5.0 | Manual testing, ad-hoc review |
| Industry average | 2–3 | — |

## Code Review Checklist (Reviewer)

**Before starting review (< 2 min)**:
- [ ] PR < 300 LOC? If not, ask author to split.
- [ ] CI passing? If not, author fixes first.
- [ ] Description explains the "why"?

**During review (focus areas)**:
- [ ] Business logic matches the spec / ticket
- [ ] Edge cases handled (null, empty, boundary values, concurrent access)
- [ ] Error handling explicit (no bare `except`, no silent failures)
- [ ] No hardcoded values (secrets, URLs, timeouts)
- [ ] No N+1 queries or obvious performance landmines
- [ ] Tests cover the happy path AND at least one failure path

**After review**:
- [ ] Findings categorized by severity (critical / high / medium / low / nit)
- [ ] At least one positive comment (psychologically important for team health)
- [ ] Review session < 60 min? If not, end and continue later.

## Smart Test Selection Tools

| Tool | Language | Notes |
|---|---|---|
| Launchable | Any | ML-based; most sophisticated |
| Trunk Flaky Tests | Any | Also catches and quarantines flaky tests |
| BuildPulse | Any | Flaky test detection + impact analysis |
| pytest-testmon | Python | File-change-based selection |
| Jest `--findRelatedTests` | JS/TS | Native, simple, file-based |
| Bazel + remote cache | Any | Build graph-based; scales to monorepos |
