---
description: Evaluate a product or business against monetization frameworks and recommend a pricing model, unit economics targets, and paywall design. Given a product description or URL, produces a structured monetization recommendation. Use when choosing a pricing model, validating unit economics, or designing a paywall.
argument-hint: "[product name or description or URL]"
allowed-tools: Bash,Read
---

# Pricing Model Evaluation

Evaluate the monetization strategy for: $ARGUMENTS

## Step 1: Gather Context

Ask for (or infer from the product description):
- **Product type**: What does it do? What's the core value action?
- **Target customer**: B2B or B2C? Company size? Industry?
- **GTM motion**: Product-led growth (self-serve) or sales-led?
- **COGS structure**: Is cost of goods proportional to usage (tokens, compute, storage) or flat?
- **Current pricing** (if any): What's in place now?
- **Key metrics** (if known): ARPU, churn rate, CAC, trial conversion rate

## Step 2: Pricing Model Selection

Apply the decision framework from the monetization skill:

```
Question 1: Is GTM motion product-led (self-serve, viral, high-volume)?
  YES → Consider freemium as acquisition layer (not revenue model)
  
Question 2: Is COGS proportional to consumption?
  YES → Usage-based or hybrid (base + overage)
  
Question 3: SMB/mid-market with predictable, sticky workflows?
  YES → Tiered subscription (Good/Better/Best)
  
Question 4: Enterprise with compliance/procurement/legal requirements?
  YES → Enterprise license (custom ACV)
```

Recommend the **primary model** with a **secondary/hybrid layer** if appropriate.

For each candidate model, assess:
- Fit with GTM motion
- Predictability of revenue
- Alignment with customer value delivery
- Complexity to implement and manage

## Step 3: Tier and Pricing Architecture

Recommend a 3-tier structure:

```
Tier 1 — [Starter/Free]
  Price:     $[X]/mo or Free
  Limits:    [Usage/feature limits]
  Purpose:   [Acquisition / lowest-risk entry / trial]
  Target customer: [description]

Tier 2 — [Pro/Growth] ← PRIMARY REVENUE TIER
  Price:     $[X]/mo (annual: $[Y]/mo billed annually)
  Limits:    [Usage/feature limits]
  Purpose:   [Core revenue; most customers land here]
  Target customer: [description]
  Highlight: YES (middle tier gets visual emphasis)

Tier 3 — [Business/Scale]
  Price:     $[X]/mo (annual: $[Y]/mo)
  Limits:    [Higher limits]
  Purpose:   [Upsell target; makes Tier 2 look reasonable]
  Target customer: [description]

Tier 4 — Enterprise (if applicable)
  Price:     Custom ACV
  Contract:  Annual
  Includes:  SSO, SLA, audit logs, dedicated support
```

Pricing psychology rules applied:
- Tier 3 priced 3–5× Tier 2 (anchors Tier 2 as the obvious choice)
- Annual discount = 20% (2.4 months free)
- Show annual pricing first in UI

## Step 4: Unit Economics Targets

Calculate and recommend targets:

```
Given inputs or reasonable estimates:

Target ARPU (Tier 2):         $_______/mo
Estimated gross margin:        _____%  (SaaS target: > 70%)
Target monthly churn:         _____%  (target: < 2%)

Derived targets:
  LTV = ARPU × GM% / Churn
  LTV = $_____ × ___% / ___% = $______

  Target CAC ceiling (for LTV:CAC ≥ 3:1):
  Max CAC = LTV / 3 = $______

  Target CAC payback period: < [12/18/24] months
  (based on GTM motion: PLG < 6mo, SMB 6-12mo, enterprise 18-24mo)

NRR target: ≥ 110% (plan for expansion revenue from Day 1)
Rule of 40 target: ≥ 40 (growth% + EBITDA margin%)
```

## Step 5: Trial and Paywall Design

Recommend:

**Trial type**: Opt-in (higher volume, 8.9% conversion) vs CC-required (lower volume, 31.4% conversion)
- Recommendation based on: price point, GTM motion, volume goals

**Trial length**: [7 / 14 / 30 days]
- Rule: Shorter is usually better — longer trials ↔ more procrastination
- For high-ARPU products: 14 days with hands-on onboarding > 30-day free trial

**Paywall timing**: Show paywall at the moment of core value delivery (Day 0 best; drops 50%+ after Day 7)

**Paywall structure recommendations**:
- Social proof element (review + rating + customer count)
- Annual/monthly toggle (annual as default)
- 3-point value summary (not 10 features — pick the 3 that matter most)
- One primary CTA

## Step 6: Expansion Revenue Plan

Recommend expansion levers for NRR > 110%:

```
Lever 1 — Usage expansion (if usage-based element exists):
  Trigger: usage reaches 80% of tier limit
  Action: in-app prompt + AE email with ROI data

Lever 2 — Seat expansion (if team product):
  Trigger: team size grows (monitor via product telemetry)
  Action: automated outreach when new team members onboarded in-product

Lever 3 — Feature upsell:
  Trigger: user attempts a gated feature
  Action: in-context upgrade prompt with specific value of unlocked feature

Lever 4 — Cross-sell (if portfolio exists):
  Trigger: X months of healthy usage in Product A
  Action: CS introduces Product B with existing customer discount
```

## Step 7: Validation Experiment Plan

Before committing to pricing architecture:

```
Experiment 1: Willingness-to-pay survey
  Method: Van Westendorp Price Sensitivity Analysis
  Sample: 20–50 existing free users or recent churns
  Question set: "too cheap / cheap / expensive / too expensive" for 4 price points
  Output: optimal price band with confidence

Experiment 2: Trial conversion by paywall timing
  A: Show paywall at Day 0 (post-activation)
  B: Show paywall at Day 3
  C: Show paywall at Day 7 (trial end)
  Metric: Trial-to-paid conversion rate
  Sample: 200+ trial starts per variant for statistical significance

Experiment 3: Annual vs monthly framing
  A: Annual pricing shown first, monthly toggle below
  B: Monthly pricing shown first, annual toggle below
  Metric: ARPU at 30 days (annual purchases count as higher ARPU)
  Expected lift: +20% ARPU from annual-first framing
```

## Final Recommendation

```
PRICING MODEL RECOMMENDATION: [Product Name]

PRIMARY MODEL:  [Freemium / Tiered / Usage-based / Hybrid]
SECONDARY:      [Expansion via seats / usage / cross-sell]
GTM FIT:        [PLG / Sales-led / Both]

RECOMMENDED TIERS:
  Starter:    $[X]/mo — [key limit]
  Pro:        $[X]/mo — [key limit] ← HIGHLIGHT THIS
  Business:   $[X]/mo — [key limit]
  Enterprise: Custom ACV

UNIT ECONOMICS TARGETS:
  ARPU (Pro):     $[X]/mo
  Target LTV:     $[X]
  Max CAC:        $[X] (for 3:1 ratio)
  Payback target: [X] months
  NRR target:     ≥ 110%

TRIAL:          [Type] | [Length] days | Paywall at [timing]

TOP 3 ACTIONS TO TAKE NOW:
  1. [Most important immediate action]
  2. [Second action]
  3. [Validation experiment to run first]
```
