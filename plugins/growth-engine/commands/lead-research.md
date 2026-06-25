---
description: Research and enrich a lead or company. Given a company name, domain, or contact email, gathers firmographic data, identifies key contacts, assesses ICP fit, and creates a Notion research page with outreach recommendations. Uses Lusha, HubSpot, and Notion connectors if configured.
argument-hint: "[company name or domain or contact email]"
allowed-tools: Bash,Read
---

# Lead Research

Research and enrich the lead: $ARGUMENTS

## Step 1: Parse the Input

Determine what was provided:
- Company name (e.g., "Stripe") → research the company
- Domain (e.g., "stripe.com") → use domain for enrichment
- Email (e.g., "john@stripe.com") → extract domain + enrich contact

## Step 2: Company Research

If Lusha MCP is connected:
- Use `prospecting_company_enrich` with the domain
- Retrieve: industry, headcount, estimated revenue, location, founding year, tech stack, funding history

If Lusha is not connected, gather from public sources:
- LinkedIn company page
- Crunchbase / PitchBook profile
- Company website → About, Pricing, Careers pages

Target data points:
- Headcount range (exact if available)
- Industry (be specific: not "tech" but "B2B SaaS - HR tech")
- Estimated ARR or revenue range
- Funding stage + most recent round (amount, date, investors)
- Geographic presence (HQ + offices)
- Key tech stack signals (CRM, marketing automation, key integrations)
- Recent news (last 90 days: funding, product launches, leadership changes, press)

## Step 3: ICP Fit Assessment

Score against the 5-layer ICP model (from sales-automation skill):

| Layer | Assessment | Score (0–5) |
|---|---|---|
| Firmographic fit | Size/industry/geo match | / 5 |
| Technographic fit | Tech stack alignment | / 5 |
| Behavioral signals | Recent triggers (funding/hire/churn) | / 5 |
| Org readiness | Buyer persona present; buying process identifiable | / 5 |
| Negative flags | Any disqualifying factors | -X |

Total: / 20 → ICP Tier (Tier 1: 16–20, Tier 2: 10–15, Tier 3: < 10)

## Step 4: Contact Discovery

If Lusha MCP is connected:
- Use `prospecting_contact_search` for this company
- Target titles: CRO, VP Sales, VP Revenue, Head of Sales, CEO (if < 50 employees)
- Also identify: technical evaluator (CTO/VP Eng) and economic buyer (CFO/CEO)

For each contact, retrieve:
- Full name + current title
- Validated work email
- Direct phone number (if available)
- LinkedIn profile URL
- Seniority level

## Step 5: Signals Check

If Lusha MCP connected:
- `signals_companies_get` for this company — any recent funding, leadership, or hiring signals?
- `signals_contacts_get` for key contacts — any recent job changes?

If Lusha not connected:
- Check LinkedIn for recent activity
- Check Crunchbase for funding events in last 90 days

## Step 6: Outreach Recommendation

Based on ICP fit and signals, recommend:
- **Priority** (Tier 1 → immediate AE outreach; Tier 2 → SDR sequence; Tier 3 → nurture)
- **Primary contact** (who to reach out to first and why)
- **Opening angle** (what signal or trigger to reference in the first line of the email)
- **Value proposition angle** (which of your value pillars is most relevant to this company)
- **Suggested cadence** (8-touch multi-channel from sales-automation skill)

## Step 7: Create Notion Research Page

If Notion MCP is connected, create a structured account research page with:

```
Title: [Company Name] — Account Research
Database: [Target Accounts or CRM database]

Properties:
  Company:     [name]
  Domain:      [domain]
  ICP Tier:    [1/2/3]
  ICP Score:   [X/20]
  Status:      Research Complete
  Assigned:    [AE name if known]
  
Content sections:
  ## Company Overview
  ## Firmographic Data
  ## Tech Stack
  ## Recent News & Signals
  ## Key Contacts (table)
  ## ICP Assessment
  ## Recommended Outreach
  ## Notes
```

If Notion is not connected, output the full research summary in the conversation.

## Final Output

Provide a summary in this format:

```
LEAD RESEARCH: [Company Name]
Domain: [domain] | ICP Tier: [1/2/3] | Score: [X/20]

COMPANY
  Industry:    [specific]
  Headcount:   [range]
  Revenue:     [estimate]
  Funding:     [stage + last round]
  HQ:          [city, country]

KEY CONTACTS
  1. [Name] — [Title] — [email] — [phone]
  2. [Name] — [Title] — [email]
  3. [Name] — [Title] — [email]

SIGNALS
  [Any recent triggers from Lusha or public sources]

RECOMMENDED ACTION
  Priority:     [Immediate/Standard/Nurture]
  First contact: [Name] — [why them]
  Opening angle: "[First line of outreach email]"
  Notion page:  [link if created]
```
