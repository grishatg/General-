---
name: monetization
description: Guide pricing strategy, monetization model selection, unit economics analysis, paywall design, and revenue expansion. Use when choosing a pricing model, designing a paywall, calculating unit economics, analyzing NRR, planning trial conversion, or building expansion revenue strategy. Triggers include: 'pricing', 'monetize', 'paywall', 'freemium', 'subscription', 'usage-based', 'LTV', 'CAC', 'NRR', 'churn', 'revenue', 'ARR', 'MRR', 'expansion', 'trial', 'conversion', 'unit economics', 'Rule of 40', 'payback period'. Do NOT use for sales outbound (sales-automation) or marketing copy (marketing-growth).
license: MIT
---

# Monetization

Pricing and revenue strategy grounded in 2026 SaaS benchmarks. NRR is the single most important metric in this decade.

## Pricing Model Selection

Choose based on your go-to-market motion and customer type. Hybrid is usually optimal at scale.

| Model | Best For | Conversion | Revenue Predictability | Risk |
|---|---|---|---|---|
| Freemium | PLG, viral, high-volume | 5–8% free→paid | Low | High CAC if viral loop fails |
| Tiered subscription | SMB self-serve, sticky workflows | 31% (CC required) | High | Limits heavy users; churn risk |
| Usage-based | AI/API products, dev tools | Variable | Low | Bill shock; hard to forecast |
| **Hybrid (recommended)** | Scale-stage SaaS | Higher ARPU | Medium-High | Complexity |
| Enterprise license | Compliance-heavy, complex deployment | Long cycle | High | Slow to scale |

**Hybrid model** (base subscription + usage overage):
- Provides predictable base MRR
- Captures revenue from heavy users who would cap out on tiered plans
- Reduces bill shock vs pure usage-based
- Example: "Starts at $299/mo for 10,000 API calls; $0.03 per call beyond"

**2026 trend**: Usage-based growing at parity with subscriptions. AI SaaS especially shifting to usage-based to recover inference costs. If your COGS is per-token or per-compute-unit, usage-based aligns incentives.

## Unit Economics: The Numbers That Matter

### LTV:CAC Ratio

```
CAC (Customer Acquisition Cost)
  = Total Sales + Marketing Spend ÷ New Customers Acquired

LTV (Lifetime Value)
  = ARPU × Gross Margin % ÷ Monthly Churn Rate

LTV:CAC Ratio = LTV ÷ CAC
```

**Thresholds**:
- < 3:1 → value destruction; pause growth spend and fix retention first
- 3:1 → floor; minimum acceptable for continued investment
- 4:1 → healthy; moderate growth acceleration appropriate
- 8:1+ → exceptional; may signal underinvestment in acquisition

### CAC Payback Period

```
Payback Period (months) = CAC ÷ (ARPU × Gross Margin %)
```

**Targets by motion**:
- PLG / self-serve: < 6 months
- SMB sales-led: 6–12 months
- Enterprise sales-led: 18–24 months
- **Warning**: > 30 months → pause growth spend; fix economics first

**2026 benchmark**: Top-quartile CAC payback period = 16 months across SaaS.

### Net Revenue Retention (NRR) — The Most Important Metric

```
NRR = (Starting MRR + Expansion MRR - Contraction MRR - Churned MRR) ÷ Starting MRR
```

| NRR | Interpretation | Action |
|---|---|---|
| < 90% | Shrinking base; growth requires more new logos just to stand still | Fix retention immediately; deprioritize acquisition |
| 90–100% | Stable; requires new logos to grow | Invest in expansion motions |
| 100–110% | Healthy expansion; modest compounding | Scale acquisition |
| 110–120% | Strong; product-market fit confirmed in existing base | Aggressive growth appropriate |
| **120%+** | **Top quartile; compounding engine** | **Commands 21× EV/revenue vs 9× below 120%** |

**2026 SaaS benchmarks**: Median NRR = 82% (compressed from historical 100%+). Upper quartile = 97%. Companies > 120% NRR are exceptionally rare and exceptionally valued.

### Rule of 40

```
Rule of 40 = Revenue Growth Rate % + EBITDA Margin %  ≥  40
```

**2026 context**: Profitability is now weighted more heavily than growth. Companies consistently exceeding Rule of 40 command 2× revenue multiples vs peers. Pure growth without profitability is no longer rewarded at the same multiples.

## Trial-to-Paid Conversion

### Benchmarks by Trial Type

| Trial Type | Conversion Rate | Note |
|---|---|---|
| Opt-in (no CC required) | 8.9% | High volume, lower quality |
| Credit-card required | 31.4% | Lower volume, higher quality |
| Top-performing apps | 20–30% | Achievable with good activation |

### The Most Important Variable: Timing of Paywall

Day-0 paywall (shown immediately after core value demonstrated) converts at the highest rate. Conversion drops 50%+ after Day 7.

**Activation-gated paywall** (best practice):
1. User signs up → immediately guided to core value action
2. Core value action completed → paywall shown ("You just experienced X. Keep it with Pro.")
3. Do NOT show paywall before value is demonstrated

### Paywall Design Tactics That Move the Needle

| Tactic | Lift |
|---|---|
| Personalization (user's name in paywall) | +17% |
| Animated vs static paywall | 2.9× higher conversion |
| Annual/monthly toggle (shows annual by default) | +20%+ ARPU |
| Social proof (5-star reviews) above CTA | +10–15% |
| 3 plans (not 2, not 5) | Reduces choice paralysis |
| Price anchor (highest price shown first) | +8–12% on mid-tier |

### Trial Lifecycle Email Sequence

```
Day 0:   Welcome + "Your first action" (activation guide)
Day 1:   Value proof (what others achieved in their first week)
Day 4:   "Your trial ends in 3 days" + specific features to try
Day 6:   "Tomorrow is your last day" + single-click upgrade link
Day 7:   Trial end → downgrade to free tier (DO NOT delete data)
Day 10:  "Your [feature] is still waiting" (data hostage re-engagement)
Day 30:  "Here's what you missed in the last month" (win-back)
```

**Critical**: Downgrade to free tier, not account deletion. Data hostage (access-restricted saved work) is the highest-converting upgrade prompt.

## Expansion Revenue Strategy

**Target**: 30% of total ARR from expansion. Current SaaS median: 10%.

Expansion is 60–70% easier to close than new logos. Yet most SaaS companies spend 90% of sales resources on new logos.

**Expansion types**:
- **Upsell**: Higher tier (more seats, higher usage limits, premium features)
- **Cross-sell**: Adjacent products in your portfolio
- **Renewal uplift**: Annual contract renewal at higher price
- **Usage expansion**: Customer grows into higher usage tier organically

**Expansion playbook**:

```
Health score ≥ 80 AND usage ≥ 80% of tier limit:
  → Create expansion opportunity in CRM
  → AE sends usage data + ROI summary
  → Offer upgrade with "no downtime, same card" framing
  → Target: upgrade within 30-day window

Health score ≤ 40:
  → CS proactive outreach within 24 hours
  → Book success call; identify adoption blockers
  → Do not attempt upsell until health > 60
```

**Expansion metrics**:
- Expansion MRR as % of new MRR (target: > 30%)
- Upsell rate (% of customers who upgrade per quarter; target: > 10%)
- Net seat expansion per account per year (enterprise target: +20%)

See [playbook.md](references/playbook.md) for complete unit economics templates, paywall design examples, and validation experiment frameworks.
