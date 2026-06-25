---
description: Run a complete pre-ship Definition of Done gate. Executes tests, lint, security scan, and code review in sequence. Fails fast on any blocking finding. Use before merging a PR or cutting a release.
argument-hint: "[optional: path or component to focus on]"
allowed-tools: Bash,Read,Grep,Glob
---

# Ship Check

Run a complete Definition of Done gate before shipping $ARGUMENTS.

## Execution Order

Work through each gate in sequence. Stop and report immediately on any blocking failure — do not continue to subsequent steps if a critical gate fails.

### Gate 1: Tests
Run the project's test suite. Check for a test script in package.json, Makefile, pytest.ini, or go.mod.

```
npm test              # Node
pytest --tb=short     # Python
go test ./...         # Go
./gradlew test        # Java
```

Report:
- Pass/fail status
- Number of tests run
- Any failing test names and their error messages
- Coverage percentage (if available) — flag if < 80%

### Gate 2: Lint & Type Check
Run all static analysis checks.

```
npm run lint && npx tsc --noEmit      # JS/TS
ruff check . && mypy .                # Python
go vet ./... && staticcheck ./...     # Go
```

Report:
- Any errors (block) vs warnings (flag but don't block)
- File and line number for each finding

### Gate 3: Security Scan
Check for secrets, SAST issues, and known vulnerability patterns.

```
# Secrets (run in repo root)
git log --oneline -20   # Recent commits to scan
grep -rn "password\s*=\|api_key\s*=\|secret\s*=\|token\s*=" --include="*.env" --include="*.config.*" .

# Dependency vulnerabilities
npm audit --audit-level=high    # Node
pip-audit                       # Python
govulncheck ./...               # Go
```

Report:
- Any secrets found in tracked files (BLOCKING — must fix before shipping)
- High/critical dependency vulnerabilities (BLOCKING)
- Medium vulnerabilities (flag, non-blocking)

### Gate 4: Code Review
Review the current diff for quality issues.

Use the `precision-engineering` skill's code review protocol:
- Get the diff: `git diff main...HEAD` or `git diff HEAD~1`
- Review for: logic correctness, edge cases, error handling, null safety, performance issues
- Categorize each finding by severity: Critical / High / Medium / Low / Nit

Report:
- All Critical and High findings (BLOCKING)
- Medium findings (recommended fix)
- Summary of LOC changed, files touched

### Gate 5: DoD Checklist

Confirm each item before declaring ship-ready:

- [ ] All tests pass
- [ ] Code coverage ≥ 80% on changed files
- [ ] No lint errors, no type errors
- [ ] No new secrets in tracked files
- [ ] No new high/critical security vulnerabilities
- [ ] No Critical or High code review findings (or all are addressed)
- [ ] PR description explains the "why" (not just the "what")
- [ ] Documentation updated if public API or behavior changed
- [ ] Rollback plan exists (feature flag, revert strategy, or migration reversal documented)

## Final Report Format

```
SHIP CHECK RESULTS — [timestamp]
Focus: [path/component or "full repo"]

Gate 1: Tests        ✅ PASS  (142 passed, 0 failed, 84% coverage)
Gate 2: Lint         ✅ PASS  (0 errors, 2 warnings noted)
Gate 3: Security     ✅ PASS  (0 secrets, 0 high vulns, 3 medium noted)
Gate 4: Code Review  ⚠️ WARN  (0 Critical, 1 High [described below], 3 Medium)
Gate 5: DoD Checklist ❌ FAIL (2 items unchecked)

VERDICT: [SHIP-READY / BLOCKED — reason]

Blocking issues:
1. [Specific finding with file:line]

Recommended (non-blocking):
1. [Finding]
```
