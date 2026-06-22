# Sales & Marketing Automation

MCP-powered workflows for GTM (Go-to-Market) execution using Claude Code.

---

## Core MCP Stack for GTM

| Tool | MCP Server | Primary Use |
|---|---|---|
| HubSpot | `mcp-hubspot` (official) | CRM — contacts, deals, tickets, quotes |
| Lusha | Built-in (this session) | B2B enrichment, prospecting, lookalike search |
| Gmail | Built-in (this session) | Email automation and triage |
| Google Calendar | Built-in (this session) | Scheduling and follow-up cadences |
| Notion | Built-in (this session) | Account research, content calendar, playbooks |
| Figma | Built-in (this session) | Design assets, ad creatives, landing pages |
| Amplitude / Mixpanel | Community MCPs | Usage analytics for PLG (product-led growth) |
| Slack | Community MCP | Team notifications and deal alerts |

---

## Workflow 1: Inbound Lead Processing

Trigger: New lead fills out a form or signs up for a trial.

```
1. HubSpot MCP — contact created, deal stage = "New Lead"
2. Lusha MCP   — enrich: company size, industry, revenue, tech stack, decision-makers
3. Notion MCP  — create account research page with enrichment data
4. Amplitude MCP — pull product usage (if existing free user)
5. Gmail MCP   — send personalized intro email (reference their industry + use case)
6. Google Calendar MCP — add 3-day follow-up task
7. Slack MCP   — notify assigned AE: "@{name} New lead: {company}, {title}"
8. HubSpot MCP — update deal with enrichment + outreach log
```

**Claude prompt to run this:**
```
Process this new lead:
- Name: [name], Company: [company], Email: [email]
- Enrich with Lusha, create a Notion research page,
  draft a personalized intro email, and notify the AE in Slack
```

---

## Workflow 2: Outbound Prospecting

Trigger: Sales rep defines an ICP (Ideal Customer Profile).

```
1. Lusha MCP — prospecting_company_search: filter by industry, size, growth signals
2. Lusha MCP — lookalike_companies: find companies similar to top 3 customers
3. Lusha MCP — prospecting_contact_search: find decision-makers at target companies
4. Lusha MCP — prospecting_contact_enrich: get emails, phones, LinkedIn
5. Notion MCP — create target account list with research
6. Gmail MCP  — draft personalized outreach sequences (1-2-3 touch)
7. HubSpot MCP — create contacts + deals in CRM
8. Google Calendar MCP — schedule send times (Tue-Thu 9-11am local time)
```

**ICP Example:**
```
Target: B2B SaaS companies, 50-500 employees, US-based,
raised Series A-B, using Salesforce or HubSpot,
hiring for "Head of Product" or "VP Engineering"
```

---

## Workflow 3: Product Launch

Trigger: New feature or product ready to ship.

```
PRE-LAUNCH (T-14 days):
1. Figma MCP    — export launch assets (hero image, social cards, ad creatives)
2. Notion MCP   — create launch brief: positioning, messaging, audience, channels
3. Google Drive MCP — store all assets in shared launch folder
4. Gmail MCP    — draft announcement email to existing customers

LAUNCH DAY:
5. Amplitude MCP — establish baseline metrics (DAU, feature adoption, conversion)
6. Gmail MCP    — send customer announcement
7. Slack MCP    — post to #announcements channel
8. HubSpot MCP  — update all active deals with new feature info

POST-LAUNCH (T+7 days):
9. Mixpanel MCP  — analyze adoption funnel, drop-off points
10. Amplitude MCP — cohort analysis: who's using it? who isn't?
11. Gmail MCP    — send targeted follow-up to non-adopters
12. Notion MCP   — write 7-day post-mortem with data
```

---

## Workflow 4: Deal Acceleration (Stuck Opportunities)

Trigger: Deal has been in a stage > 14 days with no activity.

