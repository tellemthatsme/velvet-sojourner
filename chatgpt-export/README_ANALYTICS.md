# ChatGPT Export — Analytics & Dashboard

## Overview

The analytics layer provides usage statistics, cost estimation, trend analysis, and a web dashboard for exploring your AI conversation exports.

## CLI Usage

```bash
# Show full analytics report
python main.py --cli --analytics

# Show cost estimation only
python main.py --cli --cost

# Export analytics report as HTML
python main.py --cli --report html

# Export analytics report as CSV
python main.py --cli --report csv

# Start the web dashboard
python main.py --cli --serve

# Start web dashboard on custom port
python main.py --cli --serve --port 8888
```

## Web Dashboard

The web dashboard provides a full GUI for exploring your analytics:

```
http://localhost:8766
```

### Tabs

| Tab | Description |
|-----|-------------|
| **Overview** | Stat cards, daily activity chart, source distribution, recent conversations |
| **Usage Trends** | Conversations over time (daily/weekly/monthly), source breakdown, model usage |
| **Cost Analysis** | Cost by model bar chart, cumulative cost area chart, monthly cost table |
| **Topic Distribution** | Topic pie chart, topic trend (first half vs second half), keyword cloud |
| **Search** | Full-text search across all conversations with highlighted results |
| **Export** | Export as CSV, HTML report, or JSON; filtered export by date range |

## API Endpoints

All API endpoints are prefixed with `/api`.

### Stats
```
GET /api/stats
```
Returns: total_conversations, total_messages, avg_messages_per_conv, avg_length_chars, avg_length_tokens, most_common_topics, most_active_source, top_keywords, activity_by_hour, activity_by_day

### Trends
```
GET /api/trends
```
Returns: daily/weekly counts, peak days, source timeline, topic drift, date range

### Topics
```
GET /api/topics
```
Returns: list of [topic, count] tuples sorted by frequency

### Costs
```
GET /api/costs
```
Returns: total conversations, total tokens, total cost, breakdown by model and source

### Monthly Costs
```
GET /api/costs/monthly
```
Returns: cost breakdown grouped by month (month, count, total_tokens, total_cost)

### Conversations
```
GET /api/conversations?page=1&per_page=50
```
Returns: paginated list of conversations with total count and page info

### Conversation Detail
```
GET /api/conversations/{id}
```
Returns: full conversation data by ID

### Search
```
GET /api/search?q=query&limit=50
```
Returns: full-text search results with highlighted snippets

### Export CSV
```
GET /api/export/csv
```
Returns: all conversations as CSV download

### Export Report
```
GET /api/export/report
```
Returns: analytics report as HTML download

### Filtered Export
```
GET /api/export/data?format=csv&start=2026-01-01&end=2026-12-31
```
Returns: conversations filtered by date range in specified format (csv/html/json)

## Report Export Formats

### HTML Report
- Dashboard-style layout with stat cards
- Chart.js charts for daily activity, cost by model, and topic distribution
- Topic distribution table
- Self-contained HTML file (loads Chart.js from CDN)

### CSV Report
- Flat metrics in key-value format
- One row per metric
- Topic counts as separate rows

### CSV Conversation Export
- One row per conversation
- Columns: id, title, date, source, model, topic, tokens, estimated_cost, message_count

## Architecture

```
src/
├── analyzers/
│   ├── cost_tracker.py      # Cost estimation per model
│   ├── model_detector.py    # Model detection from text/content
│   ├── session_stats.py     # Session statistics computation
│   └── trend_analyzer.py    # Trend analysis (daily/weekly, topics)
├── api/
│   └── routes.py            # FastAPI router with all API endpoints
├── exporters/
│   ├── analytics_report.py  # HTML/CSV report generation
│   └── csv_export.py        # CSV export of conversations
├── web/
│   ├── app.py               # FastAPI application with web dashboard
│   ├── static/
│   │   ├── chart.js         # Chart.js dark theme helpers
│   │   └── style.css        # Dark theme dashboard styling
│   └── templates/
│       └── dashboard.html   # Jinja2 dashboard template
└── export_sorter.py         # Core export and classification
```
