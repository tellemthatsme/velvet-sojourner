# AgentForge — Launch Runbook

**Status:** All assets built, docs generated, tokens stripped.  
**Sites deployed:** Consulting page + SaaS landing page live on Vercel.  
**Docker platform:** Running locally with 7 services (Traefik, Postgres, Redis, n8n, Prometheus, Grafana, Deployer).  
**Blocked (no GHCR):** LiteLLM + Open WebUI — pull on VPS with `docker compose up -d litellm open-webui`.  
**Deployer fix:** scan uses background task (no startup hang). Rebuild: `docker compose up -d --build deployer`.  
**Follow these steps to finish launching.**

---

## Step 1: Consulting Page ✅ LIVE

**URL:** https://agentforge-consulting.vercel.app  
**Status:** Deployed and aliased to production.  
**Next:** Add custom domain (e.g., `consulting.agentforge.dev`) in Vercel dashboard.

## Step 2: SaaS Landing Page ✅ LIVE

**URL:** https://agentforge-saas.vercel.app  
**Status:** Deployed and aliased to production.  
**Next:** Add custom domain in Vercel dashboard.

## Step 3: Upload Product to Gumroad (10 min)

1. Open https://app.gumroad.com
2. Create new product
3. Copy listing copy from `deploy-ready/gumroad-product/GUMROAD_LISTING.md`
4. Upload `deploy-ready/AI-Agent-Index-2026.zip` as the product file
5. Set pricing tiers:
   - **Starter:** $49 — ZIP download
   - **Professional:** $149 — ZIP + Docker platform + curated list
   - **Enterprise:** $299 — Everything + priority support + custom category
6. Set to "digital product"
7. Publish

## Step 4: Launch Docker Platform on VPS (20 min)

Using **Hetzner CX32** ($11/mo) or your preferred VPS:

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Copy the platform files
# From your local machine:
scp -r deploy-ready/agentforge-platform/ root@your-vps-ip:~/agentforge/

# Start
cd ~/agentforge
docker compose up -d

# Platform is now live at http://your-vps-ip:3000
```

**Note:** Docker images need to pull from Docker Hub/GHCR — needs a machine with stable internet.  
The TLS handshake timeout in this environment prevented image pull. Recommend Hetzner or a cheap VPS.

## Step 5: Send Outreach (30 min)

All templates ready in `deploy-ready/OUTREACH_MESSAGES.md`:

| Channel | When | Priority |
|---------|------|----------|
| LinkedIn DM | Day 1 | ⭐ High |
| Reddit (r/LocalLLaMA, r/indiehackers) | Day 1 | ⭐ High |
| Hacker News Show HN | Day 1-2 | ⭐ High |
| Twitter/X thread | Day 2 | Medium |
| Email sequence (5 emails) | Day 2-7 | Medium |
| Discord communities | Day 3 | Low |

## Step 6: Register on AI Directories

From `docs/competitor-pricing.md` — list AgentForge on:
- Futurepedia ($247 listing — best ROI per research)
- Toolify (free to list)
- TAAFT (free)
- Product Hunt (free with Ship $249 launch)

## Step 7: Set Up Payments

1. Create Stripe account at https://stripe.com
2. Integrate with Gumroad (built-in) or set up Stripe directly for consulting invoices
3. Send first consulting invoice via Stripe or PayPal

---

## File Reference

| File | Use |
|------|-----|
| `deploy-ready/consulting-page/` | Drag to Netlify → live consulting site |
| `deploy-ready/saas-landing-page/` | Import to Vercel → live SaaS site |
| `deploy-ready/agentforge-platform/` | `docker compose up` → live platform |
| `deploy-ready/AI-Agent-Index-2026.zip` | Upload to Gumroad → product for sale |
| `deploy-ready/gumroad-product/GUMROAD_LISTING.md` | Paste as product description |
| `deploy-ready/OUTREACH_MESSAGES.md` | Copy-paste for all channels |
| `docs/competitor-pricing.md` | Pricing strategy reference |
| `docs/repo-browser.html` | Searchable web index (open in browser) |
| `MASTER_REPO_DIRECTORY.md` | Full repo directory |
| `FULL_DETAILED_REPORT.md` | 10-section comprehensive report |
| `docs/curated-subsets/` | Curated CSV, top-50, by-category exports |
| `docs/expanded-repo-details/` | Detailed docs for top 50 A-tier repos |
| `docs/test-results.md` | 192 tests run, 74.5% pass rate |

---

**Revenue projection (conservative):** $6,000/mo  
**Revenue projection (moderate):** $18,400/mo  
**Revenue projection (aggressive):** $39,900/mo  

*See `deploy-ready/DEPLOY_GUIDE.md` for the original with more detail.*
