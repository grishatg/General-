# Monetization Playbook: Implementation Reference

## Unit Economics Worksheets

### CAC Calculation
```
Monthly CAC Calculation:

Total Sales Spend (salaries + tools + commissions):     $_______
Total Marketing Spend (ads + content + events + tools): $_______
Total S&M Spend:                                        $_______

New Customers Acquired This Month:                      _______

CAC = Total S&M Spend / New Customers
CAC = $_______ / _______ = $_______/customer

CAC Payback Period (months) = CAC / (ARPU × Gross Margin %)
= $_______ / ($_______ × ____%) = _______ months

Benchmark: Target < 12 months (self-serve), < 18 months (SMB), < 24 months (enterprise)
```

### LTV Calculation
```
Monthly LTV Calculation:

ARPU (Average Revenue Per User/month):         $_______
Gross Margin %:                                 _____%
Monthly Churn Rate:                             _____%

LTV = ARPU × Gross Margin / Monthly Churn Rate
LTV = $_______ × ____% / ____% = $_______

LTV:CAC Ratio = LTV / CAC
= $_______ / $_______ = _______:1

Benchmark: Minimum 3:1; healthy 4:1; exceptional 8:1+
```

### NRR Calculation
```
Monthly NRR Calculation:

Starting MRR (beginning of month):    $_______
+ Expansion MRR (upsells + upgrades): $_______
- Contraction MRR (downgrades):       $_______
- Churned MRR (cancellations):        $_______
= Ending MRR from same cohort:        $_______

NRR = Ending MRR / Starting MRR × 100
NRR = $_______ / $_______ × 100 = _______%

Benchmark: < 90% shrinking; 100%+ healthy; 120%+ exceptional
```

### Rule of 40
```
Rule of 40 Calculation:

YoY Revenue Growth Rate:   _____%
EBITDA Margin:             _____%
Rule of 40 Score:          _____%

(Growth Rate + EBITDA Margin ≥ 40 = passing)

2026 benchmark: Exceeding Rule of 40 commands 2x revenue multiple
```

## Pricing Model Decision Framework

### Decision Tree

```
Is your product viral / high-volume / self-serve?
  YES → Start with freemium; target 5-8% free→paid conversion
  NO  ↓

Is your COGS proportional to usage (tokens, compute, API calls)?
  YES → Usage-based or hybrid (base + overage)
  NO  ↓

Is your customer SMB or mid-market with predictable workflows?
  YES → Tiered subscription (Good/Better/Best)
  NO  ↓

Is your customer enterprise with complex deployment + compliance?
  YES → Enterprise license (custom ACV, annual contract)
```

### Hybrid Model Architecture
```
Example: Developer tool at scale

Starter: Free (up to 1,000 API calls/month)
  → Removes friction; generates top-of-funnel
  → Target: converts 5-8% to paid

Pro: $99/month (up to 50,000 API calls)
  → First paid tier; most common upgrade
  → Usage overage: $0.002 per call beyond 50K

Team: $499/month (up to 300,000 API calls)
  → Seats-based pricing (per 5 seats): $99 each additional 5 seats
  → Usage overage: $0.0015 per call beyond 300K

Enterprise: Custom ACV
  → Dedicated infrastructure, SLA, SSO, audit logs
  → Annual contract; no usage caps
```

## Paywall Design Templates

### Activation-Gated Paywall (recommended)
```
Flow:
1. User signs up (email only, no CC)
2. Onboarding: guided to complete ONE core value action (< 5 min)
3. Core action completed → paywall appears:

┌─────────────────────────────────────────┐
│  🎉 You just [core value action]!       │
│                                         │
│  Keep this and everything else with Pro │
│                                         │
│  ⭐⭐⭐⭐⭐ "Changed how we work"       │
│  — Sarah K., Head of Product at Stripe  │
│                                         │
│  [Annual: $79/mo]  [Monthly: $99/mo]   │
│  ← Save 20% annually                   │
│                                         │
│  ✅ Unlimited [core feature]            │
│  ✅ [Feature 2]                         │
│  ✅ [Feature 3]                         │
│  ✅ Priority support                    │
│                                         │
│        [Start Pro — $79/mo]            │
│                                         │
│       Or continue with Free →           │
└─────────────────────────────────────────┘
```

