---
name: dev-productivity
description: Improve developer productivity and eliminate engineering toil. Use when auditing workflows, identifying bottlenecks, setting up automation, designing async processes, or discussing developer experience. Triggers include: 'toil', 'automation', 'developer experience', 'devex', 'DX', 'inner loop', 'build time', 'slow CI', 'flow state', 'async workflow', 'documentation standards', 'productivity', 'bottleneck', 'friction', 'efficiency'. Do NOT use for code quality (precision-engineering) or release strategy (product-delivery).
license: MIT
---

# Developer Productivity

Protect flow state. Eliminate toil. 35% faster delivery and 28% less coordination time are achievable with the practices here (McKinsey Engineering Productivity 2025).

## The Google SRE Toil Test

Toil is work that is: manual, repetitive, automatable, reactive (not proactive), and provides no lasting value. Automate it **only if the time saved exceeds the time invested in the automation**.

Apply this test to every recurring task:

| Question | If YES → automate candidate |
|---|---|
| Does a human have to do this manually each time? | Yes |
| Does it happen on a predictable schedule or trigger? | Yes |
| Could software do it without human judgment? | Yes |
| Does it interrupt proactive/creative work? | Yes |
| Does it scale with infrastructure (not value) growth? | Yes |

**Cost-benefit rule**: Track the hours this task consumes per quarter. If automation takes > 3× that to build and maintain, defer it.

**Highest-ROI automation targets** (by category):
- Formatting/linting → pre-commit hooks (1-time setup, infinite return)
- Secret scanning → pre-push hook (prevents costly security incidents)
- Release notes → auto-generated from conventional commits
- On-call handoff → automated runbook + paging from monitoring, not Slack
- Dependency updates → Dependabot / Renovate (not manual PRs)

## Inner Loop vs Outer Loop

**Inner loop** = the tight cycle a developer lives in: write code → build → run tests → see result.

**Target**: < 2 minutes from code change to test result. Beyond 2 minutes, developers switch context; context switching costs 15–25 minutes of recovered focus per interruption.

Inner loop optimizations:
- Local dev env parity with prod (Docker Compose or devcontainers)
- Watch-mode test runners (Jest `--watch`, pytest-watch, Go `air`)
- Incremental builds (esbuild, Turbopack, Vite, Bazel remote cache)
- Fast unit tests < 100ms each (mock I/O; only integration tests hit the DB)
- Kill flaky tests immediately — they destroy trust in the suite

**Outer loop** = the pipeline beyond local: CI → staging → production.

**Target**: CI feedback in < 10 minutes. Lead time (commit → prod) < 1 day.

Outer loop optimizations:
- Parallelize CI jobs (test sharding, parallel matrix builds)
- Cache dependencies and build artifacts aggressively
- Run only affected tests on PRs (smart test selection)
- Fail fast: security/type-check first, expensive tests last
- IaC for all environments (no manual server config, ever)

## Automation Patterns (Smart, Not Sprawl)

Automation should reduce cognitive load, not increase it through tool sprawl.

**1-2 core tools per category** outperform 5-6 overlapping platforms:

| Category | 1–2 Recommended | Anti-pattern |
|---|---|---|
| CI/CD | GitHub Actions + ArgoCD (or Buildkite) | 4 different CI systems |
| IaC | Terraform or Pulumi | CloudFormation + CDK + Helm + Ansible |
| Monitoring | Datadog or Grafana+Prometheus | 6 APM tools |
| Secret mgmt | 1Password Secrets Automation or Vault | Secrets in .env files |
| Dependency updates | Renovate (single tool covers all langs) | Per-language bots |

**Pre-commit hook stack** (copy-paste ready):
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks: [trailing-whitespace, end-of-file-fixer, check-yaml, check-json]
  - repo: https://github.com/Yelp/detect-secrets
    hooks: [detect-secrets]
  - repo: local
    hooks:
      - id: lint
        name: lint
        entry: npm run lint
        language: system
        pass_filenames: false
```

## Async-First Documentation Standard

Async workflows reduce coordination overhead. But async fails without written standards.

**Five living documents every engineering team needs**:

1. **Communication protocol**: response-time SLAs (Slack DM: 2h; channel mention: 4h; email: 24h), escalation paths, when to create a meeting vs write a doc
2. **Decision log** (ADR — Architecture Decision Records): every major technical decision with its context, options considered, and rationale. Format: `/docs/adr/NNN-title.md`
3. **Runbook library**: one runbook per recurring incident type. Never oncall paging without a linked runbook.
4. **Architecture diagram**: current-state data flow, service dependencies, external integrations. Updated on every significant change.
5. **On-call handbook**: what each alert means, how to triage, who to escalate to, known false positives.

**Living doc principle**: Written once, updated collaboratively. Not annual all-hands binders. Co-located with the code they describe (in the repo, not a separate wiki that drifts).

## Developer Velocity Metrics

Track these to baseline your team and measure improvements:

| Metric | Target (Elite) | Target (Good) | How to measure |
|---|---|---|---|
| Inner loop feedback | < 2 min | < 5 min | Time from save to test result |
| PR pickup time | < 2 hours | < 6 hours | Time from PR opened to first review |
| PR merge time (p75) | < 6 hours | < 1 day | GitHub/Linear analytics |
| Deployment frequency | > 4×/day | 1×/day | Deployment logs |
| Lead time | < 1 day | < 1 week | Commit SHA → deploy timestamp |
| MTTR | < 30 min | < 4 hours | Incident tracking |
| Flaky test rate | < 1% | < 3% | CI analytics |
| Toil fraction | < 20% of sprint | < 30% | Self-reported in retro |

**Anomaly detection**: If velocity drops week-over-week, run a 30-minute toil audit. Common new toil sources: a new security gate added without optimization, slow dependency added to hot path, flaky test suite that everyone works around.
