---
description: Perform a severity-gated code review of the current PR diff or specified file range. Findings are categorized as Critical, High, Medium, Low, or Nit. Critical and High findings must be resolved before merge. Use when you want a systematic review of changed code.
argument-hint: "[optional: specific files or 'staged' or 'last-commit']"
allowed-tools: Bash,Read,Grep,Glob
---

# PR Review

Perform a systematic, severity-gated code review of $ARGUMENTS.

## Step 1: Get the Diff

Determine what to review:

```bash
# If reviewing full PR vs main:
git diff main...HEAD

# If reviewing staged changes:
git diff --staged

# If reviewing last commit:
git diff HEAD~1 HEAD

# If a path was specified in $ARGUMENTS:
git diff main...HEAD -- $ARGUMENTS
```

Also run:
```bash
git diff --stat main...HEAD   # Get file count and LOC summary
```

Flag immediately if total LOC changed > 400 — this PR should be split.

## Step 2: Context Gathering

For each changed file, understand its purpose:
- Read the file to understand the surrounding context of changed lines
- Check if there are corresponding test files for changed logic
- Identify what type of change this is: bug fix / new feature / refactor / config

## Step 3: Review Pass

Examine the diff with these lenses, in order:

### 3a. Correctness (highest priority)
- Does the logic do what the PR description says it should?
- Are there off-by-one errors, race conditions, or incorrect conditionals?
- Are all code paths exercised? What happens in the failure/empty/null case?
- Is state mutated unexpectedly? Any shared mutable state without synchronization?

### 3b. Security
- Is user input validated before use? (injection, XSS, path traversal)
- Are auth/permission checks present on every endpoint that needs them?
- Are secrets handled via env vars / secrets manager, not hardcoded?
- Is sensitive data logged or exposed in error messages?

### 3c. Error Handling
- Are errors caught at the right level (not too broadly, not too narrowly)?
- Are errors surfaced to callers with useful context, or swallowed silently?
- Are timeouts set on all outbound network calls?
- Does the system fail gracefully under partial failure?

### 3d. Performance
- Are there N+1 query patterns (loop containing a DB/API call)?
- Is pagination present for queries that could return large result sets?
- Are expensive operations cached where appropriate?
- Any blocking I/O on a hot path that should be async?

### 3e. Test Quality
- Do new tests exist for the new/changed behavior?
- Do tests cover at least one failure/edge case, not just the happy path?
- Are tests isolated (no shared state between tests)?
- Are mocks used appropriately (not testing the mock, testing the behavior)?

### 3f. Maintainability
- Are variable and function names clear and descriptive?
- Is there dead code, unused imports, or commented-out code to clean up?
- Is complexity higher than necessary (could this be simpler)?
- Is there a comment explaining the "why" for non-obvious decisions?

## Step 4: Categorize Findings

Use this taxonomy consistently:

| Severity | Definition | Merge impact |
|---|---|---|
| **Critical** | Security vulnerability, data loss risk, or definitively broken behavior | BLOCK — must fix before merge |
| **High** | Likely bug or design flaw that will cause problems in production | BLOCK — must discuss and fix or justify |
| **Medium** | Non-obvious issue; low probability or recoverable impact | RECOMMEND fix; author's call |
| **Low** | Minor improvement; style or naming issue | NON-BLOCKING; small suggestion |
| **Nit** | Trivial preference; no correctness or clarity impact | NON-BLOCKING; prefaced with "nit:" |
| **Praise** | Genuinely good code worth calling out | ALWAYS include at least one |

## Step 5: Report

```
PR REVIEW — [branch name] → [base branch]
Files changed: [N] · LOC: +[X] -[Y]
Review time: [N] min
[SIZE WARNING if > 300 LOC]

── CRITICAL (must fix) ─────────────────────────
[0 findings] ✅

── HIGH (should fix) ───────────────────────────
[1] src/auth/middleware.ts:47
    Missing permission check on DELETE /api/users/:id endpoint.
    Any authenticated user can delete any other user's account.
    Fix: Add `requireRole('admin')` middleware before handler.

── MEDIUM (recommended) ────────────────────────
[1] src/services/report.ts:112
    N+1 query: `getUser()` called inside `reports.map()`.
    Move to a single `getUsersByIds()` call before the loop.

── LOW ─────────────────────────────────────────
[1] src/utils/format.ts:23
    `formatDate` would be clearer as `formatISODate` given it always
    returns ISO 8601 format.

── PRAISE ──────────────────────────────────────
    The pagination implementation in src/api/list.ts is clean and
    handles edge cases (empty page, last page) correctly. Good work.

VERDICT: BLOCKED — 1 High finding must be addressed before merge.
```
