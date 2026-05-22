# AgentForge — DO IT ALL Master Guide

**Last updated:** 2026-05-17  
**Goal:** Execute every launch, marketing, and growth action  
**Total cost:** $23 minimum (domain + VPS) | $0 if using free options only

---

## Phase 1: TODAY (2-3 hours, $0)

### Step 1: Upload to Gumroad (30 min)

1. Go to **gumroad.com** → Sign in
2. Click **Products** → **New Product**
3. Fill in:
   - **Name:** `AI Agent Index 2026`
   - **Type:** Digital Product
   - **Price:** $49
   - **Description:** Copy-paste entire content from `deploy-ready/gumroad-product/GUMROAD_LISTING.md`
   - **Thumbnail:** Upload `docs/screenshots/repo-index-full.png`
   - **Cover Image:** Upload `docs/screenshots/repo-browser-demo.gif`
   - **File:** Upload `deploy-ready/AgentForge-Product-v2.zip` (18 MB)
4. Set URL slug: `ai-agent-index-2026`
5. Click **Publish**
6. **Copy your Gumroad URL** — you'll need it for every post below

### Step 2: Update All Links (10 min)

Replace `agentforge-consulting.vercel.app` with your Gumroad URL in:
- `deploy-ready/LAUNCH_POSTS.md` (all 7 sections)
- `deploy-ready/OUTREACH_MESSAGES.md` (11 occurrences)
- `deploy-ready/gumroad-product/GUMROAD_LISTING.md` (2 occurrences)

Use your text editor's "Find and Replace All" function.

### Step 3: Post Show HN on Hacker News (15 min)

**Timing:** 11am-1pm ET for maximum visibility

1. Go to **news.ycombinator.com** → Click **submit**
2. **Title:** `Show HN: AI Agent Index — 843 curated, scored, and categorized AI repos`
3. **URL:** Your Gumroad URL
4. Click **submit**
5. **IMMEDIATELY** post this as the first comment:

```
I built a curated, offline research product of the open-source AI agent ecosystem. 843 repos, each cloned, analyzed, scored for quality (0-116), documented, and organized into 32 categories.

What it is:
A downloadable research product containing quality scores, license audits, Docker readiness flags, clone analysis, and a searchable catalog for 843 AI repositories. The repos themselves remain on GitHub (free to clone), but the analysis work that would take 200+ hours is done for you.

Why I built it:
The "awesome list" model is broken — it's just links. I wanted real analysis you can actually use without wondering if a repo has a license, tests, or even works.

What's inside:
- 179 AI App Builders (litellm, eliza, ClaraVerse, aider, local-operator)
- 107 Trading bots (ccxt, nautilus_trader, freqtrade)
- 27 Developer Tools, 13 MCP Servers, 13 AI Frameworks
- 572 A-Tier repos (production-ready), 168 B-Tier, 103 C-Tier
- 842/843 have Dockerfiles, 100% have README + LICENSE
- 265 likely clones identified across 6 pattern groups
- 837 exposed GitHub tokens stripped for security
- Full catalog in Markdown, CSV, and JSON

Pricing:
- Starter: $49 — Full research product + quarterly updates
- Professional: $149 — +License audit + priority support
- Enterprise: $299 — +Redistribution rights + custom integration

30-day money-back guarantee. Quarterly updates included free.

Tech:
Python pipeline → Repo cloning → AST analysis → Documentation generation → Docker testing → Scoring → Catalog export → QA scan (9 checks)

Happy to discuss the methodology, share interesting findings about the ecosystem, or answer technical questions about the pipeline.
```

**HN Rules:**
- Don't upvote your own post
- Respond to every comment within 30 minutes
- Be technical and transparent
- Don't be salesy

### Step 4: Post r/LocalLLaMA (15 min)

1. Go to **reddit.com/r/LocalLLaMA** → **Create Post**
2. **Title:** `I analyzed 843 open-source AI agent repos so you don't have to — here's the full indexed archive [OC]`
3. **Body:** Copy-paste from `deploy-ready/LAUNCH_POSTS.md` section 2
4. Post as **text post** (not link)
5. Replace URL with your Gumroad URL

