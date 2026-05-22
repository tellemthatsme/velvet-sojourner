# ChatGPT Export — Welcome Email Sequence

## Email 1 of 4 — Welcome + Installation
**Send:** Day 0 (immediately after purchase)

**Subject:** Your ChatGPT archives, exported & organized — start here

**Preview:** Install the app, export your first 5 conversations in 2 minutes

---

Thanks for purchasing **ChatGPT Export**!

You now own the fastest way to back up, search, and analyze your entire ChatGPT history.

### Download & Install

[Download ChatGPT Export →](https://gumroad.com/l/chatgpt-export/your-download-link)

**System requirements:**
- macOS 12+ or Windows 10+ (or Linux with Wine)
- 500 MB free disk space
- Python 3.10+ (for API integrations)

### Quick Export Tutorial

Here's how to export your first 5 conversations:

1. **Launch the app** — Double-click the ChatGPT Export icon
2. **Log in to ChatGPT** — The app opens a browser window; sign into your OpenAI account
3. **Select conversations** — Choose 5 conversations to export
4. **Choose format** — Select JSON (default) for maximum portability
5. **Click Export** — Your files are saved to `~/ChatGPT Exports/`

**Time elapsed: ~2 minutes.**

You can view each export as a readable markdown file in any text editor.

### What You Can Do Now

- Search all exported conversations locally
- Keep a personal backup independent of OpenAI's servers
- Share individual threads as clean markdown files

---

Start exporting,

**The Export Team**

---

[Launch App →](https://gumroad.com/l/chatgpt-export/your-download-link)

---

## Email 2 of 4 — Features Deep-Dive
**Send:** Day 2

**Subject:** HTML export, stats dashboard, and full-text search — explore your data

**Preview:** Turn your ChatGPT history into a searchable knowledge base

---

Hi,

You've got the basics down. Let's explore what ChatGPT Export can really do.

### HTML & PDF Export

Export conversations as formatted documents perfect for sharing or printing.

```bash
# Export as HTML (clean, readable web pages)
chatgpt-export export --id 123 --format html

# Export as PDF (ideal for archiving or sending to clients)
chatgpt-export export --id 123 --format pdf
```

HTML exports include syntax-highlighted code blocks, collapsible sections, and a table of contents. PDF exports are print-ready.

### Statistics Dashboard

Open the **Dashboard** tab to see:

- **Total conversations** exported
- **Messages per conversation** histogram
- **Model usage breakdown** (GPT-4 vs GPT-3.5 vs Claude)
- **Activity timeline** — when you chat most
- **Topic clusters** — auto-generated from conversation titles
- **Token count estimates** — useful for API cost projections

### Search Functionality

The built-in search indexes every word across all your exports.

- **Full-text search** — Search across all conversations in milliseconds
- **Date filters** — `from:2024-01-01 to:2024-06-30`
- **Model filters** — `model:gpt-4`
- **Regex support** — Advanced pattern matching
- **Saved searches** — Bookmark frequent queries

---

Explore more,

**The Export Team**

---

[Open Dashboard →](https://gumroad.com/l/chatgpt-export/your-download-link)

---

## Email 3 of 4 — Advanced Features
**Send:** Day 5

**Subject:** Build a personal knowledge base — SQLite, Obsidian, and API integrations

**Preview:** Sync your ChatGPT exports to Obsidian and connect OpenAI + Claude APIs

---

Hey,

You're ready for the advanced stuff. Here's how to turn your exports into a permanent knowledge system.

### SQLite FTS5 — Your Searchable Knowledge Base

ChatGPT Export can build a fully searchable local database using SQLite's FTS5 full-text search engine.

```bash
# Build the knowledge base from all exports
chatgpt-export kb build --source ~/ChatGPT\ Exports/

# Query it
chatgpt-export kb search "deployment strategies"

# Export specific results
chatgpt-export kb export --query "python async" --format markdown
```

Your entire chat history becomes a local, offline-searchable, queryable dataset.

### Obsidian Vault Sync

Turn every exported conversation into an Obsidian note — automatically.

```bash
# Sync all exports to your Obsidian vault
chatgpt-export obsidian sync --vault ~/Obsidian/MyVault

# Daily auto-sync (cron)
0 8 * * * /usr/local/bin/chatgpt-export obsidian sync --vault ~/Obsidian/MyVault
```

Each conversation becomes a formatted `.md` file with YAML frontmatter (date, model, token count) and wiki-linked tags.

### API Integrations

Connect external AI APIs for conversation analysis:

**OpenAI Integration:**
```bash
export OPENAI_API_KEY=sk-xxxxx
chatgpt-export analyze --id 123 --summary    # Auto-summarize a conversation
chatgpt-export analyze --all --topics        # Extract topics across all chats
```

**Claude Integration:**
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
chatgpt-export analyze --id 123 --insights   # Get Claude's analysis
```

- **Auto-tagging** — AI-generated tags for every conversation
- **Sentiment trends** — Track tone over time
- **Action item extraction** — Pull todos and decisions from chats

---

Build your knowledge base,

**The Export Team**

---

[Configure Integrations →](https://docs.chatgpt-export.com/integrations)

---

## Email 4 of 4 — Bundle Offer
**Send:** Day 10

**Subject:** Complete your toolkit — ChatGPT Export + GitHub Downloader + AgentForge Index

**Preview:** Save 40% when you buy all three products together

---

Hi,

You bought **ChatGPT Export**. There are two more tools that complete your AI workflow — and right now you can get all three for 40% off.

### The Complete Pipeline

```
Discover → Download → Export
   │           │           │
AgentForge  GitHub     ChatGPT
Index     Downloader   Export
```

| Step | Tool | What It Does |
|---|---|---|
| **1** | AgentForge Index | Find the best AI agent repos for your project |
| **2** | GitHub Downloader | Download those repos locally for offline access |
| **3** | ChatGPT Export | Back up, search, and analyze all your AI conversations |

### Bundle Pricing

| Product | Standalone |
|---|---|
| ChatGPT Export | $39 |
| GitHub Downloader | $29 |
| AgentForge Index | $49 |
| **Total separately** | **$117** |
| **Bundle price** | **$70** |
| **You save** | **$47 (40%)** |

### Use Code: `AIBUNDLE40`

[Get the Complete Bundle →](https://checkout.com/bundle/ai-toolkit)

*Offer expires in 5 days.*

> *"I use all three daily. The index helps me find repos, the downloader grabs them, and ChatGPT Export keeps my conversations searchable. Essential toolkit."*
> — Marcus R., AI Engineer

---

**The Export Team**

---

[Claim 40% Off Bundle →](https://checkout.com/bundle/ai-toolkit)
