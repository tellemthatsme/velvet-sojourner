# CHATGPT EXPORT SYSTEM — ENHANCEMENT PLAN

**Goal:** Launch-ready in 6 weeks  
**Current quality:** 5/10 → **Target:** 8.5/10

---

## WEEK 1: FOUNDATION (20 hours)

### Step 1: Extract to Standalone Project
```powershell
# Create new project structure
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export"
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export\src"
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export\tests"
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export\docs"
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export\assets"
New-Item -ItemType Directory -Path "C:\temp\velvet-sojourner\chatgpt-export\examples"

# Copy core script
Copy-Item "C:\temp\velvet-sojourner\projects\ai-automation-stack\export_sorter.py" "C:\temp\velvet-sojourner\chatgpt-export\src\export_sorter.py"
```

### Step 2: Add Test Suite
Create `tests/test_export_sorter.py`:
```python
import pytest
from src.export_sorter import ExportSorter

class TestExportSorter:
    def test_parse_txt(self):
        sorter = ExportSorter()
        result = sorter.parse_txt("examples/sample.txt")
        assert len(result) > 0
    
    def test_parse_md(self):
        sorter = ExportSorter()
        result = sorter.parse_md("examples/sample.md")
        assert len(result) > 0
    
    def test_parse_json(self):
        sorter = ExportSorter()
        result = sorter.parse_json("examples/sample.json")
        assert len(result) > 0
    
    def test_deduplication(self):
        sorter = ExportSorter()
        conversations = [
            {"content": "Hello world", "hash": "abc123"},
            {"content": "Hello world", "hash": "abc123"},
            {"content": "Different content", "hash": "def456"}
        ]
        result = sorter.deduplicate(conversations)
        assert len(result) == 2
    
    def test_topic_classification(self):
        sorter = ExportSorter()
        conversation = {"content": "How do I build a React component?"}
        result = sorter.classify_topic(conversation)
        assert result == "code"
    
    def test_frontmatter_generation(self):
        sorter = ExportSorter()
        conversation = {
            "title": "React Component Help",
            "date": "2026-05-21",
            "topic": "code"
        }
        result = sorter.generate_frontmatter(conversation)
        assert "---" in result
        assert "title:" in result
```

### Step 3: Fix --merge Functionality
Add to `export_sorter.py`:
```python
def merge_conversations(self, input_files, output_file):
    """Merge multiple broken conversation threads into one."""
    all_conversations = []
    
    for file_path in input_files:
        conversations = self.parse_file(file_path)
        all_conversations.extend(conversations)
    
    # Sort by timestamp
    all_conversations.sort(key=lambda x: x.get('timestamp', ''))
    
    # Merge consecutive messages from same role
    merged = []
    for conv in all_conversations:
        if merged and merged[-1]['role'] == conv['role']:
            merged[-1]['content'] += "\n\n" + conv['content']
        else:
            merged.append(conv)
    
    # Write merged output
    self.write_output(merged, output_file)
    return merged
```

### Step 4: Add HTML/PDF Output
Add to `export_sorter.py`:
```python
def export_html(self, conversations, output_file):
    """Export conversations as HTML with styling."""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Conversations Export</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
        .conversation { margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
        .user { background: #f0f0f0; }
        .assistant { background: #e8f4f8; }
        .timestamp { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>AI Conversations Export</h1>
    <p>Exported on {date} — {count} conversations</p>
"""
    
    for conv in conversations:
        html += f"""
    <div class="conversation">
        <h2>{conv.get('title', 'Untitled')}</h2>
        <p class="timestamp">{conv.get('timestamp', 'Unknown date')}</p>
"""
        for msg in conv.get('messages', []):
            role_class = msg['role'].lower()
            html += f'        <div class="message {role_class}">\n'
            html += f'            <strong>{msg["role"]}:</strong>\n'
            html += f'            <p>{msg["content"]}</p>\n'
            html += f'        </div>\n'
        
        html += "    </div>\n"
    
    html += "</body>\n</html>"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def export_pdf(self, conversations, output_file):
    """Export conversations as PDF using weasyprint."""
    # Generate HTML first
    html_file = output_file.replace('.pdf', '.html')
    self.export_html(conversations, html_file)
    
    # Convert to PDF
    from weasyprint import HTML
    HTML(html_file).write_pdf(output_file)
```