### Step 5: Post Twitter/X Thread (20 min)

1. Post the 10-tweet thread from `deploy-ready/LAUNCH_POSTS.md` section 5
2. Each tweet replies to the previous one (thread)
3. Attach `docs/screenshots/repo-index-full.png` to Tweet 1
4. Tag: @litellm @openwebui @elizaOS
5. Post between 9-11am ET

---

## Phase 2: TOMORROW (1-2 hours, $0)

### Step 6: Post r/ArtificialIntelligence (15 min)

**Wait 2-4 hours after r/LocalLLaMA post**

1. Go to **reddit.com/r/ArtificialIntelligence** → **Create Post**
2. **Title:** `I curated and scored 843 open-source AI agent repositories — here's the landscape breakdown`
3. **Body:** Copy-paste from `deploy-ready/LAUNCH_POSTS.md` section 3
4. Replace URL with your Gumroad URL

### Step 7: Post r/indiehackers (15 min)

**Wait 2-4 hours after r/AI post**

1. Go to **reddit.com/r/indiehackers** → **Create Post**
2. **Title:** `I turned 843 AI agent repos into a research product — here's how I built, priced, and launched it`
3. **Body:** Copy-paste from `deploy-ready/LAUNCH_POSTS.md` section 4
4. Replace URL with your Gumroad URL

### Step 8: Submit to Directories (20 min)

**Toolify (toolify.ai):**
1. Go to toolify.ai/submit
2. Name: `AI Agent Index 2026`
3. Description: `A curated research product analyzing 843 open-source AI agent repositories. Every repo scored for quality (0-116), license-verified, Docker-tested, and organized into 32 categories.`
4. URL: Your Gumroad URL
5. Category: AI Developer Tools
6. Pricing: Paid ($49+)
7. Submit

**TAAFT (taaft.com):**
1. Go to taaft.com/submit
2. Same details as Toolify
3. Submit

**There's An AI For That:**
1. Go to theresanaiforthat.com/submit
2. Same details
3. Submit

**AI Tool Hunt:**
1. Go to aitoolhunt.com/submit
2. Same details
3. Submit

**TopAI.tools:**
1. Go to topai.tools/submit
2. Same details
3. Submit

### Step 9: Send 20 LinkedIn DMs (1 hour)

1. Open LinkedIn
2. Search for: "AI agency founder", "AI startup CTO", "AI consultant"
3. Send Message 1 from `deploy-ready/LAUNCH_POSTS.md` section 6
4. Personalize each: use their name, mention their company
5. **Don't send more than 20/day** (LinkedIn rate limits)

---

## Phase 3: THIS WEEK (Ongoing, $0)

### Step 10: Engage with Comments (Ongoing)

**Every 2 hours, check:**
- [ ] Hacker News comments on your Show HN post
- [ ] Reddit comments on all 3 posts
- [ ] Twitter replies to your thread
- [ ] LinkedIn DM responses

**Response rules:**
- Respond within 1 hour
- Thank people for positive feedback
- Address concerns with data
- Never argue — be gracious
- Answer technical questions in detail

### Step 11: Track Metrics (15 min/day)

Create a spreadsheet with these columns:

| Date | Channel | Views | Clicks | Sales | Revenue | Notes |
|------|---------|-------|--------|-------|---------|-------|
| Day 1 | Show HN | | | | | |
| Day 1 | r/LocalLLaMA | | | | | |
| Day 1 | Twitter | | | | | |
| Day 1 | Gumroad | | | | | |

**Where to find data:**
- Gumroad views/sales: gumroad.com → Analytics
- HN upvotes: news.ycombinator.com item page
- Reddit upvotes: Reddit post
- Twitter impressions: Twitter Analytics

### Step 12: Follow-Up LinkedIn DMs (30 min/day)

