# Sales Automation: MCP Workflow Reference

## Complete Workflow Implementations

### Workflow 1: Inbound Lead Processing

Trigger: New lead signs up or fills out a form.

```
Step 1: HubSpot MCP
  Tool: create_contact
  Data: name, email, company, source
  Output: contact_id, deal_id

Step 2: Lusha MCP
  Tool: prospecting_contact_enrich
  Input: email or LinkedIn URL
  Output: company size, revenue estimate, title, phone, LinkedIn

Step 3: Lusha MCP
  Tool: prospecting_company_enrich
  Input: company domain
  Output: industry, headcount, tech stack, funding history, growth signals

Step 4: HubSpot MCP
  Tool: update_contact
  Data: enrichment data from Lusha
  Action: update company, title, phone on contact record

Step 5: Notion MCP
  Tool: create_page
  Template: Account Research
  Content: company overview, ICP fit score, key contacts, relevant news

Step 6: Gmail MCP
  Tool: create_draft
  Framework: AIDA (Attention: trigger event → Interest: value prop → Desire: outcome → Action: specific time)
  Personalization: reference company's industry + specific trigger

Step 7: Google Calendar MCP
  Tool: create_event
  Type: follow-up reminder at T+3 days

Step 8: Slack MCP (if configured)
  Tool: send_message
  Channel: #sales or AE direct message
  Message: "New lead: [Company] ([Title]) — ICP Tier [1/2/3]. Enrichment complete. Notion: [link]"

Step 9: HubSpot MCP
  Tool: create_note
  Content: full enrichment summary + outreach plan
```

### Workflow 2: Outbound Prospecting (ICP-Driven)

Trigger: Sales rep defines an ICP segment for a prospecting run.

```
ICP Input Example:
  Industry: B2B SaaS
  Headcount: 50–200
  Geography: US + Canada
  Funding: Series A or B (raised in last 18 months)
  Tech stack: Salesforce OR HubSpot
  Negative: companies with < 5 SDRs (too small for our price point)

Step 1: Lusha MCP
  Tool: prospecting_company_search
  Filters: industry, size, geography, funding stage
  Output: company list

Step 2: Lusha MCP
  Tool: lookalike_companies
  Input: your top 3 existing customers
  Output: companies with similar firmographic + technographic profile

Step 3: Deduplicate + score combined list
  Remove: existing customers, current pipeline, recently lost deals
  Score: by ICP layer fit (Layer 1–5 from sales-automation SKILL.md)

Step 4: Lusha MCP (per target company)
  Tool: prospecting_contact_search
  Target titles: CRO, VP Sales, Head of Revenue, COO
  Output: contact list per company

Step 5: Lusha MCP
  Tool: prospecting_contact_enrich
  Input: contact ID or LinkedIn URL
  Output: validated email, direct dial, LinkedIn, seniority

Step 6: Notion MCP
  Tool: create_database_entry (target accounts database)
  Fields: company, ICP tier, key contacts, signals, assigned AE, status

Step 7: Gmail MCP
  Tool: create_drafts (batch)
  Volume: first 20 highest-score accounts
  Personalization: reference specific signal (funding, hiring, tech stack signal)

Step 8: HubSpot MCP
  Tool: bulk_create_contacts + create_deals
  Stage: Prospect (Stage 0)
  Source: Outbound - Lusha
```

### Workflow 3: Lusha Signals — Daily Alert

Trigger: Scheduled daily run (or on-demand).

```
Step 1: Lusha MCP
  Tool: signals_contacts_search
  Filter: contacts in your CRM who changed jobs in last 7 days
  Action: immediate re-engagement at new company (warm relationship)

Step 2: Lusha MCP
  Tool: signals_companies_search
  Filter: companies in pipeline with funding news in last 48 hours
  Action: AE notified; upgrade outreach to economic buyer

Step 3: Lusha MCP
  Tool: signals_companies_search
  Filter: target accounts (not yet pipeline) with leadership hire signal
  Action: create new opportunity; reach out to new hire

Step 4: Slack MCP
  Tool: send_message
  Channel: #signals
  Message: formatted digest of all signals with action items per AE
```