### Step 5: Create Proper README
```markdown
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
- **CLI interface** — Fast, scriptable, automatable

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic export
python src/export_sorter.py --input exports/ --output organized/

# With deduplication
python src/export_sorter.py --input exports/ --output organized/ --dedupe

# Show statistics
python src/export_sorter.py --input exports/ --stats

# Merge conversations
python src/export_sorter.py --merge exports/*.txt --output merged.md

# Export as HTML
python src/export_sorter.py --input exports/ --output organized/ --format html

# Export as PDF
python src/export_sorter.py --input exports/ --output organized/ --format pdf
```

## Output Structure

```
organized/
├── code/
│   ├── 2026-05-21-react-component.md
│   └── 2026-05-20-api-design.md
├── design/
│   └── 2026-05-19-ui-feedback.md
├── plan/
│   └── 2026-05-18-project-roadmap.md
├── guide/
│   └── 2026-05-17-deployment-guide.md
└── stats.json
```

## Requirements

- Python 3.9+
- weasyprint (for PDF export)
- pytest (for testing)

## License

MIT
```

---

## WEEK 2-3: GUI (40 hours)

### Step 1: Design GUI Layout
```
┌─────────────────────────────────────────────────────────┐
│ ChatGPT Export System                            [─][□][×]│
├─────────────────────────────────────────────────────────┤
│ [📁 Input Folder] [📂 Output Folder] [⚙️ Settings]       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 Statistics Dashboard                                │
│  ┌─────────────┬─────────────┬─────────────┐           │
│  │ Total: 1,247│ Code: 423   │ Design: 189 │           │
│  │ Duplicates: │ Plan: 156   │ Guide: 234  │           │
│  │ 89 removed  │ Idea: 98    │ General: 147│           │
│  └─────────────┴─────────────┴─────────────┘           │
│                                                         │
│  📋 Conversation Preview                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Title: React Component Help                       │ │
│  │ Date: 2026-05-21                                  │ │
│  │ Topic: code                                       │ │
│  │ Messages: 12                                      │ │
│  │                                                   │ │
│  │ User: How do I build a React component?           │ │
│  │ Assistant: Here's a step-by-step guide...         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [▶️ Export] [⏹️ Stop] [📊 Stats] [🔍 Search]           │
├─────────────────────────────────────────────────────────┤
│ Status: Ready                                          │
└─────────────────────────────────────────────────────────┘
```

### Step 2: Build PyQt6 GUI
Create `src/gui.py`:
```python
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTextEdit, QProgressBar, QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from export_sorter import ExportSorter

class ExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, input_dir, output_dir, options):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.options = options
    
    def run(self):
        try:
            sorter = ExportSorter()
            # Run export with progress callbacks
            self.finished.emit("Export complete!")
        except Exception as e:
            self.error.emit(str(e))

class ExportGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Export System")
        self.resize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Input/Output row
        io_layout = QHBoxLayout()
        self.input_label = QLabel("Input: Not selected")
        self.output_label = QLabel("Output: Not selected")
        self.input_btn = QPushButton("📁 Select Input")
        self.output_btn = QPushButton("📂 Select Output")
        self.input_btn.clicked.connect(self.select_input)
        self.output_btn.clicked.connect(self.select_output)
        io_layout.addWidget(self.input_label)
        io_layout.addWidget(self.input_btn)
        io_layout.addWidget(self.output_label)
        io_layout.addWidget(self.output_btn)
        layout.addLayout(io_layout)
        
        # Statistics dashboard
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0")
        self.code_label = QLabel("Code: 0")
        self.design_label = QLabel("Design: 0")
        self.plan_label = QLabel("Plan: 0")
        self.guide_label = QLabel("Guide: 0")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.code_label)
        stats_layout.addWidget(self.design_label)
        stats_layout.addWidget(self.plan_label)
        stats_layout.addWidget(self.guide_label)
        layout.addLayout(stats_layout)
        
        # Preview area
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("▶️ Export")
        self.export_btn.clicked.connect(self.start_export)
        self.stats_btn = QPushButton("📊 Show Stats")
        self.search_btn = QPushButton("🔍 Search")
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.stats_btn)
        btn_layout.addWidget(self.search_btn)
        layout.addLayout(btn_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def select_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_dir = folder
            self.input_label.setText(f"Input: {folder}")
            self.statusBar().showMessage(f"Input selected: {folder}")
    
    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_label.setText(f"Output: {folder}")
            self.statusBar().showMessage(f"Output selected: {folder}")
    
    def start_export(self):
        if not hasattr(self, 'input_dir') or not hasattr(self, 'output_dir'):
            self.statusBar().showMessage("Please select input and output folders")
            return
        
        self.progress.setVisible(True)
        self.export_btn.setEnabled(False)
        
        self.worker = ExportWorker(self.input_dir, self.output_dir, {})
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.export_finished)
        self.worker.error.connect(self.export_error)
        self.worker.start()
    
    def export_finished(self, message):
        self.progress.setVisible(False)
        self.export_btn.setEnabled(True)
        self.statusBar().showMessage(message)
        self.preview.append(message)
    
    def export_error(self, error):
        self.progress.setVisible(False)
        self.export_btn.setEnabled(True)
        self.statusBar().showMessage(f"Error: {error}")
        self.preview.append(f"ERROR: {error}")