**Day 4:** Send Message 2 to non-responders
**Day 7:** Send Message 3 to still non-responders
**Day 14:** Send Message 4 (social proof) to remaining
**Day 21:** Send Message 5 (collaboration) as final attempt

### Step 13: Post in Discord Communities (30 min)

**Find communities:**
- LocalLLaMA Discord
- AI Agent Discord
- Indie Hackers Discord
- Python Discord

**For each:**
1. Join the server
2. Ask mods if self-promo is allowed
3. If yes, post:

```
Hey everyone! I just finished analyzing 843 open-source AI agent repos — scored them for quality (0-116), verified licenses, checked Docker readiness, and organized into 32 categories.

The full analysis is available as a research product. Happy to answer questions about the methodology or share interesting findings!

[Your Gumroad URL]
```

### Step 14: Ongoing Twitter (1-2 tweets/day)

Post about:
- Interesting repos from the index
- Data insights from the analysis
- "Did you know?" facts about the AI agent landscape
- Screenshots of the repo browser
- Build-in-public updates

---

## Phase 4: IF FIRST 10 SALES ($23 total)

### Step 15: Buy Domain ($12/year)

1. Go to **namecheap.com** or **cloudflare.com**
2. Search: `agentforge.dev`
3. Purchase ($12/year on Namecheap, ~$9.15/year on Cloudflare)
4. Point to Vercel:
   - In Vercel dashboard → Your project → Settings → Domains
   - Add `agentforge.dev`
   - Follow DNS configuration instructions

### Step 16: Deploy Docker to VPS ($11/month)

1. **Create Hetzner account:** console.hetzner.cloud
2. **Create server:**
   - Type: CX21 (2 vCPU, 4 GB RAM, 40 GB SSD) — $11/mo
   - Image: Ubuntu 24.04
   - Location: Nuremberg or Helsinki
   - Add your SSH key
3. **SSH in:** `ssh root@YOUR_VPS_IP`
4. **Install Docker:** `curl -fsSL https://get.docker.com | sh`
5. **Deploy platform:**
   ```bash
   cd /opt
   git clone <your-repo-url> agentforge
   cd agentforge/deploy-ready/agentforge-platform
   cp .env.example .env
   nano .env  # Set passwords
   docker compose up -d
   ```
6. **Verify:** `docker compose ps` — all services should be "running"

### Step 17: Set Up Stripe (Free)

1. Go to **stripe.com** → Sign up
2. Complete business verification
3. Connect to Gumroad (Gumroad → Settings → Payouts → Stripe)
4. For consulting invoices:
   - Create invoice templates in Stripe
   - Set up payment links for $2,500 setup + $500/mo

### Step 18: Configure Vercel Custom Domain (Free)

1. Vercel dashboard → agentforge-consulting project → Settings → Domains
2. Add `agentforge.dev`
3. Add DNS records at your domain registrar:
   - CNAME: `agentforge-consulting.vercel.app`
   - Or A records: `76.76.21.21`
4. Wait for SSL certificate (5-10 minutes)

### Step 19: Create Gumroad Discount Code (Free)

1. Gumroad → Products → Your product → Discounts
2. Create code:
   - **Code:** `LAUNCH50`
   - **Discount:** 50% off
   - **Limit:** 20 uses
   - **Expires:** 7 days from now
3. Share in follow-up posts and DMs

### Step 20: Set Up Gumroad Email Sequence (Free)

1. Gumroad → Products → Your product → Workflows
2. Create 4 automated emails:

**Email 1 (Immediate):** Thank you + getting started guide
**Email 2 (Day 3):** "How to get the most from your index"
**Email 3 (Day 14):** "How's it going? Any questions?"
**Email 4 (Day 25):** "Need deployment help? Book a consultation"

Templates in `docs/GUMROAD_SETUP.md`

### Step 21: Enable Gumroad Affiliates (Free)

1. Gumroad → Products → Your product → Affiliates
2. Enable affiliate program
3. Set commission: 20%
4. Reach out to AI newsletter writers, bloggers, YouTubers
5. Offer 30% commission for first 10 affiliates (limited-time incentive)