### Key Paywall Design Rules
- Show annual pricing first (anchors higher value)
- Annual toggle visible but monthly not the default
- Social proof ABOVE the CTA button (not below)
- 3 bullet points max on the paywall itself (full comparison table on pricing page)
- Primary CTA: one, clear, no competition
- "Continue with Free" is de-emphasized (smaller, lower, gray text)

## Trial Lifecycle Email Sequence (Complete)

### Day 0 — Welcome + Activation
```
Subject: Your first move in [Product] (takes 2 min)

Hi [First name],

Welcome. Here's the one thing that will make [Product] click for you:

→ [Core action, hyperlinked, takes < 2 min]

That's it. Do that today and you'll see why [X,XXX] teams use this every week.

If anything is unclear, reply to this email — I read every response.

[Your name]
[Title], [Company]
```

### Day 1 — Value Proof
```
Subject: What teams like yours did in their first week

[First name],

Teams that [completed core action] in their first 24 hours typically [outcome metric].

Here are 3 things worth exploring while your trial is fresh:
1. [Feature A] — most popular for teams in [their industry]
2. [Feature B] — saves ~[X hours] per [week/sprint]
3. [Feature C] — integrates with [tool they likely use]

Your trial is active for [N] more days.

[Your name]
```

### Day 4 — Urgency
```
Subject: 3 days left — don't lose your [data/work/setup]

[First name],

Your trial ends in 3 days.

Everything you've set up — [specific things they may have done] — will 
become read-only on Day 7 unless you upgrade.

The 1-click upgrade takes 30 seconds: [UPGRADE LINK]

If the timing isn't right, reply and I'll extend your trial. 
No forms, no sales call.

[Your name]
```

### Day 6 — Last Chance
```
Subject: Last day tomorrow

[First name],

Tomorrow your [Product] trial ends.

If you want to keep [the thing that provides core value], 
upgrade before midnight: [UPGRADE LINK]

Questions? Reply here — I'll respond within the hour.

[Your name]
```

### Day 10 — Re-engagement (data hostage)
```
Subject: Your [X reports / Y automations / Z datasets] are waiting

[First name],

You built [specific count/description of work done in trial] during your trial.

It's still there — just locked behind the free tier. 

One click to unlock it: [UPGRADE LINK]

Or if you've moved on, I completely understand. Just wanted to make sure 
you didn't lose work accidentally.

[Your name]
```

## Expansion Revenue Playbook

### Health Score Model (0–100)

Build in your analytics platform (Amplitude, Mixpanel, or custom):

```
Product engagement (40 points):
  DAU/WAU ratio            → 0–15 points
  Core feature adoption    → 0–15 points
  Integration usage        → 0–10 points

Usage vs tier limit (30 points):
  > 80% of tier limit      → 30 points (expansion signal)
  50–80%                   → 15 points
  20–50%                   → 5 points
  < 20%                    → 0 points (churn risk if persists)

Support health (20 points):
  0 support tickets        → 20 points
  1–2 tickets (resolved)   → 15 points
  3+ tickets               → 5 points
  Open unresolved tickets  → 0 points

Company signals (10 points):
  Lusha: headcount growing → 5 points
  Lusha: new funding       → 5 points
```

### Expansion Motion by Tier

```
Health ≥ 80 AND usage ≥ 80% of tier:
  → AE reaches out with ROI data within 24 hours
  → Offer: upgrade now = no downtime, prorated credit, same payment method
  → Target: upgrade within 30 days

Health 60–79 AND usage ≥ 60%:
  → Targeted in-app message + 1 email
  → Low-touch upgrade; no AE involvement unless deal > $X ACV

Health < 40:
  → CS assigned within 24 hours
  → Goal: recover health before attempting expansion
  → Track: days to health recovery; if not recovered in 30 days → churn risk flag
```

## Pricing Psychology Quick Reference

| Technique | Mechanism | Implementation |
|---|---|---|
| Price anchoring | First number sets reference | Show annual price first; show highest tier first in comparison |
| The decoy effect | Middle option looks better vs extremes | Starter: $29 · Pro: $99 · Business: $399 (Pro looks reasonable) |
| Loss framing | Losses feel 2× more painful than equal gains | "Don't lose access to your [X]" > "Keep access to your [X]" |
| Specificity | Specific numbers = credibility | "$4,200/year savings" > "save thousands" |
| Social proof | Conformity; risk reduction | "Join 8,400 teams" · Named logo bar · G2 rating widget |
| Commitment escalation | Small yes leads to bigger yes | Free tier → email capture → CC required → annual commitment |
