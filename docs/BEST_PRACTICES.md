# AgentForge — Best Practices Guide

**Last updated:** 2026-05-17

---

## Using the AI Agent Index

### How to Evaluate Repos

1. **Start with A-Tier repos** (572 total, score 57+)
   - These are production-ready with good documentation
   - Examples: litellm, open-webui, ccxt, nautilus_trader

2. **Check the license** before using commercially
   - MIT/Apache 2.0: Safe for commercial use
   - GPL: Can use commercially but must share source
   - No license: Contact author before using

3. **Review the Dockerfile**
   - If present, the repo is likely deployable
   - Check for multi-stage builds (best practice)
   - Verify base image versions are pinned

4. **Check test coverage signals**
   - Look for `tests/` directory
   - Check for CI/CD configuration
   - Run tests locally before deploying

### When to Use Each Tier

| Tier | Score | Use Case | Effort Required |
|------|-------|----------|-----------------|
| A-Tier | 57+ | Production deployment | Low — deploy and go |
| B-Tier | 38-56 | Learning, prototyping | Medium — fix docs, add tests |
| C-Tier | <38 | Research, inspiration | High — significant work needed |

---

## Combining Frameworks

### Popular Combinations

| Use Case | Frameworks | Why |
|----------|-----------|-----|
| LLM API Gateway | litellm + open-webui | Unified API + chat UI |
| Trading Bot | ccxt + nautilus_trader | Exchange access + strategy engine |
| Agent Platform | eliza + MCP servers | Multi-agent + tool ecosystem |
| Workflow Automation | n8n + custom agents | Visual workflows + AI |
| Code Assistant | aider + local-operator | AI coding + local execution |

### Integration Tips

1. **Use LiteLLM as the API layer** — One endpoint for all LLM calls
2. **Containerize everything** — Each service in its own container
3. **Use Docker networks** — Services communicate internally
4. **Shared database** — Postgres for all services
5. **Centralized logging** — Aggregate logs for debugging

---

## Docker Deployment Tips

### Before Deploying

1. **Test locally first:**
   ```bash
   docker build -t my-repo .
   docker run -p 8080:8080 my-repo
   ```

2. **Check resource requirements:**
   ```bash
   docker stats
   # Monitor CPU, memory, network usage
   ```

3. **Pin image versions:**
   ```dockerfile
   # Good
   FROM python:3.11-slim

   # Bad
   FROM python:latest
   ```

### Production Deployment

1. **Use docker-compose for multi-service apps**
2. **Set resource limits:**
   ```yaml
   services:
     app:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```
3. **Use health checks:**
   ```yaml
   services:
     app:
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```
4. **Set up log rotation:**
   ```yaml
   services:
     app:
       logging:
         driver: json-file
         options:
           max-size: "10m"
           max-file: "3"
   ```

---

## License Compliance Workflow

### Step 1: Identify License

Use the license audit report to find repos with clear licenses:
- MIT: 716 repos
- Apache 2.0: Check report
- GPL: Check report
- CC0: Check report

### Step 2: Verify Compliance

For each license type:
- **MIT:** Include copyright notice in your product
- **Apache 2.0:** Include license + notice of changes
- **GPL:** Share your source code under GPL
- **CC0:** No requirements

### Step 3: Document Usage

Keep a record of:
- Which repos you're using
- Their license type
- How you're complying with terms

---

## Using Catalog Exports

### Markdown Catalog

Best for: Reading, sharing, documentation

```bash
# Search for specific repos
grep -i "trading" docs/repo-browser.html
```

### CSV Export

Best for: Importing into spreadsheets, databases, Notion

```python
import pandas as pd
df = pd.read_csv('docs/curated-subsets/all-repos.csv')
# Filter by tier
a_tier = df[df['tier'] == 'A']
# Filter by category
trading = df[df['category'] == 'Trading Bots']
```

### JSON Export

Best for: Programmatic access, API integration

```python
import json
with open('docs/repo-categories.json') as f:
    data = json.load(f)
# Access by category
ai_builders = data['categories']['AI App Builders']
```

---

## Quarterly Update Process

### What Gets Updated

1. **New repos** — Discover and add new AI agent repos
2. **Score updates** — Re-score existing repos for changes
3. **Category updates** — Reclassify uncategorized repos
4. **License updates** — Check for new or changed licenses
5. **Clone detection** — Identify new duplicate repos

### How to Run Updates

```bash
# 1. Download new repos
python download_missing.py

# 2. Enhance new repos
python enhance_all_repos.py

# 3. Run QA
python qa_all_repos.py --json

# 4. Re-score
python scan_all_repos.py

# 5. Update catalog
python build_html.py

# 6. Package new version
python package_product.py
```

### Communicating Updates

Email customers with:
- What changed (new repos, score updates)
- Download link for updated product
- Changelog of improvements

---

## Avoiding Common Pitfalls

### Pitfall 1: Deploying C-Tier Repos to Production

**Problem:** C-Tier repos need significant work before production use.

**Solution:** Only deploy A-Tier repos directly. Use B-Tier for prototyping. Treat C-Tier as research material.

### Pitfall 2: Ignoring License Terms

**Problem:** Using GPL-licensed code in proprietary products.

**Solution:** Always check the license report before using any repo commercially. When in doubt, contact the author.

### Pitfall 3: Not Testing Before Deploying

**Problem:** Assuming Dockerfile means "works out of the box."

**Solution:** Always test locally first. Check logs, resource usage, and functionality before deploying to production.

### Pitfall 4: Overlooking Clone Duplicates

**Problem:** Deploying the same repo twice under different names.

**Solution:** Check the clone analysis report (`docs/CLONE_ANALYSIS.md`) before selecting repos. 265 repos are likely clones.

### Pitfall 5: Skipping Security Review

**Problem:** Deploying repos without checking for hardcoded secrets.

**Solution:** Run a security scan before deploying:
```bash
# Check for hardcoded tokens
grep -r "ghp_\|sk-\|token" repos/<repo-name>/
```

### Pitfall 6: Not Monitoring Deployed Services

**Problem:** Deploying and forgetting — services crash without notice.

**Solution:** Use the built-in monitoring (Prometheus + Grafana) to track:
- CPU and memory usage
- Request latency
- Error rates
- Uptime