def main():
    app = QApplication(sys.argv)
    window = ExportGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Step 3: Create PyInstaller Spec
Create `chatgpt-export.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChatGPTExport',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

### Step 4: Build EXE
```powershell
cd C:\temp\velvet-sojourner\chatgpt-export
pyinstaller chatgpt-export.spec
```

---

## WEEK 4-5: API INTEGRATION (40 hours)

### Step 1: OpenAI API Integration
Create `src/openai_export.py`:
```python
import openai
import json
from datetime import datetime

class OpenAIExporter:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def export_conversations(self, limit=100):
        """Export conversations from OpenAI API."""
        conversations = []
        
        # Get all threads
        threads = self.client.beta.threads.list(limit=limit)
        
        for thread in threads.data:
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            
            conversation = {
                "id": thread.id,
                "title": thread.metadata.get("title", "Untitled"),
                "created_at": datetime.fromtimestamp(thread.created_at),
                "messages": []
            }
            
            for msg in messages.data:
                for content in msg.content:
                    if content.type == "text":
                        conversation["messages"].append({
                            "role": msg.role,
                            "content": content.text.value,
                            "timestamp": datetime.fromtimestamp(msg.created_at)
                        })
            
            conversations.append(conversation)
        
        return conversations
```

### Step 2: Claude API Integration
Create `src/claude_export.py`:
```python
import anthropic
import json

class ClaudeExporter:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def export_conversations(self, limit=100):
        """Export conversations from Claude API."""
        # Note: Claude doesn't have a conversation export API yet
        # This would work with user's local Claude exports
        pass
```

### Step 3: Semantic Clustering
Create `src/semantic_cluster.py`:
```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

class SemanticClusterer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def cluster(self, conversations, n_clusters=10):
        """Cluster conversations by semantic similarity."""
        # Extract text content
        texts = [conv.get('title', '') + ' ' + conv.get('content', '') for conv in conversations]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        # Assign clusters
        for i, conv in enumerate(conversations):
            conv['cluster'] = labels[i]
        
        return conversations, labels
```

### Step 4: Knowledge Base Generation
Create `src/knowledge_base.py`:
```python
import sqlite3
from sqlite3 import Error

