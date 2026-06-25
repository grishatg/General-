---
name: sales-automation
description: Guide B2B sales strategy, outbound prospecting, lead qualification, and CRM workflows. Use when defining an ICP, researching accounts, building outbound sequences, analyzing pipeline, or setting up sales automation. Triggers include: 'ICP', 'ideal customer profile', 'outbound', 'prospecting', 'lead enrichment', 'CRM', 'deal stage', 'cadence', 'SDR', 'AE', 'pipeline', 'qualification', 'BANT', 'signal', 'account research', 'contact research', 'cold email', 'cold call', 'sales sequence'. Do NOT use for marketing content (marketing-growth skill) or pricing strategy (monetization skill).
license: MIT
---

# Sales Automation

B2B sales frameworks grounded in 2026 benchmarks. Not generic advice — specific frameworks with numbers.

## ICP: The 5-Layer Model

Your Ideal Customer Profile is a **living data model**, not a one-page doc. Review quarterly.

**Layer 1 — Firmographics** (filter the addressable universe):
- Industry vertical (be specific: "B2B SaaS" not "software")
- Headcount range (e.g., 50–500 employees)
- Annual revenue range (e.g., $5M–$50M ARR)
- Geography
- Funding stage (if relevant: Seed/Series A/B, bootstrapped, public)

**Layer 2 — Technographics** (signals from their tech stack):
- CRM in use (Salesforce vs HubSpot → different buyer personas)
- Marketing automation stack (signals budget and sophistication)
- Security certifications (SOC2 = compliance buyer = long cycle)
- Cloud provider (AWS → certain infra patterns; GCP → certain ML/data patterns)

**Layer 3 — Behavioral signals** (real-time triggers):
- Hiring patterns (CRO hire → sales transformation initiative)
- Funding round announced (budget available, growth mode)
- Tool churn (left Salesforce → evaluating alternatives)
- Pricing page visits (intent signal from product analytics)
- Webinar/content downloads (top-of-funnel engagement)

**Layer 4 — Organizational readiness**:
- Buyer persona exists at target title level
- Buying committee size and structure (champion + economic buyer + technical evaluator)
- Deal maturity signals (active RFP, budget cycle timing)

**Layer 5 — Negative indicators** (disqualify fast):
- Competitor in-contract (locked in, waste of time unless renewal is < 3 months)
- < 10 employees (too small for your price point)
- Industry you don't serve (compliance, sales cycle, or data reasons)
- No champion identified after 2 touches

**ICP outcomes when used correctly**: 68% higher win rate, 25–35% shorter sales cycles, 40% reduction in qualification time (2026 industry benchmarks).

## Signal Stacking

Don't prospect on a single trigger. Stack multiple signals — multi-signal accounts convert 3–5× faster.

**Weak signal (single)**: Company raised Series B → send generic congrats email
**Strong signal (stacked)**: Company raised Series B **AND** posted CRO job **AND** visited pricing page twice in 30 days → high-intent outreach with specific messaging

**Signal types to blend**:

| Signal Type | Example | Source |
|---|---|---|
| Firmographic | Just raised $20M Series B | Crunchbase, Lusha signals |
| Technographic | Just added Outreach.io (intent to scale sales) | BuiltWith, Lusha |
| Behavioral | 3 visits to pricing page in 7 days | Product analytics / reverse IP |
| Strategic | New CRO hired 30 days ago | LinkedIn, Lusha signals |
| Competitive | Competitor's contract renewal in 60 days | G2, sales intel |

**Lusha signals to monitor daily** (if Lusha MCP connected):
- Funding rounds (48-hour window is critical — move fast)
- Leadership changes (new CTO/CRO/CMO hire)
- Headcount growth > 20% (scaling pains = tool purchases)
- Key contact job changes (warm relationship at new company)

## Outbound Cadence: 8–12 Touches Over 2–4 Weeks

**2026 benchmarks**:
- Cold email reply rate: 5.1%
- Cold call success rate: 2.3%
- Multi-channel cadence reply rate: 8–12% (2–2.5× single-channel)

**Proven cadence structure** (multi-channel, not email-only):

```
Day 1:  Email (personalized, 3-sentence max, specific trigger)
Day 2:  LinkedIn connection request (no pitch in request)
Day 3:  Phone call (leave voicemail if no answer)
Day 5:  Email follow-up (add value: relevant case study or insight)
Day 7:  LinkedIn message (reference shared connection or content)
Day 10: Phone call (reference email + LinkedIn touch)
Day 14: Email (different angle: problem-focused, not product-focused)
Day 18: "Break-up" email (honest: "Should I stop reaching out?")
```

**Email structure (cold)**:
- Line 1: Specific trigger (funding, hire, article they wrote)
- Line 2: Crisp value statement (outcome, not feature)
- Line 3: Single, low-friction CTA ("15 min Thursday at 2pm?")
- No attachments on cold emails; no more than 150 words

**Personalization minimum**: Reference something specific about the company or person that required research. "I loved your blog post" = not personalized. "I saw you just launched in EMEA — we helped [similar company] do the same while keeping CAC under $X" = personalized.

## CRM Hygiene

Bad CRM data makes analytics impossible. Fix the data layer first, then optimize the workflow.

**Required fields for every contact**:
- Validated email address (not role-based: avoid info@, support@)
- LinkedIn profile URL
- Direct phone number (not switchboard)
- Title (exact, from LinkedIn)
- Last activity date (auto-logged by sequence tool)

**Required fields for every deal**:
- ICP tier (Tier 1 / 2 / 3 — based on your scoring model)
- Deal source (outbound / inbound / referral / partner)
- Close date (realistic, updated every pipeline review)
- Next action + next action owner + next action date

**Automation to implement** (eliminates manual logging):
- Auto-log emails via BCC or native integration
- Auto-create activities from call recordings
- Auto-update deal stage based on email keywords or meeting completion
- Alert AE when deal has no activity > 14 days (stuck deal signal)

**Impact**: Clean CRM reduces sales ops friction 30%; improves lead routing accuracy 40%.

## Deal Qualification Framework

Define explicit entry criteria for each stage. Prevents pipeline inflation ("deal creep").

```
Stage 0 → Prospect:     In ICP; has been researched; not yet contacted
Stage 1 → Contacted:    At least 1 meaningful touchpoint; responded to outreach
Stage 2 → Qualified:    BANT confirmed: Budget (≥ your floor) + Authority (economic buyer identified) + Need (pain confirmed) + Timing (< 6 months)
Stage 3 → Opportunity:  Demo completed; champion identified; multi-threading started
Stage 4 → Proposal:     Verbal pricing discussion; proposal sent
Stage 5 → Negotiation:  Legal/procurement engaged; timeline confirmed
Stage 6 → Closed Won/Lost
```

**Win rate by stage target** (should increase as deals progress):
- Stage 2 → 3: 50%+ (if < 40%, qualification criteria are too loose)
- Stage 3 → 4: 65%+
- Stage 4 → 5: 75%+
- Stage 5 → Close Won: 85%+

See [workflows.md](references/workflows.md) for complete MCP-powered workflow implementations.
