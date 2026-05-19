# AgentForge — Gumroad Setup Guide

**Last updated:** 2026-05-17

---

## Overview

This guide walks you through setting up the AI Agent Index 2026 on Gumroad — from account creation to first sale.

**What you need:**
- Product ZIP file (`deploy-ready/AgentForge-Product-v2.zip`, 18 MB)
- Gumroad listing copy (`deploy-ready/gumroad-product/GUMROAD_LISTING.md`)
- Screenshot for cover image (`docs/screenshots/repo-index-full.png`)
- 30 minutes

---

## Step 1: Create Gumroad Account

1. Go to **gumroad.com**
2. Click **Start Selling** (or **Sign In** if you have an account)
3. Sign up with email or Google account
4. Complete profile:
   - Display name: `AgentForge`
   - Profile photo: Use AgentForge logo or favicon
   - Bio: `Curated research on 843 open-source AI agent repositories. Scored, categorized, deployable.`

---

## Step 2: Create Product

1. Click **Products** in the left sidebar
2. Click **New Product**
3. Fill in:
   - **Name:** `AI Agent Index 2026`
   - **Type:** Digital Product
   - **Price:** $49
   - **Description:** Paste content from `deploy-ready/gumroad-product/GUMROAD_LISTING.md`
     - Use the formatted markdown version
     - Include all sections: What You're Getting, Key Features, Pricing Tiers, FAQ
   - **Thumbnail:** Upload `docs/screenshots/repo-index-full.png` (18 KB)
   - **Cover Image:** Upload `docs/screenshots/repo-browser-demo.gif` (12 KB, animated)
   - **File:** Upload `deploy-ready/AgentForge-Product-v2.zip`
4. Click **Save Draft**

---

## Step 3: Configure Pricing Tiers

Gumroad uses "Versions" for multiple pricing tiers.

1. In product settings, go to **Versions** tab
2. Add three versions:

### Version 1: Starter
- **Name:** Starter
- **Price:** $49
- **Description:** Full research product + quarterly updates. Includes searchable catalog (MD+CSV+JSON), quality scores, Docker readiness flags, and category reports.
- **File:** `AgentForge-Product-v2.zip`

### Version 2: Professional
- **Name:** Professional
- **Price:** $149
- **Description:** Everything in Starter + full license audit report (843 repos), clone analysis (265 clones in 6 groups), custom filtering, and 30 days of email support.
- **File:** `AgentForge-Product-v2.zip` + `deploy-ready/gumroad-product/license-audit.pdf` (create this from QA report)

### Version 3: Enterprise
- **Name:** Enterprise
- **Price:** $299
- **Description:** Everything in Professional + redistribution rights for your own products, 90 days of priority support, and custom integration assistance.
- **File:** Same as Professional + redistribution license document

---

## Step 4: Configure Product Settings

### URL Slug
- Set to: `ai-agent-index-2026`
- Final URL: `gumroad.com/l/ai-agent-index-2026`

### Call to Action
- Button text: `I want this!`
- Pre-purchase question: `What's your primary use case?` (dropdown: Research, Building a product, Consulting, Other)

### Receipt Message
```
Thanks for purchasing the AI Agent Index 2026!

Your download includes:
- Searchable catalog (Markdown + CSV + JSON)
- Quality scores for all 843 repos
- License audit reports
- Docker readiness flags
- 32 category reports
- Clone analysis

Quarterly updates will be sent to this email address.

Need help? Reply to this email or visit agentforge-consulting.vercel.app
```

### Enable Features
- [x] Allow customers to pay what they want (minimum $49)
- [x] Offer discount codes (for launch promotions)
- [ ] Enable affiliate program (optional, 20% commission)

---

## Step 5: Set Up Email Sequence

Gumroad allows automated follow-up emails.

### Email 1: Immediate (Thank You)
Already configured in receipt message above.

### Email 2: Day 3 (Getting Started)
**Subject:** Getting the most from your AI Agent Index

```
Hey,

Hope you're enjoying the AI Agent Index 2026!

Here's how to get started:
1. Open the CSV file in a spreadsheet
2. Filter by your category of interest
3. Sort by score (descending)
4. Check license compatibility
5. Clone the top repos from GitHub

Need help? Reply to this email.

Cheers,
AgentForge Team
```

### Email 3: Day 14 (Check-in)
**Subject:** How's the index working for you?

```
Hey,

It's been two weeks since you got the AI Agent Index.

Quick questions:
- Have you found any repos you didn't know about?
- Is the scoring system helpful for your decisions?
- Anything we could improve?

Reply and let me know — I read every response.

Also: if you're building something with these repos, I'd love to feature it.

Cheers,
AgentForge Team
```

### Email 4: Day 25 (Upsell)
**Subject:** Need deployment help?

```
Hey,

Quick note — if you're looking to actually deploy any of these repos, we offer done-for-you setup starting at $2,500.

Includes: Docker platform deployed, LiteLLM configured, Open WebUI ready, n8n workflows set up.

Book a call: agentforge-consulting.vercel.app

Cheers,
AgentForge Team
```

---

## Step 6: Publish

1. Review all settings
2. Click **Publish**
3. Test the purchase flow (buy your own product with a test account)
4. Verify download works
5. Verify email sequence triggers

---

## Step 7: Analytics Setup

### Track Key Metrics

| Metric | Where to Find | Target |
|--------|--------------|--------|
| Views | Gumroad Analytics | 500+/month |
| Sales | Gumroad Analytics | 10+/month |
| Conversion rate | Sales ÷ Views | 2-5% |
| Refund rate | Gumroad Analytics | <5% |
| Average order value | Revenue ÷ Sales | $80+ |

### Create Discount Codes

For launch promotion:
- **Code:** `LAUNCH50`
- **Discount:** 50% off (makes Starter $24.50)
- **Limit:** First 20 uses
- **Expires:** 7 days from launch

---

## Optimization Tips

### Cover Image
- Use a screenshot showing the repo browser interface
- Add text overlay: "843 AI Repos · Scored · Categorized"
- Keep it under 200 KB for fast loading

### Description
- Lead with the value proposition (save 200+ hours)
- Use bullet points, not paragraphs
- Include social proof (even if early: "designed for 100+ developers")
- End with clear CTA

### Pricing
- Start at $49 (launch price)
- Raise to $79 after 50 sales
- Raise to $99 after 100 sales
- Communicate price increases in advance

### Affiliate Program
- Enable 20% commission for affiliates
- Reach out to AI newsletter writers
- Offer higher commission (30%) for first 10 affiliates