class KnowledgeBase:
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with full-text search."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations USING fts5(
                title, content, topic, date, tags
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_conversation(self, conversation):
        """Add conversation to knowledge base."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations(title, content, topic, date, tags)
            VALUES(?, ?, ?, ?, ?)
        ''', (
            conversation.get('title', ''),
            conversation.get('content', ''),
            conversation.get('topic', 'general'),
            conversation.get('date', ''),
            conversation.get('tags', '')
        ))
        
        conn.commit()
        conn.close()
    
    def search(self, query):
        """Search knowledge base."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, content, topic, date, tags, rank
            FROM conversations
            WHERE conversations MATCH ?
            ORDER BY rank
        ''', (query,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
```

### Step 5: Obsidian Vault Sync
Create `src/obsidian_sync.py`:
```python
import os
import shutil

class ObsidianSync:
    def __init__(self, vault_path):
        self.vault_path = vault_path
    
    def sync(self, export_dir):
        """Sync exported conversations to Obsidian vault."""
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)
        
        # Copy all markdown files
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                if file.endswith('.md'):
                    src = os.path.join(root, file)
                    dst = os.path.join(self.vault_path, file)
                    shutil.copy2(src, dst)
        
        return f"Synced to {self.vault_path}"
```

---

## WEEK 6: LAUNCH (20 hours)

### Step 1: Create Gumroad Product
1. Go to gumroad.com → Products → New Product
2. Name: **ChatGPT Export System**
3. Type: Digital Product
4. Price: $29 (Pro tier)

### Step 2: Write Description
```markdown
# ChatGPT Export System

Never lose an AI insight again. Export, organize, and own your AI conversations from ChatGPT, Claude, and Gemini.

## Features

- **Multi-platform** — ChatGPT, Claude, Gemini exports
- **5 input formats** — TXT, MD, JSON, HTML, PDF
- **Deduplication** — Remove duplicate conversations
- **Topic classification** — Auto-tag by subject
- **Obsidian-compatible** — YAML frontmatter
- **Multiple outputs** — Markdown, HTML, PDF
- **Merge conversations** — Combine broken threads
- **GUI + CLI** — Desktop app or command-line

## What's Included

- ChatGPTExport.exe (GUI desktop app)
- CLI scripts for automation
- Complete documentation
- Example exports
- Obsidian vault sync

## System Requirements

- Windows 10/11 (64-bit)
- Python 3.9+ (for CLI)
- Obsidian (optional, for vault sync)

## Support

Email: ashlee69r@gmail.com

## Refund Policy

30-day money-back guarantee.
```

### Step 3: Create Launch Posts
- r/ChatGPT: Power user angle
- r/ObsidianMD: PKM integration
- r/PKM: Knowledge management
- r/LocalLLaMA: AI power user
- Hacker News: Show HN
- Product Hunt: Launch
- Twitter/X: Before/after thread

### Step 4: Record Demo Video
- 3-minute screen capture
- Show: Drag-and-drop export, preview, organized output
- Save as `docs/chatgpt-export-demo.mp4`

---

## POST-LAUNCH ROADMAP

### Month 2: v1.1
- [ ] Add Gemini API integration
- [ ] Add Notion export
- [ ] Add Roam Research export
- [ ] Add Logseq export
- [ ] Add conversation timeline visualization

### Month 3: v1.2
- [ ] Add AI-powered summarization
- [ ] Add multi-user support
- [ ] Add export scheduling
- [ ] Add web dashboard
- [ ] Add team sharing

### Month 4-6: v2.0
- [ ] Build browser extension
- [ ] Add real-time sync
- [ ] Add advanced search
- [ ] Add collaboration
- [ ] Add API access

---

## FILES TO CREATE/UPDATE

| File | Action | Status |
|------|--------|--------|
| `chatgpt-export/src/export_sorter.py` | Enhance with merge, HTML, PDF | ⏳ |
| `chatgpt-export/src/gui.py` | Create PyQt6 GUI | ⏳ |
| `chatgpt-export/tests/test_export_sorter.py` | Create test suite | ⏳ |
| `chatgpt-export/src/openai_export.py` | Create OpenAI integration | ⏳ |
| `chatgpt-export/src/semantic_cluster.py` | Create clustering | ⏳ |
| `chatgpt-export/src/knowledge_base.py` | Create SQLite KB | ⏳ |
| `chatgpt-export/src/obsidian_sync.py` | Create Obsidian sync | ⏳ |
| `chatgpt-export/README.md` | Create documentation | ⏳ |
| `chatgpt-export/CHANGELOG.md` | Create version history | ⏳ |
| `chatgpt-export/LICENSE` | Create (MIT) | ⏳ |
| `chatgpt-export/assets/icon.ico` | Create app icon | ⏳ |
| `chatgpt-export/chatgpt-export.spec` | Create PyInstaller spec | ⏳ |

---

## SUCCESS METRICS

| Metric | 30-Day Target | 90-Day Target |
|--------|--------------|---------------|
| Gumroad views | 1,000 | 5,000 |
| Downloads | 100 | 500 |
| Sales | 20 | 100 |
| Revenue | $600 | $3,000 |
| HN upvotes | 40+ | 150+ |
| Reddit upvotes | 80+ | 300+ |

---

**Start Week 1 now. Complete each step before moving to the next. Track everything.**
