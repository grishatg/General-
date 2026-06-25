---
name: product-delivery
description: Guide product delivery, release management, and deployment strategy. Use when planning releases, setting up feature flags, designing canary deployments, defining 'Definition of Done', creating rollout strategies, or discussing DORA metrics. Triggers include: 'feature flag', 'canary', 'staged rollout', 'release management', 'definition of done', 'DoD', 'rollback', 'deployment', 'DORA', 'change failure rate', 'lead time', 'SLO', 'ship', 'release'. Do NOT use for code-level quality (precision-engineering skill) or developer workflow tooling (dev-productivity skill).
license: MIT
---

# Product Delivery

Ship reliably at scale. Every pattern here maps to a DORA metric or a real failure mode at companies that ship > 4× per day.

## DORA Elite Targets (2026 Benchmarks)

| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment frequency | > 4×/day | 1×/day–1×/week | 1×/week–1×/month | < 1×/month |
| Lead time (commit → production) | < 1 day | 1 day–1 week | 1 week–1 month | > 1 month |
| Change failure rate | < 15% | 16–30% | 16–30% | > 30% |
| MTTR (mean time to recovery) | < 30 min | < 1 day | < 1 day | > 1 day |

These are the only four metrics that matter for delivery. If CFR > 15% or MTTR > 30 min, fix those before optimizing frequency.

## Definition of Done as a CI-Enforced Gate

"Done" means **shippable** — not "code complete." The DoD is the contract between engineering and product.

Required DoD elements (enforce via CI checklist, not trust):
- [ ] All automated tests pass (unit + integration + E2E for critical paths)
- [ ] Code reviewed and approved (no unaddressed blocking findings)
- [ ] Documentation updated (API docs, runbook, ADR if architecture changed)
- [ ] Security scan clean (no new high/critical findings)
- [ ] Performance baseline unchanged (no regression > 10% on P99 latency)
- [ ] Feature flag created (if applicable; not merged to flag = not shippable)
- [ ] Rollback procedure documented

**Rework rate target**: < 10%. If rework rate > 15%, your DoD is too weak.

## Feature Flags vs Canary Deployments

These are different tools solving different problems. Use both.

**Feature flags** — control *release risk*:
- Live in application code; toggled by engineers or PMs
- Can target: specific users, orgs, regions, pricing tiers, beta cohorts
- Use for: gradual feature exposure, A/B tests, kill switches, trunk-based dev
- Example: enable for 5% of paid users in EU only

**Canary deployments** — control *infrastructure risk*:
- Live in deployment infrastructure (k8s, ECS, Kubernetes)
- Target: % of servers or traffic (cannot target by user attribute)
- Use for: new service versions, dependency upgrades, config changes
- Standard pattern: 1% → 5% → 25% → 50% → 100%

**When to use which**:
- New product feature → feature flag (you need user-level targeting)
- New service version / infra change → canary (you need traffic-level targeting)
- High-risk release → both (feature flag guards the code, canary guards the infra)

## Staged Rollout Playbook

```
Stage 0: Internal (dogfooding)
  → 100% of internal users
  → Gate: 48 hours stable, no P0 issues

Stage 1: Canary (1%)
  → Monitor: error rate, latency P50/P95/P99, conversion
  → Gate: 1 hour stable, error rate < 2× baseline

Stage 2: Ramp (5%)
  → Gate: 2 hours stable

Stage 3: Expand (25%)
  → Gate: 4 hours stable

Stage 4: Majority (50%)
  → Gate: 24 hours stable

Stage 5: Full (100%)
  → Incident review window: 48 hours
  → Feature flag archived after 2 weeks if stable
```

**Auto-rollback trigger**: Error rate > 2× pre-deploy baseline OR P99 latency > 3× baseline → automatic rollback within 10 minutes.

**MTTD target**: < 5 minutes (time from deploy to detecting a problem). Requires real-time alerting at each stage, not post-hoc analysis.

## Rollback Procedures

Manual rollback must be executable in < 10 minutes by any on-call engineer. Document and drill it.

Rollback checklist:
- [ ] Who can trigger rollback (on-call, any engineer, SRE only)?
- [ ] How to trigger (one command / one click — not a 12-step runbook)?
- [ ] How long does rollback take (target < 10 min)?
- [ ] What is the data migration story (can you roll back the DB?)?
- [ ] Who gets paged when rollback triggers?

**Feature flag rollback**: instant (toggle off). Best rollback story — practice feature-flagging all user-facing changes.

## Incident Response Basics

| Phase | Target | Action |
|---|---|---|
| Detection (MTTD) | < 5 min | Alert fires; on-call paged |
| Acknowledgment | < 10 min | On-call confirms, opens incident channel |
| Mitigation (MTTR) | < 30 min | Rollback, kill switch, or hotfix deployed |
| Resolution | < 2 hours | Root cause identified |
| Post-mortem | Within 48 hours | Blameless; corrective actions assigned |

**Golden signal alerting** (Brendan Gregg / SRE Book): alert on Latency, Traffic, Errors, and Saturation (LTES). If you're not alerting on all four per service, you have blind spots.

## Built-in Quality Layers

Ship confidently by stacking quality at every layer:

```
Layer 1: Test-first (TDD/BDD)         → catches spec drift early
Layer 2: Code review                  → catches logic/design bugs
Layer 3: Automated security + perf    → catches non-functional regressions
Layer 4: Feature flag + canary        → limits blast radius
Layer 5: Production monitoring        → catches what slips through
```

Skipping any layer increases the probability of a post-mortem. Layers 4 and 5 are often skipped — they're not optional at scale.
