# General- Plugin Marketplace

A Claude Code plugin marketplace with two production-ready plugins for engineering teams that need to ship fast *and* sell effectively.

## Install

```
/plugin marketplace add grishatg/General-
/plugin install precision-delivery@general-marketplace
/plugin install growth-engine@general-marketplace
```

## Plugins

### Precision Delivery

Skills, commands, and agents for shipping with extreme accuracy.

| Component | Invocation | What it does |
|---|---|---|
| Skill: `precision-engineering` | Auto-triggered | PR-size enforcement, TDD, 80% coverage gates, defensive boundaries |
| Skill: `product-delivery` | Auto-triggered | Definition of Done gates, feature flags vs canary, staged rollouts, DORA |
| Skill: `dev-productivity` | Auto-triggered | Toil elimination, inner/outer loop, async-first docs |
| Command: `/precision-delivery:ship-check` | Manual | Full pre-ship gate: tests → lint → security → code review |
| Command: `/precision-delivery:pr-review` | Manual | Severity-gated review of current diff |
| Agent: `precision-reviewer` | Claude-invoked | Adversarial correctness reviewer subagent |

### Growth Engine

Skills, commands, agents, and MCP connectors for GTM and monetization.

| Component | Invocation | What it does |
|---|---|---|
| Skill: `sales-automation` | Auto-triggered | ICP 5-layer, signal stacking, 8–12 touch cadences, CRM hygiene |
| Skill: `marketing-growth` | Auto-triggered | AIDA/PAS, topic clusters, CRO psychology levers |
| Skill: `monetization` | Auto-triggered | LTV:CAC, NRR, trial-to-paid, pricing models, paywall design |
| Skill: `connectors` | Auto-triggered | MCP connector stack: HubSpot, Lusha, Notion, Slack, Amplitude |
| Command: `/growth-engine:lead-research` | Manual | Enrich and research a lead using available connectors |
| Command: `/growth-engine:pricing-model` | Manual | Evaluate a pricing model against unit economics benchmarks |
| Agent: `gtm-strategist` | Claude-invoked | Dedicated GTM strategist subagent |

## MCP Connectors (Growth Engine)

Configure your tokens after installing:

```
/plugin configure growth-engine
```

| Connector | Purpose |
|---|---|
| HubSpot | Contacts, deals, tickets, quotes |
| Notion | Specs, wikis, account research |
| Slack | Channel posts, deal alerts |
| Playwright | Web automation and scraping |
| Postgres | Direct database queries |

## Repository Structure

```
.claude-plugin/marketplace.json       # This marketplace manifest
plugins/
  precision-delivery/                 # Plugin 1
    .claude-plugin/plugin.json
    skills/
      precision-engineering/SKILL.md
      product-delivery/SKILL.md
      dev-productivity/SKILL.md
    commands/
      ship-check.md
      pr-review.md
    agents/
      precision-reviewer.md
    hooks/hooks.json
  growth-engine/                      # Plugin 2
    .claude-plugin/plugin.json
    skills/
      sales-automation/SKILL.md
      marketing-growth/SKILL.md
      monetization/SKILL.md
      connectors/SKILL.md
    commands/
      lead-research.md
      pricing-model.md
    agents/
      gtm-strategist.md
    .mcp.json
.github/
  workflows/ci.yml
  PULL_REQUEST_TEMPLATE.md
```

## License

MIT