### Step 22: Build License Audit PDF (Free, 1 hour)

1. Open `qa-results/qa-report.json`
2. Extract license data for all 843 repos
3. Create a formatted PDF with:
   - Repo name
   - License type
   - Commercial use allowed (Yes/No)
   - Notes
4. Upload as Professional tier bonus file

---

## Phase 5: MONTH 2+ (Strategic Growth)

### Step 23: Futurepedia Paid Listing ($247)

1. Go to futurepedia.io
2. Click "Submit Tool"
3. Choose paid featured listing ($247)
4. Same details as free submissions
5. Featured listings get 5-10x more visibility

### Step 24: Product Hunt Ship ($249)

1. Go to producthunt.com
2. Click "Ship your product"
3. Prepare:
   - Product name: AI Agent Index 2026
   - Tagline: "843 AI repos scored, categorized, and deployable"
   - Description: From GUMROAD_LISTING.md
   - Images: 3-4 screenshots
   - First comment: Founder story
4. Schedule launch for Tuesday-Thursday (best days)
5. Rally supporters to upvote on launch day

### Step 25: Google Ads ($50-200/month)

1. Go to ads.google.com
2. Create Search campaign
3. Target keywords:
   - "AI agent frameworks"
   - "open source AI agents"
   - "LLM agent tools"
   - "AI agent directory"
4. Budget: $5/day to start
5. Landing page: Your Gumroad URL
6. Track conversions in Gumroad analytics

### Step 26: Hire VA for Outreach ($5-10/hour)

1. Post on Upwork or Fiverr
2. Job description: "Send personalized LinkedIn DMs to AI founders"
3. Provide:
   - Target list (50-100 profiles/week)
   - Message templates
   - Tracking spreadsheet
4. Goal: Scale from 20 DMs/day to 100 DMs/week

### Step 27: Open-Source the Pipeline (Free, 2-3 weeks)

1. Create separate GitHub repo: `agentforge-pipeline`
2. Include:
   - `scan_all_repos.py`
   - `qa_all_repos.py`
   - `enhance_all_repos.py`
   - `categorize_repos.py`
   - Scoring algorithm documentation
3. Add README with setup instructions
4. Post on HN: "Show HN: Open-source pipeline for analyzing GitHub repos"
5. Drives credibility and traffic to the product

### Step 28: Build API Marketplace (Free, 2-3 weeks)

1. Use existing Deployer API as foundation
2. Add endpoints:
   - `GET /api/search?q=trading` — Search repos
   - `GET /api/repos/{name}` — Get repo details
   - `GET /api/categories` — List categories
   - `GET /api/tier/{tier}` — Filter by tier
3. Add API key management
4. Rate limiting: 100 requests/day free
5. Pricing: Pro $29/mo (10k/day), Enterprise $99/mo (unlimited)

### Step 29: Community Contributions (Free, 4-6 weeks)

1. Build submission portal (simple web form)
2. Allow users to:
   - Submit new repos
   - Vote on repo quality
   - Suggest categories
   - Report errors
3. Add discussion forums per repo
4. Recognize top contributors

### Step 30: Mobile App (Free, 4-6 weeks)

1. React Native app (iOS + Android)
2. Features:
   - Browse 843 repos
   - Search and filter
   - Save favorites
   - Offline mode
   - Push notifications for new repos
3. Free to download, in-app purchase for full access

---

## Phase 6: ENTERPRISE (Long-term)

### Step 31: Enterprise Features (6-8 weeks)

- SSO integration
- Team access management
- Custom scoring criteria
- Private repo analysis
- Compliance reporting
- SLA guarantees
- Pricing: $999+/month

### Step 32: Integration Partnerships (2-3 weeks each)

| Integration | Effort | Impact |
|-------------|--------|--------|
| VS Code extension | 2 weeks | High |
| GitHub search integration | 2 weeks | High |
| Notion template | 1 week | Medium |
| Slack bot | 1 week | Medium |
| CLI tool | 1 week | Medium |

