# Precision Delivery Plugin

Ship software with extreme accuracy. Every component in this plugin is grounded in 2026 engineering benchmarks.

## Skills

### `precision-engineering`
Enforces the practices that actually reduce defect rates:
- PR size limit ≤ 300 LOC (defect detection drops 66–75% beyond 400 LOC)
- Automate ALL objective checks before human review (removes ~40% of review comments)
- TDD + 80% coverage gate (40% reduction in debugging time)
- Defensive input validation at system boundaries only
- Smart test selection for large codebases (reduces suite from hours to minutes)

### `product-delivery`
Gate every release against DORA elite targets:
- Definition of Done as CI-enforced checklist (rework rate target < 10%)
- Feature flags (release risk) vs canary deployments 1%→5%→25%→100% (infrastructure risk)
- Auto-rollback on SLO breach (MTTD < 5 min, rollback < 10 min)
- DORA targets: deploy frequency > 4×/day, lead time < 1 day, MTTR < 30 min, CFR < 15%

### `dev-productivity`
Eliminate toil and protect flow state:
- Google SRE toil test: manual + repetitive + automatable + no lasting value = automate it
- Inner-loop feedback < 2 min (code → build → test result)
- Outer loop: IaC, CI/CD, monitoring standardized
- Async-first living docs; 35% faster delivery (McKinsey 2025)

## Commands

### `/precision-delivery:ship-check`
Full pre-ship DoD gate. Runs: tests → lint → security scan → code review → generates release checklist.

### `/precision-delivery:pr-review`
Severity-gated diff review. Blocking findings (critical/high) must be fixed before merge.

## Agents

### `precision-reviewer`
Adversarial correctness reviewer. Tries to find bugs, race conditions, security holes, and spec violations in the diff.

## Hooks

- `PreToolUse[Bash]`: Warns before destructive shell commands (`rm -rf`, `DROP TABLE`, `git push --force`)
- `Stop`: Logs a session summary of all files changed