```
1. HubSpot MCP   — query deals stuck in stage > 14 days
2. Lusha MCP     — enrich: find additional stakeholders at the account
3. Amplitude MCP — pull their product usage (are they still active?)
4. Notion MCP    — research company news, funding, hiring (find a trigger)
5. Gmail MCP     — draft "breakup email" or re-engagement based on trigger
6. Google Calendar MCP — propose a specific time for a call
7. HubSpot MCP   — log activity, update next step date
8. Slack MCP     — notify AE + manager with context
```

---

## Workflow 5: Customer Success & Expansion

Trigger: Customer approaching end of trial or renewal date.

```
HEALTH SCORING:
1. Amplitude MCP  — weekly active usage score
2. Mixpanel MCP   — feature breadth (how many features used?)
3. HubSpot MCP    — support ticket volume (negative signal)
4. Lusha MCP      — company growth signals (hiring = expansion potential)

AT-RISK (health score < 40):
5. Gmail MCP      — CS proactive outreach: "Here's what you haven't tried"
6. Google Calendar MCP — schedule success call
7. HubSpot MCP    — create at-risk flag on account

EXPANSION READY (health score > 80, usage near tier limit):
8. HubSpot MCP    — create expansion opportunity in CRM
9. Gmail MCP      — send upgrade proposal with ROI data
10. Amplitude MCP  — pull their ROI metrics for the proposal
```

---

## Content & SEO Automation

### Content Calendar Workflow
```
1. Notion MCP      — maintain content calendar database
2. Amplitude MCP   — identify high-traffic pages to expand
3. Mixpanel MCP    — find features users search for in-app (content ideas)
4. Gmail MCP       — coordinate with writers and designers
5. Google Drive MCP — manage drafts, review, publish flow
6. Figma MCP       — create featured images and social assets
```

### SEO-Driven Lead Gen
```
Target: Informational keywords where ICP searches for solutions

Workflow:
1. Identify 10 high-intent keywords (jobs-to-be-done framing)
2. doc-coauthoring skill → draft long-form content for each
3. Figma MCP → design custom illustrations (not stock photos)
4. Google Drive MCP → store and version-control content
5. Amplitude MCP → track organic traffic + conversion by article
```

---

## Metrics Dashboard

Track these weekly; review in Notion.

### Sales Metrics
```
Pipeline metrics:
- New MQLs this week
- MQL → SQL conversion %
- Average deal size
- Sales cycle length (days)
- Win rate by source / ICP segment

Activity metrics:
- Outbound emails sent
- Meetings booked
- Demos completed
- Proposals sent
```

### Marketing Metrics
```
Acquisition:
- Traffic by channel (organic, paid, referral, direct)
- Trial starts by channel
- CAC by channel

Activation:
- Trial → active user % (at day 1, day 7)
- Feature adoption rate
- Time to first value

Retention:
- DAU/WAU/MAU ratios
- 30/60/90-day retention curves
- Churn rate by cohort
```

### Revenue Metrics
```
- MRR / ARR
- New MRR, Expansion MRR, Churned MRR
- NRR (target: >110%)
- Payback period (target: <12 months)
- LTV:CAC ratio (target: >3:1)
```

---

## Lusha Signals — What to Watch

Lusha MCP provides real-time company signals that trigger outreach:

| Signal | What It Means | Action |
|---|---|---|
| Funding round announced | Budget available, growth mode | Contact CFO/CPO within 48 hours |
| New CTO/VP hired | Tech stack decisions incoming | Reach out to new hire + old champion |
| Headcount growing >20% | Scaling pains, tool purchases | Pitch efficiency/productivity angle |
| Key contact job change | Warm relationship at new company | Re-engage at new company |
| Competitor churned | They may be evaluating | Time-sensitive outreach |

```
# Daily signal check with Lusha MCP
"Check Lusha signals for all accounts in our pipeline
and flag any with funding, leadership changes, or hiring spikes.
Create a Notion table with action items for each AE."
```
