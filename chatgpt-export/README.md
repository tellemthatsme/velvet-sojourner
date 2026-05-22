# ChatGPT Export System

Export, organize, and own your AI conversations from ChatGPT, Claude, and Gemini.

## Features

- **Multi-platform support** — ChatGPT, Claude, Gemini exports
- **5 input formats** — TXT, MD, JSON, HTML, PDF
- **Deduplication** — Content-hash based duplicate removal
- **Topic classification** — Auto-tag conversations (code, design, plan, guide, idea)
- **Obsidian-compatible** — YAML frontmatter for PKM integration
- **Multiple output formats** — Markdown, HTML, PDF
- **Merge conversations** — Combine broken threads into one
- **Semantic clustering** — Group similar conversations using AI embeddings
- **Knowledge base** — SQLite with full-text search
- **Obsidian vault sync** — Export directly to your vault
- **OpenAI API integration** — Fetch conversations directly from OpenAI
- **GUI + CLI** — Desktop app or command-line interface

## Installation

```bash
pip install -r requirements.txt
```

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
```

### Direct Python
```bash
# CLI only (no PyQt6 needed)
python src/export_sorter.py --input ./downloads --output ./exports
```

## Output Structure

```
exports/
├── code/
│   ├── 2026-05-22/
│   │   ├── react-component.md
│   │   └── api-design.md
│   └── ...
├── design/
│   ├── 2026-05-20/
│   └── ...
├── guide/
├── plan/
├── idea/
├── general/
└── export.html (if --format html)
└── export.pdf (if --format pdf)
```

## API Integration

```python
from src.openai_export import OpenAIExporter
from src.knowledge_base import KnowledgeBase

# Fetch conversations from OpenAI
exporter = OpenAIExporter(api_key="sk-...")
conversations = exporter.export_conversations()

# Store in knowledge base
kb = KnowledgeBase("my_knowledge.db")
kb.add_conversations_batch(conversations)

# Search
results = kb.search("React component")
```

## Screenshots

(Screenshots coming soon — run `python main.py` to see the GUI)

## Requirements

- Python 3.9+
- PyQt6 (for GUI)
- pypdf (for PDF parsing)
- beautifulsoup4 (for HTML parsing)
- weasyprint (for PDF output)
- openai (for API integration)
- sentence-transformers (for semantic clustering)

## Project Structure

```
chatgpt-export/
├── main.py                    # Entry point (GUI + CLI)
├── src/
│   ├── export_sorter.py       # Core export logic
│   ├── gui.py                 # PyQt6 desktop interface
│   ├── openai_export.py       # OpenAI API integration
│   ├── claude_export.py       # Claude API integration
│   ├── semantic_cluster.py    # AI-powered clustering
│   ├── knowledge_base.py      # SQLite full-text search
│   └── obsidian_sync.py       # Obsidian vault sync
├── tests/
│   └── test_export_sorter.py  # 15+ unit tests
├── examples/
│   └── sample.txt             # Sample export file
├── README.md
├── CHANGELOG.md
├── LICENSE
└── requirements.txt
```

## License

MIT
