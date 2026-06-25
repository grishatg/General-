# Growth Engine Plugin

Sell, market, and monetize. Built on 2026 GTM benchmarks with MCP connectors wired in.

## Skills

### `sales-automation`
B2B sales engine with structured frameworks:
- ICP 5-layer model: firmographic + technographic + behavioral + readiness + negative signals
- Signal stacking: multi-signal accounts convert 3–5× faster than single-trigger
- 8–12 touch multi-channel cadence (email + phone + LinkedIn); cold email 5.1%, cold call 2.3% reply rates
- CRM hygiene as prerequisite; quarterly ICP review
- ICP-matched accounts: 68% higher win rate, 25–35% shorter sales cycle

### `marketing-growth`
Content and conversion frameworks:
- AIDA (Attention-Interest-Desire-Action) for cold/top-of-funnel audiences
- PAS (Problem-Agitate-Solution) for problem-aware/warm audiences
- Topic cluster + pillar page model: 25–40% organic traffic lift vs siloed posts
- CRO layered: copy (60% of conversion variance) → UX (25%) → offer (15%)
- Psychology levers: social proof, anchoring, loss aversion, scarcity

### `monetization`
Unit economics and pricing strategy:
- Pricing models: freemium (5–8% conversion), tiered, usage-based, hybrid (recommended)
- LTV:CAC ≥ 3:1 minimum; ≥ 4:1 healthy; payback period < 12 months
- NRR: 90–100% stable; 110%+ healthy; 120%+ = 21× EV/revenue multiple
- Trial-to-paid: opt-in 8.9%, credit-card-required 31.4%; Day-0 paywall converts highest
- Expansion revenue target: 30% of total ARR (current SaaS median: 10%)

### `connectors`
Tiered MCP connector stack: which tools to wire up and in what order, with specific use cases and cross-tool GTM workflows.

## Commands

### `/growth-engine:lead-research $COMPANY`
Full lead enrichment: company research → contact discovery → Notion page → outreach draft.

### `/growth-engine:pricing-model $PRODUCT`
Evaluate a product against unit economics benchmarks; recommend pricing model and paywall design.

## Agents

### `gtm-strategist`
Dedicated GTM strategist. Develops ICP definitions, outbound sequences, launch playbooks, and monetization experiments. Invoked for strategic sales/marketing questions.

## MCP Connectors

Configure credentials with `/plugin configure growth-engine`:

| Token | Required | Purpose |
|---|---|---|
| `hubspot_api_token` | Recommended | Contacts, deals, tickets, quotes |
| `lusha_api_key` | Recommended | B2B contact enrichment, prospecting |
| `notion_token` | Recommended | Account research pages, content calendar |
| `slack_bot_token` | Optional | Deal alerts, GTM notifications |
