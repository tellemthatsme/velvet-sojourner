# AgentForge — Revenue Guide

**Last updated:** 2026-05-17

---

## Revenue Streams Overview

AgentForge has three revenue streams, each targeting different customer segments:

| Stream | Product | Price | Target | Effort |
|--------|---------|-------|--------|--------|
| 1. Index Product | Digital research product | $49-$299 | Developers, founders | Low (passive) |
| 2. Consulting | Done-for-you deployment | $2,500 + $500/mo | Businesses, agencies | High (active) |
| 3. SaaS Platform | Self-hosted AI platform | $49-$299/mo | Teams, enterprises | Medium (build) |

---

## Stream 1: AI Agent Index Product

### Pricing Tiers

| Feature | Starter ($49) | Professional ($149) | Enterprise ($299) |
|---------|--------------|---------------------|-------------------|
| Full research product | ✓ | ✓ | ✓ |
| Catalog (MD+CSV+JSON) | ✓ | ✓ | ✓ |
| Category reports | ✓ | ✓ | ✓ |
| Quality scores | ✓ | ✓ | ✓ |
| Docker readiness flags | ✓ | ✓ | ✓ |
| Quarterly updates | ✓ | ✓ | ✓ |
| License audit report | — | ✓ | ✓ |
| Clone analysis | — | ✓ | ✓ |
| Custom filtering | — | ✓ | ✓ |
| Email support | — | 30 days | 90 days |
| Redistribution rights | — | — | ✓ |
| Custom integration | — | — | ✓ |

### Revenue Projections

| Month | Starter Sales | Pro Sales | Ent Sales | Total Revenue |
|-------|--------------|-----------|-----------|---------------|
| 1 (launch) | 10 ($490) | 3 ($447) | 1 ($299) | $1,236 |
| 2 | 15 ($735) | 5 ($745) | 2 ($598) | $2,078 |
| 3 | 20 ($980) | 7 ($1,043) | 3 ($897) | $2,920 |
| 6 (steady) | 30 ($1,470) | 10 ($1,490) | 5 ($1,495) | $4,455 |

### Upsell Paths

1. **Starter → Professional:** "Need license compliance for your team? Upgrade for full audit reports."
2. **Professional → Enterprise:** "Building a product on these repos? Get redistribution rights."
3. **Any tier → Consulting:** "Want us to deploy and configure? Book a consultation."

### Optimization Tips

- **Launch at $49** (50% off planned $99) — creates urgency
- **Raise to $79** after first 50 sales
- **Bundle with consulting** — "Buy Enterprise, get 1 hour free consulting"
- **Quarterly updates** keep customers engaged and reduce refund requests

---

## Stream 2: Consulting Services

### Pricing

| Service | Price | Deliverables |
|---------|-------|--------------|
| Setup package | $2,500 (one-time) | Docker platform deployed, LiteLLM configured, Open WebUI ready, n8n workflows |
| Monthly support | $500/mo | Monitoring, updates, troubleshooting, feature requests |
| Custom integration | $1,500+ | Custom API development, third-party integrations, training |

### Target Clients

- AI agencies building solutions for clients
- Startups needing AI infrastructure
- Enterprises evaluating agent frameworks
- Solo developers wanting production setup

### Client Acquisition

1. **LinkedIn outreach** — 50 DMs/week to AI agency founders
2. **Reddit credibility** — Active participation in r/LocalLLaMA, r/artificial
3. **Gumroad upsell** — "Need deployment help? Book a consultation" on product page
4. **Referrals** — 10% commission for existing customers who refer clients

### Revenue Projections

| Month | New Clients | Monthly Recurring | Total Revenue |
|-------|-------------|-------------------|---------------|
| 1 | 1 | $500 | $3,000 |
| 2 | 1 | $1,000 | $3,500 |
| 3 | 2 | $2,000 | $7,000 |
| 6 | 2 | $4,000 | $9,000 |

---

## Stream 3: SaaS Platform

### Pricing

| Plan | Price | Features |
|------|-------|----------|
| Starter | $49/mo | Deployer API access, 5 repo deployments, basic monitoring |
| Professional | $149/mo | Unlimited deployments, n8n workflows, LiteLLM gateway, priority support |
| Enterprise | $299/mo | Custom domains, team access, SLA, dedicated resources |

### Platform Components

- **Deployer API** — Deploy repos with one API call
- **LiteLLM Gateway** — Unified LLM API with rate limiting
- **Open WebUI** — Self-hosted ChatGPT alternative
- **n8n Workflows** — Automation and integrations
- **Monitoring** — Prometheus + Grafana dashboards

### Revenue Projections

| Month | Starter | Pro | Enterprise | MRR |
|-------|---------|-----|------------|-----|
| 1-3 | 0 | 0 | 0 | $0 (building) |
| 4-6 | 5 ($245) | 2 ($298) | 1 ($299) | $842 |
| 7-12 | 15 ($735) | 5 ($745) | 3 ($897) | $2,377 |

### Build Priority

1. Deploy Docker platform to VPS (Week 1-2)
2. Test all services locally (Week 2-3)
3. Build landing page with waitlist (Week 3-4)
4. Launch to existing customers (Month 2)
5. Public launch (Month 3)

---

## Combined Revenue Projections

| Month | Index | Consulting | SaaS | Total |
|-------|-------|------------|------|-------|
| 1 | $1,236 | $3,000 | $0 | $4,236 |
| 2 | $2,078 | $3,500 | $0 | $5,578 |
| 3 | $2,920 | $7,000 | $0 | $9,920 |
| 6 | $4,455 | $9,000 | $842 | $14,297 |
| 12 | $6,000 | $12,000 | $2,377 | $20,377 |

---

## Cost Structure

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| VPS (Hetzner) | $11 | Docker platform hosting |
| Gumroad fees | ~10% of sales | 10% + $0.30 per transaction |
| Vercel | $0 | Free tier for landing pages |
| Stripe | ~2.9% + $0.30 | Consulting payments |
| Domain | $1/yr amortized | Optional custom domain |
| **Total fixed costs** | **~$11/mo** | Before revenue share |

---

## Key Metrics to Track

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Conversion rate | 2-5% | Gumroad views to sales |
| Refund rate | <5% | Product quality indicator |
| Customer LTV | $150+ | Revenue per customer over time |
| CAC | <$10 | Cost to acquire a customer |
| MRR growth | 20%/mo | Platform revenue trajectory |
| Churn | <5%/mo | Platform retention |
