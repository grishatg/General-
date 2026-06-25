---
name: connectors
description: Guide MCP connector setup, configuration, and cross-tool workflow automation. Use when setting up integrations, planning multi-tool automation workflows, choosing which connectors to install, or wiring together CRM + analytics + communication tools. Triggers include: 'MCP', 'connector', 'integration', 'HubSpot', 'Lusha', 'Notion', 'Slack', 'Amplitude', 'Mixpanel', 'Jira', 'Linear', 'Postgres', 'connect to', 'wire up', 'automate workflow', 'cross-tool'. Do NOT use for sales strategy (sales-automation) or content strategy (marketing-growth).
license: MIT
---

# MCP Connectors

The right connectors, in the right order, wired to the right workflows. This plugin ships `.mcp.json` with the Growth Engine connectors pre-configured — you only need to supply tokens.

## The Tiered Stack

Install in tier order. Tier 1 unblocks everything else.

### Tier 1 — Core (install first)

| Connector | MCP Server | What it unlocks |
|---|---|---|
| **GitHub** | `@modelcontextprotocol/server-github` | PR reviews, issue creation, CI status, code search, repo management |
| **Notion** | `@notionhq/notion-mcp-server` | Specs, wikis, account research pages, content calendar, meeting notes |
| **Gmail** | Built into Claude Code session | Email triage, drafting, search, label management |
| **Google Calendar** | Built into Claude Code session | Scheduling, availability, follow-up cadences |
| **Google Drive** | Built into Claude Code session | File creation, sharing, permissions, version history |
| **Slack** | `@modelcontextprotocol/server-slack` | Channel search, message send, canvas creation, user lookup |

### Tier 2 — Sales & Marketing

| Connector | MCP Server | What it unlocks |
|---|---|---|
| **HubSpot** | `@hubspot/mcp-server` | Contacts, deals, tickets, invoices, quotes, pipelines (official, June 2025) |
| **Lusha** | Built into this session | B2B contact enrichment, company enrichment, lookalike search, real-time signals |
| **Figma** | `@figma/mcp` | Design assets, brand export, component library sync, design-to-code |
| **Playwright** | `@executeautomation/playwright-mcp-server` | Web automation, competitor research, landing page screenshots |

### Tier 3 — Analytics & Precision

| Connector | MCP Server | What it unlocks |
|---|---|---|
| **Amplitude** | Community MCP | Behavioral funnels, cohort analysis, session replay, experiments |
| **Mixpanel** | Community MCP | Event tracking, retention curves, revenue analytics, JQL queries |
| **Jira** | `sooperset/mcp-atlassian` | Epic/story/bug management, sprint tracking, velocity |
| **Linear** | Community MCP | Engineering issue tracking, cycle analytics, roadmap |

### Tier 4 — Data & Infrastructure

| Connector | MCP Server | What it unlocks |
|---|---|---|
| **Postgres** | `@modelcontextprotocol/server-postgres` | Direct SQL queries, schema inspection, analytics on your data |
| **AWS/GCP/Azure** | Cloud provider MCPs | Infrastructure management, cost queries, resource status |
| **Elasticsearch** | Community MCP | Log analysis, full-text search, debugging |

## Cross-Tool Workflows

### Inbound Lead Processing

```
Trigger: New lead signs up for trial

1. HubSpot MCP     → create contact + deal (Stage: New Lead)
2. Lusha MCP       → enrich: company size, revenue, tech stack, decision-makers
3. Notion MCP      → create account research page with enrichment data
4. Amplitude MCP   → pull existing product usage (if returning user)
5. Gmail MCP       → draft personalized intro email (reference their industry)
6. Google Calendar → add 3-day follow-up task
7. Slack MCP       → notify AE: "New lead: {company} ({title})"
8. HubSpot MCP     → update deal with enrichment + outreach log
```

### Outbound Prospecting

```
Trigger: Sales rep defines ICP segment

1. Lusha MCP       → prospecting_company_search: filter by ICP criteria
2. Lusha MCP       → lookalike_companies: find lookalikes of top 3 customers
3. Lusha MCP       → prospecting_contact_search: find decision-makers
4. Lusha MCP       → prospecting_contact_enrich: get emails + phones + LinkedIn
5. Notion MCP      → create target account list database
6. Gmail MCP       → draft personalized sequences (8-touch cadence)
7. HubSpot MCP     → bulk import contacts + create deals
```

### Deal Health & Expansion

```
Trigger: Weekly revenue review

1. HubSpot MCP     → query deals with no activity > 14 days
2. Amplitude MCP   → pull usage scores for each stuck account
3. Lusha MCP       → check signals (funding, hiring, leadership changes)
4. Gmail MCP       → draft re-engagement emails with trigger-based messaging
5. Slack MCP       → notify AEs with prioritized action list
6. HubSpot MCP     → log activities, update next steps

Expansion trigger:
1. Amplitude MCP   → health score ≥ 80 AND usage ≥ 80% of tier limit
2. HubSpot MCP     → create expansion opportunity
3. Gmail MCP       → send ROI summary + upgrade proposal
```

### Product Launch Sequence

```
T-14 days:
1. Figma MCP       → export launch assets (hero, social cards, ad creatives)
2. Notion MCP      → create launch brief (positioning, messaging, channels)
3. Google Drive    → store assets in launch folder

Launch day:
4. Amplitude MCP   → capture baseline metrics
5. Gmail MCP       → send customer announcement
6. Slack MCP       → post to #product and #gtm channels
7. HubSpot MCP     → update all active deals with new capability

T+7 days:
8. Mixpanel MCP    → adoption funnel analysis; drop-off points
9. Amplitude MCP   → cohort: who used it? who didn't?
10. Gmail MCP      → re-engage non-adopters with targeted message
11. Notion MCP     → write 7-day post-mortem with data
```

## Configuring the Growth Engine Plugin Connectors

After installing the plugin:

```
/plugin configure growth-engine
```

You'll be prompted for:
- `hubspot_api_token` — HubSpot Settings → Integrations → Private Apps → Create app with CRM read/write scopes
- `lusha_api_key` — Lusha account settings → API
- `notion_token` — notion.so/my-integrations → Create integration → copy Internal Integration Secret
- `slack_bot_token` — api.slack.com/apps → Create app → OAuth & Permissions → add `channels:read`, `chat:write`, `users:read` scopes → install to workspace

All tokens are stored in your OS keychain — never written to disk.

## Ecosystem Scale (2026)

- 44,000+ MCP servers indexed (Glama registry)
- 19,000+ servers updated daily (PulseMCP)
- 500+ production-ready servers in official modelcontextprotocol/servers repo
- Compatible with: Claude Code, Cursor, GitHub Copilot, Gemini CLI, Codex CLI, Windsurf, Zed
