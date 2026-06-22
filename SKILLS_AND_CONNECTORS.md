# Skills & Connectors Reference Guide

Curated guide to Claude Code skills and MCP connectors for large-scale, precision-driven projects.

Source: [anthropics/skills](https://github.com/anthropics/skills) · Apache 2.0

---

## Built-in Claude Code Skills

Available in every session — no installation needed.

| Command | Purpose | When to Use |
|---|---|---|
| `/code-review` | 20+ language review, severity-gated findings | Before every merge; blocks on critical issues |
| `/verify` | Runs real app, observes behavior | After any functional change — confirms it actually works |
| `/run` | Launches the project (auto-detects type) | Starting a dev session or smoke-testing after setup |
| `/batch` | Bulk file operations across large repos | Refactors, renames, or formatting passes across 10+ files |
| `/loop 5m /code-review` | Recurring automated review | Continuous quality gate during active development |
| `/security-review` | OWASP-focused security audit | Pre-release or after auth/input handling changes |

---

## anthropics/skills — Top Picks by Use Case

### Accuracy & Quality Gate

**`webapp-testing`**
- Playwright-driven automated UI testing
- Catches regressions before they reach production
- Use: `add webapp-testing to this project` → generates tests, runs them, reports failures
- 5,300+ GitHub stars; most widely deployed testing skill

**`skill-creator`**
- Build domain-specific skills with quantitative evaluation loops
- Iterates: draft → test → metrics → refine until quality bar is met
- Use when your team repeatedly needs the same complex workflow

**`doc-coauthoring`**
- 3-stage process: context → refinement → external reader test
- Catches assumptions and blind spots before real readers hit them
- Use for: RFCs, specs, proposals, PRDs

### Product Delivery & Speed

**`web-artifacts-builder`**
- React 18 + TypeScript + Vite + Tailwind + shadcn/ui pre-wired
- Deploys as a single HTML file — no build pipeline needed
- 40+ UI components ready; no generic purple-gradient defaults

**`mcp-builder`**
- Generates production-quality MCP servers for any external API
- Output includes 10+ complex test cases
- Use to connect proprietary internal tools to Claude

**`claude-api`**
- Full reference: model IDs, pricing, streaming, tool use, caching, batch
- Use when building monetizable Claude-powered products
- Always check before picking a model or designing an agent

### Document Automation (Proposals, Contracts, Reports)

| Skill | Output | Quality Assurance |
|---|---|---|
| `docx` | Word documents | XML-level manipulation; tracked changes support |
| `pdf` | PDF creation/extraction | OCR on scanned docs; merge/split/encrypt |
| `pptx` | PowerPoint decks | Mandatory visual QA per slide (overlap, contrast, alignment) |
| `xlsx` | Excel spreadsheets | Formula recalculation via LibreOffice — zero formula errors |

### Team Communication & Alignment

**`internal-comms`**
- Templates: 3P updates (Progress, Plans, Problems), incident reports, newsletters
- Standardizes how the team communicates status upward
- Prevents "what's the status?" Slack threads

**`doc-coauthoring`**
- External reader testing catches what you're too close to see
- Critical for onboarding docs and external-facing specs

**`brand-guidelines`**
- Applies consistent color, typography, tone across all artifacts
- Color palette, Poppins/Lora fonts, dark/light mode variants

### Client-Facing Design

**`frontend-design`**
- Distinctive, subject-grounded UIs — not AI-template defaults
- Workflow: design system → critique → build (responsive + accessible)

**`theme-factory`**
- 10 professional themes; custom generation if none fit
- Applies consistently across decks, docs, and web pages

**`canvas-design`**
- Museum-quality visual artifacts (PDF/PNG)
- 90% visual, 10% text — for posters and high-end collateral

---

## MCP Connector Stack

### Tier 1 — Core (Wire These First)

| Connector | What It Unlocks |
|---|---|
| **GitHub MCP** | PR reviews, issue creation, CI status, code search |
| **Notion MCP** | Specs, wikis, meeting notes, project databases |
| **Gmail MCP** | Email triage, drafting, label management, thread search |
| **Google Calendar MCP** | Scheduling, availability checking, event management |
| **Google Drive MCP** | File creation, sharing, metadata, permissions |
| **Slack MCP** | Channel search, message send, canvas creation, user lookup |

### Tier 2 — Sales & Marketing

| Connector | What It Unlocks |
|---|---|
| **HubSpot MCP** | Contacts, deals, tickets, invoices, quotes — natural language queries |
| **Lusha MCP** | B2B contact + company enrichment, lookalike prospecting, signals |
| **Figma MCP** | Design-to-code, brand asset export, component library sync |
| **Kiwi.com MCP** | Travel search for field sales teams |

### Tier 3 — Analytics & Precision

| Connector | What It Unlocks |
|---|---|
| **Amplitude MCP** | Behavioral funnels, cohorts, session replay, experiments |
| **Mixpanel MCP** | Event tracking, retention curves, revenue analytics, JQL |
| **Jira MCP** | Epic/story/bug management, sprint tracking |
| **Linear MCP** | Engineering issue tracking, cycle analytics |

### Tier 4 — Infrastructure & Scale

| Connector | What It Unlocks |
|---|---|
| **PostgreSQL MCP** | Direct DB queries, schema inspection |
| **AWS/GCP/Azure MCPs** | Cloud resource management |
| **Elasticsearch MCP** | Log analysis, full-text search |
| **Playwright/Selenium MCP** | Browser automation at scale |

---

## Skill Priority for Big Projects

Run these on every significant project:

```
1. /code-review       — before every merge (blocks on severity: critical)
2. webapp-testing     — after every UI change
3. /security-review   — before every release
4. /verify            — after any infra or config change
5. doc-coauthoring    — for every external-facing spec or RFC
6. internal-comms     — weekly 3P status updates to stakeholders
```

---

## Quick-Start Commands

```bash
# Install a skill from anthropics/skills
/install-skill https://github.com/anthropics/skills/tree/main/webapp-testing

# Run code review at max thoroughness
/code-review --effort max

# Verify a change in the real app
/verify

# Build an MCP connector for an internal API
/install-skill https://github.com/anthropics/skills/tree/main/mcp-builder
# then: "build an MCP server for [your API URL]"

# Create a spec with blind-spot testing
/install-skill https://github.com/anthropics/skills/tree/main/doc-coauthoring
# then: "co-author a spec for [feature]"
```

---

## Ecosystem Scale (as of 2026)

- **Glama Registry**: 44,000+ MCP servers indexed
- **PulseMCP**: 19,000+ servers updated daily
- **Official GitHub**: 500+ production-ready servers
- **Skill installs**: 277,000+ for Anthropic frontend-design; 476,000+ for Superpowers
- **SKILL.md standard**: Cross-platform (Claude Code, Cursor, GitHub Copilot, Gemini CLI, Codex CLI)
