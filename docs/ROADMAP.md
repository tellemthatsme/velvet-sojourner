# AgentForge — Product Roadmap

**Last updated:** 2026-05-17

---

## Current Version: v2.2

### Shipped Features

- [x] 843 repos collected and scored (0-116 scale)
- [x] 32-category taxonomy
- [x] Batch enhancement (LICENSE, Dockerfile, .gitignore, README)
- [x] QA tool with 9 checks
- [x] 501 KB searchable web index (PWA-enabled)
- [x] 12 screenshots + animated demo GIF
- [x] Product landing page (docs/product.html)
- [x] Legal pages (terms.html, privacy.html)
- [x] Demo page (docs/demo.html)
- [x] CLI EXE rebuilt (no PyQt6, --help works)
- [x] Docker platform (7 services)
- [x] Deployer API + Python SDK
- [x] Install scripts (Linux/macOS/Windows)
- [x] Gumroad listing copy (3 tiers, 8 FAQ)
- [x] 7-channel outreach templates
- [x] Competitor pricing analysis
- [x] Clone analysis (265 clones, 6 patterns)
- [x] 837 exposed tokens stripped
- [x] Zero-cost launch content prepared
- [x] All URLs updated to Vercel (no domain cost)

---

## v2.3 — Planned (Q2 2026)

### Automated Repo Discovery

**Goal:** Automatically discover new AI agent repos.

**Features:**
- GitHub API topic search (`ai-agent`, `llm`, `mcp`)
- Trending repos monitoring
- New repo alerts
- Automatic scoring and categorization
- Monthly batch updates

**Effort:** 2-3 weeks

### Improved Scoring Algorithm

**Goal:** More accurate quality assessment.

**Improvements:**
- AST-based code quality analysis
- Dependency freshness checks
- Commit frequency weighting
- Community engagement signals (stars, forks, issues)
- AI-assisted README quality evaluation

**Effort:** 1-2 weeks

### API Marketplace

**Goal:** Allow third-party access to the catalog data.

**Features:**
- REST API for repo search and filtering
- API key management
- Rate limiting (100 requests/minute free tier)
- Webhook notifications for new repos
- Developer documentation

**Pricing:**
- Free: 100 requests/day
- Pro: 10,000 requests/day ($29/mo)
- Enterprise: Unlimited ($99/mo)

**Effort:** 2-3 weeks

### Enhanced Web Index

**Goal:** Better browsing experience.

**Features:**
- Full-text search across READMEs
- Advanced filtering (language, license, score range)
- Comparison view (side-by-side repo comparison)
- Export custom subsets
- Dark/light theme toggle
- Mobile-responsive design

**Effort:** 1-2 weeks

---

## v3.0 — Major Update (Q3 2026)

### Community Contributions

**Goal:** Allow users to contribute repos and improvements.

**Features:**
- User submission portal
- Community voting on repo quality
- User-generated categories
- Discussion forums per repo
- Contributor recognition system

**Effort:** 4-6 weeks

### Mobile App

**Goal:** Browse the index on mobile devices.

**Features:**
- React Native app (iOS + Android)
- Offline browsing
- Push notifications for new repos
- Quick search and filter
- Save favorites

**Effort:** 4-6 weeks

### Enterprise Features

**Goal:** Serve larger organizations.

**Features:**
- SSO integration
- Team access management
- Custom scoring criteria
- Private repo analysis
- Compliance reporting
- SLA guarantees

**Pricing:** Custom (starting at $999/mo)

**Effort:** 6-8 weeks

### Integration Partnerships

**Goal:** Embed AgentForge data in other tools.

**Targets:**
- VS Code extension (browse repos from editor)
- GitHub integration (score repos in search results)
- Notion template (import catalog)
- Slack bot (query repos from chat)
- CLI tool (search from terminal)

**Effort:** 2-3 weeks per integration

---

## Revenue Milestones

| Milestone | Target Date | Revenue | How |
|-----------|-------------|---------|-----|
| First sale | Week 1 | $49 | Gumroad launch |
| 10 sales | Week 2 | $490 | Reddit + HN traction |
| 50 sales | Month 1 | $2,450 | Directory listings + outreach |
| $5k MRR | Month 3 | $5,000/mo | Consulting + index + SaaS |
| $10k MRR | Month 6 | $10,000/mo | All streams active |
| $20k MRR | Month 12 | $20,000/mo | Enterprise features launched |

---

## Technical Debt

### Items to Address

1. **Git repository** — Initial commit just made, needs proper branching strategy
2. **Test coverage** — Downloader tests exist but need expansion
3. **CI/CD pipeline** — No automated testing or deployment
4. **Documentation consistency** — Multiple doc formats, needs standardization
5. **Code duplication** — Three versions of github-downloader (v2, new, src/)
6. **Dependency management** — requirements.txt needs pinning
7. **Security audit** — API endpoints need penetration testing

### Priority Order

1. Code deduplication (merge downloader versions)
2. CI/CD pipeline (automated testing)
3. Test coverage expansion
4. Dependency pinning
5. Security audit
6. Documentation standardization

---

## Competitive Landscape

### Current Position

| Competitor | What They Do | Our Advantage |
|------------|-------------|---------------|
| Awesome Lists | Curated links | We have actual analysis, not just links |
| Tool Directories | Product listings | We analyze code quality, not just features |
| GitHub Search | Raw repo search | We score, categorize, and verify |
| AI Tool Hunt | Tool discovery | We focus on developer repos, not SaaS products |

### Future Differentiation

- **Real-time scoring** — Scores update as repos change
- **Community validation** — Users confirm or dispute scores
- **Deployment success rate** — Track which repos actually deploy
- **Integration compatibility** — Which repos work together
- **Cost analysis** — Infrastructure cost estimates per repo

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| GitHub API rate limits | Medium | High | Use multiple tokens, cache results |
| Competitor copies product | High | Medium | Build community, move faster |
| Low conversion rate | High | Medium | Iterate pricing, improve marketing |
| Legal challenges (licenses) | High | Low | Sell analysis, not code; clear disclaimers |
| Platform downtime | Medium | Low | VPS monitoring, automated restarts |
| Customer churn | Medium | Medium | Quarterly updates, active support |