### Workflow 4: Stuck Deal Acceleration (> 14 days no activity)

```
Step 1: HubSpot MCP
  Tool: search_deals
  Filter: last_activity_date < today - 14 days AND stage != closed
  Output: stuck deal list

Step 2: For each stuck deal:
  Lusha MCP → signals_companies_get: any new signals?
  Lusha MCP → prospecting_contact_search: find additional stakeholders
  Amplitude MCP → pull product usage for this account

Step 3: Categorize by reason:
  A) Still active users + no response → try new stakeholder
  B) Usage dropping → CS rescue call
  C) No usage + no response → breakup email

Step 4: Gmail MCP → draft appropriate email per category:
  A) "I noticed [new stakeholder] joined — worth a 15-min intro?"
  B) "Usage looks like onboarding hit a snag — can I help?"
  C) "Should I close this out? Happy to reconnect when timing is better."

Step 5: HubSpot MCP → log all activities; set next_action_date + owner
Step 6: Slack MCP → notify AE + manager with deal list + recommended actions
```

### Workflow 5: Weekly Pipeline Review Prep

```
Step 1: HubSpot MCP → pull all open deals with stage, amount, close date, last activity
Step 2: HubSpot MCP → compare close dates vs. today (how many are past due?)
Step 3: Amplitude MCP → usage scores for all pipeline accounts
Step 4: Lusha MCP → signals for all pipeline companies (funding, hiring, news)
Step 5: Notion MCP → create pipeline review page with:
  - Deal count by stage
  - Total pipeline value
  - Weighted pipeline (by stage probability)
  - At-risk deals (no activity > 14 days)
  - Positive signals by account
  - Actions per AE
Step 6: Gmail MCP → send pipeline summary to sales leadership
```

## ICP Scoring Template

Score each prospective account 0–100:

| Layer | Weight | Criteria | Score |
|---|---|---|---|
| Firmographic fit | 25% | Industry + size + geo match | 0–25 |
| Technographic fit | 20% | Tech stack alignment | 0–20 |
| Signal strength | 25% | Recent trigger event (funding, hire, churn) | 0–25 |
| Org readiness | 20% | Buyer persona present; buying process identifiable | 0–20 |
| Negative flags | -10% per flag | Competitor locked; too small; no champion | -10 each |

**Tier 1** (score ≥ 80): AE-personalized outreach; priority
**Tier 2** (score 50–79): SDR-led outreach with templates
**Tier 3** (score < 50): Marketing nurture; revisit quarterly

## Cold Email Templates (AIDA Framework)

### Template A — Funding Trigger
```
Subject: Congrats on the Series B — quick thought

[First name],

Saw the Series B news — impressive round. Companies at your stage 
typically have [specific scaling pain] as a top-3 priority right now.

We help [ICP descriptor] teams like [similar company] [specific outcome 
with number] — typically within [timeframe].

Worth 15 minutes to see if it applies? I have [Day] at [Time] or [Day] at [Time].

[Your name]
```

### Template B — Leadership Hire
```
Subject: Welcome to [Company], [First name]

[First name],

Noticed you just joined [Company] as [Title] — congrats.

New [Title]s at companies like yours usually inherit [specific challenge] 
as an immediate priority. We've helped [2–3 similar companies] [outcome].

Would a 15-minute orientation call make sense? Happy to share what's 
working for similar teams right now.

[Day/time options]
```

### Breakup Email
```
Subject: Closing the loop

[First name],

I've reached out a few times without hearing back — totally understand, 
timing isn't always right.

I'll stop reaching out unless you'd like to reconnect. If things change 
in the next quarter, my calendar link is below — happy to pick up where we left off.

Wishing [Company] a strong Q[N].

[Your name]
```
