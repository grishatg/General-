# Monetization Playbook

Framework for choosing and validating a revenue model for software products.

---

## Step 1: Choose Your Model

Evaluate against your product's core characteristics before committing.

| Model | Best Fit | Key Metric | Avoid When |
|---|---|---|---|
| **Freemium** | High volume, viral loops, network effects | Free → Paid conversion % (target: 2–5%) | Low traffic or high COGS per user |
| **Subscription** | Sticky workflows, recurring value delivery | Monthly Churn (target: <2%) / NRR (target: >110%) | Users get value once and leave |
| **Usage-based** | AI/API products, variable consumption | Gross margin at scale (target: >70%) | Unpredictable revenue is unacceptable |
| **Marketplace** | Platform plays, two-sided supply/demand | Take rate × GMV | You don't control both sides |
| **API licensing** | Developer tools, B2B, embed use cases | API call volume growth MoM | Requires strong developer relations |
| **Enterprise license** | Complex deployments, compliance requirements | ACV (Annual Contract Value), logo count | Sales cycle >6 months is unsustainable |

---

## Step 2: Unit Economics Template

Fill this in before building paywalls.

```
CAC (Customer Acquisition Cost)
  = Total Sales + Marketing Spend / New Customers Acquired
  Target: CAC Payback Period < 12 months

LTV (Lifetime Value)
  = ARPU × Gross Margin % / Churn Rate
  Target: LTV:CAC ratio > 3:1

Gross Margin
  = (Revenue - COGS) / Revenue
  COGS includes: hosting, AI inference costs, support
  Target: >70% for SaaS, >50% for usage-based

Payback Period
  = CAC / (ARPU × Gross Margin %)
  Target: <12 months for self-serve, <18 months for enterprise
```

---

## Step 3: Validation Experiments

Run these before building full payment infrastructure.

### Freemium Validation
- [ ] Ship free tier with hard usage caps (not soft limits)
- [ ] Add upgrade prompt at cap with pricing page
- [ ] Measure: How many users hit the cap? What % click upgrade? What % convert?
- [ ] Target: >10% of active users hitting cap before launch

### Subscription Validation
- [ ] Stripe Checkout with a single price point (no tiers yet)
- [ ] Offer 7-day free trial, credit card required
- [ ] Measure: Trial start rate, trial-to-paid %, MoM churn in month 2+
- [ ] Do not build annual plans until monthly churn < 3%

### Usage-Based Validation
- [ ] Instrument every billable action with precise counting
- [ ] Show users their usage in real-time (prevents bill shock)
- [ ] Run 1-month free tier, then switch to pay-as-you-go
- [ ] Measure: Usage distribution (P50, P90, P99 — who are your whales?)

### Marketplace Validation
- [ ] Manual matching before building the platform
- [ ] Charge supply side first (they have more to gain)
- [ ] Prove 3 repeat transactions from the same buyer before automating
- [ ] Measure: Repeat purchase rate, NPS of both sides

---

## Step 4: Paywall Design

### Principles
- Block on value delivery, not on time (time-gating feels punitive)
- Show the upgrade value *at the moment of friction*, not before
- One CTA per paywall screen — never two options on the same screen
- Social proof adjacent to pricing (logos, testimonials, user count)

### Trial-to-Conversion Optimization
- [ ] Email at day 1: "Here's what you can do today"
- [ ] Email at day 4: "Your trial ends in 3 days — here's what you'll lose"
- [ ] Email at day 7: Last chance with a single-click upgrade link
- [ ] In-app: Countdown timer visible in nav (not intrusive, but persistent)
- [ ] Post-trial: Downgrade to free tier, do NOT delete data — data hostage is the best upgrade prompt

### Pricing Anchoring
- Always show 3 tiers: Starter / Pro / Enterprise
- Make the middle tier the obvious choice (highlight it)
- Price the top tier 3–5× middle to make middle feel reasonable
- Annual discount: 20% off (equivalent to 2.4 months free) — not more

---

## Step 5: Revenue Expansion

Once baseline revenue is working:

```
Expansion Revenue Levers:
1. Seat expansion       — more users in the same account
2. Usage expansion      — same users, more volume
3. Feature upsell       — unlock higher-tier features
4. Cross-sell           — adjacent product lines
5. Professional services — implementation, training, custom work
```

Net Revenue Retention (NRR) formula:
```
NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
Target: >110% means product grows even without new logos
```

---

## MCP-Powered Monetization Workflows

### Subscription Analytics Stack
```
Stripe → (webhook) → track payment events in Amplitude MCP
Amplitude MCP → analyze trial-to-paid funnel
Mixpanel MCP → track feature usage by tier
Gmail MCP → send lifecycle emails (trial start, day 4, expiry)
Notion MCP → maintain pricing experiment log
```

### Sales Pipeline (Usage-Based / Enterprise)
```
Lead qualifies (HubSpot MCP — deal created)
Lusha MCP → enrich contact with company financials, headcount
Google Calendar MCP → book discovery call
Notion MCP → create account research page
Gmail MCP → send personalized proposal
HubSpot MCP → track deal stage progression
Amplitude MCP → pull usage data for QBRs
```

---

## Checklist Before Launch

- [ ] Unit economics are positive at current scale
- [ ] Payback period modeled at 3 scenarios: bear / base / bull
- [ ] Stripe (or equivalent) integrated and tested end-to-end
- [ ] Dunning sequence configured (failed payment recovery)
- [ ] Legal: Terms of Service and Privacy Policy published
- [ ] Tax: VAT/GST handling configured (Stripe Tax or equivalent)
- [ ] Support escalation path defined for billing disputes
- [ ] Analytics: Revenue, churn, and NRR in a live dashboard
