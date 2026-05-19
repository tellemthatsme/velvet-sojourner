# AgentForge — Contributing Guide

**Last updated:** 2026-05-17

---

## Welcome

Thanks for your interest in contributing to AgentForge! This project analyzes 843 open-source AI agent repositories and makes the findings accessible to developers, founders, and researchers.

**Ways to contribute:**
- Add new repos to the index
- Improve scoring accuracy
- Fix documentation errors
- Suggest new categories
- Report bugs
- Improve the codebase

---

## Adding New Repos

### Criteria

We accept repos that:
1. Are related to AI agents, LLMs, or AI infrastructure
2. Are publicly accessible on GitHub
3. Have at least 10 files (not empty or minimal)
4. Are not duplicates of existing repos (check clone analysis first)

### How to Submit

1. **Check if it's already included:**
   - Search `docs/repo-browser.html`
   - Or search `docs/repo-categories.json`

2. **If not found, submit via:**
   - GitHub Issue: "Add repo: [repo-name]"
   - Include the GitHub URL
   - Brief description of what the repo does

3. **We'll process it:**
   - Clone and analyze
   - Score and categorize
   - Add to next quarterly update

### Batch Submissions

If you have 5+ repos to suggest:
1. Create a text file with one URL per line
2. Submit as a GitHub Issue: "Batch add: [N] repos"
3. We'll process them in the next batch run

---

## Improving Scores

### When to Suggest Score Changes

- Repo has significantly improved since last analysis
- Repo was miscategorized
- Scoring algorithm missed important quality signals
- License status changed

### How to Report

1. Open a GitHub Issue: "Score update: [repo-name]"
2. Include:
   - Current score and tier
   - Proposed score and tier
   - Evidence (new features, improved docs, etc.)
   - Why the change is warranted

3. We'll review and update in the next release

---

## Fixing Documentation

### Types of Doc Fixes

| Type | Example | Where to Fix |
|------|---------|--------------|
| Factual error | Wrong repo count | PROJECT_STATE.md |
| Broken link | Dead URL | Any markdown file |
| Outdated info | Old pricing | GUMROAD_LISTING.md |
| Missing info | No deployment guide | docs/DEPLOYMENT_GUIDE.md |
| Typos | Spelling errors | Any file |

### How to Submit Fixes

1. **Small fixes (typos, broken links):**
   - Open a GitHub Issue
   - Describe the fix
   - We'll update directly

2. **Larger fixes (new sections, rewrites):**
   - Fork the repository
   - Make changes in a branch
   - Submit a Pull Request
   - Describe what you changed and why

---

## Suggesting New Categories

### Current Categories (32)

The top categories are:
- AI App Builders (179)
- Trading Bots (107)
- Developer Tools (27)
- MCP Servers (13)
- AI Frameworks (13)

Plus 229 uncategorized repos awaiting classification.

### How to Suggest

1. Open a GitHub Issue: "New category: [category-name]"
2. Include:
   - Category name
   - Description of what fits
   - 3-5 example repos that would fit
   - Why existing categories don't cover this

3. We'll evaluate and add if it makes sense

---

## Reporting Bugs

### What to Report

- QA tool false positives/negatives
- Scoring algorithm errors
- Web index search issues
- Docker platform bugs
- EXE build failures
- Any other unexpected behavior

### How to Report

1. Open a GitHub Issue: "Bug: [brief description]"
2. Include:
   - What you expected to happen
   - What actually happened
   - Steps to reproduce
   - Screenshots if applicable
   - Environment (OS, Python version, etc.)

---

## Feature Requests

### What We're Looking For

- New analysis metrics
- Better visualization options
- API endpoints
- Integration ideas
- Marketing improvements
- Anything that makes the product more valuable

### How to Request

1. Open a GitHub Issue: "Feature: [brief description]"
2. Include:
   - What the feature does
   - Why it's valuable
   - How it would work (if you have ideas)
   - Priority (nice-to-have vs. critical)

---

## Code Contributions

### Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd velvet-sojourner

# Set up Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Code Style

- Python: Follow PEP 8, use type hints
- Markdown: Use consistent heading levels, tables for data
- HTML: Semantic tags, accessible markup
- Commits: Descriptive messages, one change per commit

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Commit with descriptive message
6. Push to your fork
7. Open a Pull Request
8. Describe what you changed and why

### PR Requirements

- [ ] Tests pass
- [ ] No linting errors
- [ ] Description explains the change
- [ ] Screenshots for UI changes
- [ ] Documentation updated if needed

---

## Community Guidelines

### Be Respectful

- Treat all contributors with respect
- Disagree with ideas, not people
- Welcome newcomers
- Give constructive feedback

### Be Helpful

- Answer questions when you can
- Share your knowledge
- Document your work
- Help others get started

### Be Transparent

- Disclose conflicts of interest
- Be honest about limitations
- Share both successes and failures
- Credit others' contributions

---

## Recognition

Contributors are recognized in:
- PROJECT_STATE.md contributors section
- GitHub Contributors graph
- Quarterly update release notes
- Product documentation (where applicable)

---

## Questions?

If you're unsure about anything:
- Open a GitHub Issue with your question
- Visit agentforge-consulting.vercel.app
- We respond within 48 hours

Thanks for contributing!