---

## Decision Matrix

### When to Raise Prices

| Milestone | Action |
|-----------|--------|
| First 10 sales | Keep $49 |
| 50 sales | Raise to $79 |
| 100 sales | Raise to $99 |
| 6 months | Evaluate based on conversion rate |

### When to Deploy VPS

| Trigger | Action |
|---------|--------|
| 0 sales | Don't deploy |
| 1-5 sales | Deploy to validate demand |
| 10+ sales | Deploy + start building SaaS |
| 50+ sales | Scale VPS, add monitoring |

### When to Hire

| Revenue | Hire |
|---------|------|
| $0-$1k/mo | Do everything yourself |
| $1k-$5k/mo | VA for outreach ($500/mo) |
| $5k-$10k/mo | Developer for API ($2k/mo) |
| $10k+/mo | Full-time team |

---

## Daily Checklist

### Morning (30 min)
- [ ] Check Gumroad sales overnight
- [ ] Respond to HN/Reddit/Twitter comments
- [ ] Check LinkedIn DM responses
- [ ] Send 20 new LinkedIn DMs

### Afternoon (30 min)
- [ ] Post 1-2 tweets
- [ ] Engage with AI community on Twitter
- [ ] Check directory submission status
- [ ] Update metrics spreadsheet

### Evening (15 min)
- [ ] Final comment check
- [ ] Plan tomorrow's outreach targets
- [ ] Note any issues to fix

---

## Success Metrics

| Metric | 30-Day Target | 90-Day Target |
|--------|--------------|---------------|
| Gumroad views | 2,000 | 10,000 |
| Gumroad sales | 20 | 100 |
| Revenue | $1,000 | $5,000 |
| HN upvotes | 50+ | 200+ (multiple posts) |
| Reddit upvotes | 100+ total | 500+ total |
| Twitter followers | 200 | 1,000 |
| LinkedIn connections | 100 new | 500 new |
| Directory listings | 5 | 10 |
| Email subscribers | 50 | 200 |
| Consulting clients | 1 | 5 |

---

## Emergency Actions

### If No Sales After 7 Days
1. Lower price to $29
2. Post in more subreddits (r/MachineLearning, r/artificial)
3. Increase LinkedIn DMs to 30/day
4. Add more screenshots to Gumroad
5. Ask for feedback from people who viewed but didn't buy

### If Refund Rate > 10%
1. Email all refunders asking why
2. Improve product description (set correct expectations)
3. Add more detail about what's included
4. Consider adding a free sample (10 repos)

### If HN Post Gets Removed
1. Read HN guidelines again
2. Rewrite title to be less promotional
3. Focus on technical methodology
4. Resubmit after 24 hours

### If Reddit Posts Get Downvoted
1. Check if subreddit allows self-promotion
2. Rewrite to be more data-focused, less salesy
3. Engage more in the community before posting
4. Try different subreddits

---

## Quick Reference URLs

| Platform | URL |
|----------|-----|
| Gumroad | gumroad.com |
| Hacker News | news.ycombinator.com |
| Reddit r/LocalLLaMA | reddit.com/r/LocalLLaMA |
| Reddit r/ArtificialIntelligence | reddit.com/r/ArtificialIntelligence |
| Reddit r/indiehackers | reddit.com/r/indiehackers |
| Twitter/X | x.com |
| LinkedIn | linkedin.com |
| Toolify | toolify.ai/submit |
| TAAFT | taaft.com/submit |
| Futurepedia | futurepedia.io |
| There's An AI For That | theresanaiforthat.com |
| AI Tool Hunt | aitoolhunt.com |
| TopAI.tools | topai.tools |
| Product Hunt | producthunt.com |
| Hetzner Cloud | console.hetzner.cloud |
| Stripe | stripe.com |
| Namecheap | namecheap.com |
| Vercel | vercel.com |

---

**Start with Phase 1. Complete each step before moving to the next. Track everything. Adjust based on results.**
