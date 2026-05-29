# ChatGPT Export Pro

**Export, analyze, and own your AI conversations from ChatGPT, Claude, and Gemini**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen.svg)](#)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)](#)

```
                         ___
     ___   __ _  ___    / __|___ _ _  _ __  __ _ ___
    / __| / _` |/ __|  | (_ / -_) ' \| '  \/ _` / -_)
    \___| \__, |\___|   \___\___|_||_|_|_|_\__,_\___|
          |___/
```

## Feature Comparison

| Feature                      | Free | Pro | Pro Max |
|------------------------------|:----:|:---:|:-------:|
| Max Conversations            | 50   | Unlimited | Unlimited |
| Export Markdown              | ✅   | ✅  | ✅ |
| Export HTML                  | ✅   | ✅  | ✅ |
| Export PDF                   | ❌   | ✅  | ✅ |
| Deduplication                | ✅   | ✅  | ✅ |
| Topic Classification         | ✅   | ✅  | ✅ |
| Merge Conversations          | ✅   | ✅  | ✅ |
| Cost Tracking                | ❌   | ✅  | ✅ |
| Analytics Reports            | ❌   | ✅  | ✅ |
| Web Dashboard                | ❌   | ✅  | ✅ |
| Obsidian Sync                | ❌   | ✅  | ✅ |
| CLI + GUI                    | ✅   | ✅  | ✅ |
| REST API                     | ❌   | ✅  | ✅ |
| Real-time Chart.js Dashboard | ❌   | ✅  | ✅ |
| CSV Export                   | ❌   | ✅  | ✅ |

---

## Quick Start in 30 Seconds

```bash
# 1. Install
pip install -r requirements.txt

# 2. Export your conversations
python main.py --cli --input ./downloads --output ./exports

# 3. View analytics
python main.py --cli --analytics

# 4. Start the web dashboard
python main.py --cli --serve
# Dashboard: http://localhost:8766
```

---

## Usage

### GUI Mode
```bash
python main.py
```

### CLI Mode

```bash
# Basic export
python main.py --cli --input ./downloads --output ./exports

# Deduplicate
python main.py --cli --input ./downloads --output ./exports --dedupe

# Merge conversations
python main.py --cli --merge file1.txt file2.txt --output merged.md

# Export as HTML
python main.py --cli --input ./downloads --output ./exports --format html

# Export as PDF
python main.py --cli --input ./downloads --output ./exports --format pdf

# Show statistics
python main.py --cli --input ./downloads --stats

# Show analytics report
python main.py --cli --analytics

# Show cost estimation
python main.py --cli --cost

# Generate HTML/CSV report
python main.py --cli --report html
python main.py --cli --report csv

# Start web dashboard
python main.py --cli --serve
python main.py --cli --serve --port 8766

# License management
python main.py --cli --license-status
python main.py --cli --license-activate KEY EMAIL TIER
```

### ASCII Demo

```
$ python main.py --cli --analytics

  License Status: Pro
  Conversations: Unlimited

  === ANALYTICS REPORT ===
  Total Conversations: 142
  Total Messages:      3,847
  Avg Msgs/Conv:       27.1
  Avg Length (chars):  1,234.5
  Avg Length (tokens): 308.6
  Most Active Source:  chatgpt

  Top Topics:
    - code: 47
    - design: 32
    - plan: 28
    - guide: 22
    - idea: 13

  Estimated Cost (GPT-4): $0.4823
```

---

## Web Dashboard

The web dashboard provides a real-time analytics interface with 6 tabs:

| Tab               | Description                                              |
|-------------------|----------------------------------------------------------|
| **Overview**      | KPI cards, daily activity chart, source distribution     |
| **Usage Trends**  | Daily/weekly/monthly counts, source & model breakdowns   |
| **Cost Analysis** | Cost by model, cumulative cost, monthly breakdown table  |
| **Topic Dist.**   | Topic pie chart, topic drift over time, keyword cloud    |
| **Search**        | Full-text search with highlighted results                |
| **Export**        | Export as CSV, HTML, or JSON with date filtering         |

### Screenshots

```
┌─────────────────────────────────────────────────────────┐
│  ChatGPT Export Dashboard                     🔍 Search │
├─────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│ │Over- │ │Usage │ │ Cost │ │Topic │ │Search│ │Export│ │
│ │view  │ │Trends│ │Anal. │ │Dist. │ │      │ │      │ │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ │
│                                                         │
│  ┌─── KPI Cards ─────────────────────────────────────┐  │
│  │ 142 Conv  3,847 Msgs  27.1 Avg  $0.48 Cost       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Daily Activity ────┐  ┌─── Source Dist. ──────┐  │
│  │  ▁▃▅▇▆▄▂  (Chart.js)  │  │  █ ChatGPT █ Claude   │  │
│  └────────────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | Session statistics (counts, averages, keywords) |
| `GET /api/trends` | Daily/weekly trends, source timelines, topic drift |
| `GET /api/topics` | Topic distribution (sorted by count) |
| `GET /api/costs` | Cost breakdown by model and source |
| `GET /api/costs/monthly` | Monthly cost aggregation |
| `GET /api/search?q=term` | Full-text search (requires knowledge base) |
| `GET /api/conversations` | Paginated conversation list |
| `GET /api/conversations/{id}` | Single conversation detail |
| `GET /api/export/csv` | Download all conversations as CSV |
| `GET /api/export/report` | Download analytics report as HTML |
| `GET /api/export/data?format=csv` | Filtered export with date range |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     main.py (Entry Point)                    │
│              GUI (PyQt6) / CLI (argparse)                    │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
     ┌─────▼──────┐              ┌───────▼────────┐
     │  CLI Mode   │              │   GUI Mode     │
     │ --analytics │              │  (PyQt6 App)   │
     │ --serve     │              └────────────────┘
     │ --cost      │
     └─────┬───────┘
           │
    ┌──────┴──────────────────────────────────────────────┐
    │                      src/                            │
    │                                                      │
    │  ┌─────────────────┐  ┌──────────────────────────┐   │
    │  │ export_sorter.py │  │  analyzers/              │   │
    │  │ - ExportParser   │  │  ├── session_stats.py    │   │
    │  │ - ExportOrganizer│  │  ├── trend_analyzer.py   │   │
    │  │ - ExportSorter   │  │  ├── cost_tracker.py     │   │
    │  └─────────────────┘  │  └── model_detector.py    │   │
    │                       │                           │   │
    │  ┌─────────────────┐  │  ┌────────────────────────┐   │
    │  │ license.py      │  │  │ web/                   │   │
    │  │ - HMAC keys     │  │  │ ├── app.py (FastAPI)   │   │
    │  │ - 3 tiers       │  │  │ ├── templates/         │   │
    │  └─────────────────┘  │  │ └── static/            │   │
    │                       │  └────────────────────────┘   │
    │  ┌─────────────────┐  │  ┌────────────────────────┐   │
    │  │ api/routes.py   │  │  │ exporters/              │   │
    │  │ - REST endpoints│  │  │ ├── analytics_report   │   │
    │  └─────────────────┘  │  │ └── csv_export.py      │   │
    │                       │  └────────────────────────┘   │
    │  ┌─────────────────┐  │  ┌────────────────────────┐   │
    │  │ knowledge_base  │  │  │ semantic_cluster.py    │   │
    │  │ (SQLite + FTS)  │  │  │ obsidian_sync.py       │   │
    │  └─────────────────┘  │  └────────────────────────┘   │
    └──────────────────────────────────────────────────────┘
```

---

## License Activation

```bash
# Check current license status
python main.py --cli --license-status

# Activate a license key
python main.py --cli --license-activate KEY EMAIL TIER

# Examples:
python main.py --cli --license-activate a1b2c3... user@example.com pro
python main.py --cli --license-activate a1b2c3... user@example.com pro_max
```

```
$ python main.py --cli --license-status
License Status: Free
Conversations: 42/50 used (84%)
WARNING: Approaching free limit -- Upgrade to Pro for unlimited access
Available features: export_md, export_html, dedup, topic_classify
Upgrade to Pro: https://example.com/upgrade
```

Valid tiers: `free`, `pro`, `pro_max`.

---

## Full Command Reference

```
usage: main.py [-h] [--cli] [--analytics] [--cost] [--serve]
               [--report {html,csv}] [--port PORT]
               [--license-activate KEY EMAIL TIER] [--license-status]
               [--input INPUT] [--output OUTPUT] [--stats] [--dedupe]
               [--merge MERGE [MERGE ...]] [--format {md,html,pdf}]
               [--verbose]

ChatGPT Export Pro - Export, organize, and analyze AI conversations

options:
  -h, --help                        show this help message and exit
  --cli                             Run in CLI mode
  --analytics                       Show analytics report
  --cost                            Show cost estimation
  --serve                           Start web dashboard server
  --report {html,csv}               Generate analytics report (html/csv)
  --port PORT                       Web dashboard port (default: 8766)
  --license-activate KEY EMAIL TIER Activate a license key
  --license-status                  Show current license status
  --input, -i INPUT                 Input directory (default: downloads)
  --output, -o OUTPUT               Output directory (default: exports)
  --stats                           Show file statistics
  --dedupe                          Remove duplicates
  --merge MERGE [MERGE ...]         Merge conversation files into one
  --format {md,html,pdf}            Output format (default: md)
  --verbose, -v                     Verbose output
```

---

## Output Structure

```
exports/
├── code/
│   ├── 2026-05-22/
│   │   ├── react-component.md
│   │   └── api-design.md
│   └── ...
├── design/
├── guide/
├── plan/
├── idea/
├── general/
└── export.html (if --format html)
└── export.pdf (if --format pdf)
```

---

## API Integration

```python
from src.openai_export import OpenAIExporter
from src.knowledge_base import KnowledgeBase

exporter = OpenAIExporter(api_key="sk-...")
conversations = exporter.export_conversations()

kb = KnowledgeBase("my_knowledge.db")
kb.add_conversations_batch(conversations)

results = kb.search("React component")
```

---

## Requirements

- Python 3.9+
- PyQt6 (for GUI)
- pypdf (for PDF parsing)
- beautifulsoup4 (for HTML parsing)
- weasyprint (for PDF output)
- openai (for API integration)
- sentence-transformers (for semantic clustering)
- fastapi + uvicorn (for web dashboard)
- jinja2 (for web templates)

---

## Project Structure

```
chatgpt-export/
├── main.py                       # Entry point (GUI + CLI + analytics + license)
├── cli_main.py                   # CLI-only entry point
├── build_pro.spec                # PyInstaller build spec
├── setup.py                      # PyPI packaging
├── test_all.py                   # Test runner
├── src/
│   ├── license.py                # HMAC-based license manager
│   ├── export_sorter.py          # Core export logic
│   ├── gui.py                    # PyQt6 desktop interface
│   ├── openai_export.py          # OpenAI API integration
│   ├── claude_export.py          # Claude API integration
│   ├── semantic_cluster.py       # AI-powered clustering
│   ├── knowledge_base.py         # SQLite full-text search
│   └── obsidian_sync.py          # Obsidian vault sync
│   ├── analyzers/
│   │   ├── session_stats.py      # Conversation statistics
│   │   ├── trend_analyzer.py     # Usage trends over time
│   │   ├── cost_tracker.py       # Cost estimation by model
│   │   └── model_detector.py     # AI model detection
│   ├── api/
│   │   └── routes.py             # REST API endpoints
│   ├── exporters/
│   │   ├── analytics_report.py   # HTML/CSV report generation
│   │   └── csv_export.py         # CSV export utilities
│   └── web/
│       ├── app.py                # FastAPI web application
│       ├── templates/
│       │   └── dashboard.html    # Chart.js dashboard
│       └── static/
│           ├── style.css         # Dashboard styles
│           └── chart.js          # Chart.js helpers
├── tests/
│   ├── test_export_sorter.py     # Export parser/organizer/sorter tests
│   ├── test_license.py           # License manager tests
│   ├── test_web.py               # Web dashboard tests
│   ├── test_integration.py       # End-to-end integration tests
│   └── smoke_test.py             # Post-build smoke test
├── .github/workflows/
│   └── release.yml               # GitHub Actions release pipeline
├── README.md
├── CHANGELOG.md
├── LICENSE
└── requirements.txt
```

---

## Upgrade to Pro

Unlock the full power of ChatGPT Export Pro:

| Feature | Free | Pro | Pro Max |
|---------|:----:|:---:|:-------:|
| Conversations | 50 max | Unlimited | Unlimited |
| Analytics | ❌ | ✅ | ✅ |
| Cost Tracking | ❌ | ✅ | ✅ |
| Web Dashboard | ❌ | ✅ | ✅ |
| PDF Export | ❌ | ✅ | ✅ |
| Obsidian Sync | ❌ | ✅ | ✅ |
| REST API | ❌ | ✅ | ✅ |
| Reports (HTML/CSV) | ❌ | ✅ | ✅ |

```bash
# Activate Pro
python main.py --cli --license-activate YOUR_KEY your@email.com pro

# Activate Pro Max
python main.py --cli --license-activate YOUR_KEY your@email.com pro_max

# Check your status
python main.py --cli --license-status
```

[Get a license key →](https://example.com/upgrade)

---

## License

MIT
