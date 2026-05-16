# Chat Exporter Documentation

## Overview

Parses, categorizes, and organizes chat exports from ChatGPT, Claude, Gemini, and other AI platforms.

## Features

- Supports TXT, MD, JSON, HTML, PDF inputs
- Detects source (ChatGPT, Claude, Gemini)
- Extracts Q&A structure and metadata
- Deduplication by content hash
- Merge broken threads
- PDF/HTML to Markdown conversion
- Keyword tagging and topic classification
- Organized output by date/source/type

## Usage

### Basic

```bash
python export_sorter.py
```

### Options

```bash
# Custom input directory
python export_sorter.py --input ./downloads

# Custom output directory
python export_sorter.py --output ./my-exports

# Show statistics only
python export_sorter.py --stats

# Deduplicate existing exports
python export_sorter.py --dedupe
```

## Input Formats

### ChatGPT Export
- JSON format from ChatGPT export
- Automatically detected

### Claude Export
- Markdown or JSON format
- Automatically detected

### Generic Text
- Look for user/assistant patterns
- First line often contains title

## Output Structure

```
exports/
├── code/
│   └── 2024-01-15/
│       └── project-setup.md
├── design/
│   └── 2024-01-14/
│       └── ui-redesign.md
├── plan/
│   └── 2024-01-13/
│       └── q1-roadmap.md
└── general/
    └── 2024-01-12/
        └── chatgpt-conversation.md
```

## Frontmatter

Exported files include YAML frontmatter:

```yaml
---
title: Project Setup Guide
source: chatgpt
date: 2024-01-15
tags: [chatgpt, code, python, setup]
model: gpt-4
exported_at: 2024-01-15T10:30:00Z
---

# Project Setup Guide

## First Prompt

> How do I set up a Python project?

## Conversation
```

## Troubleshooting

### Files Not Processed

1. Check file extension is supported (.txt, .md, .json, .html, .pdf)
2. Verify input directory exists
3. Check logs in `logs/export_sort.log`

### PDF Not Parsed

Install pypdf:
```bash
pip install pypdf
```

### HTML Not Parsed

Install beautifulsoup4:
```bash
pip install beautifulsoup4
```
