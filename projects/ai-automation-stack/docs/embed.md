# RAG Embedder Documentation

## Overview

Builds a searchable knowledge base using OpenAI embeddings and FAISS vector storage.

## Features

- Ingests Markdown, PDF, TXT, HTML files
- Semantic chunking with overlap
- OpenAI text-embedding-3-small
- FAISS vector store with persistence
- Incremental updates
- Hybrid search (semantic + keyword)

## Usage

### Full Pipeline

```bash
python embed.py
```

### Options

```bash
# Custom directories
python embed.py --path ./docs --path ./Obsidian/AI-Vault

# Custom chunk size
python embed.py --chunk-size 1500 --chunk-overlap 200

# Incremental (only new/changed files)
python embed.py --incremental

# Search knowledge base
python embed.py --search "your query"
python embed.py -s "AI automation" --results 10

# Show statistics
python embed.py --stats

# Clear vector store
python embed.py --clear
```

## How It Works

1. **Scans** directories for supported files
2. **Loads** and parses documents
3. **Chunks** text with overlap
4. **Embeds** using OpenAI API
5. **Stores** in FAISS index
6. **Persists** to disk

## Configuration

Edit in `.env`:

```env
EMBED_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## API Usage

### Start Search Server

```bash
python search_server.py --port 5001
```

### Search Endpoints

```bash
# Full-text search
curl "http://localhost:5001/api/search?q=automation"

# List files
curl http://localhost:5001/api/list

# Get file content
curl "http://localhost:5001/api/file?path=./docs/readme.md"

# Get statistics
curl http://localhost:5001/api/stats
```

## Output

```
vector_store/
├── index.faiss      # FAISS index
├── documents.json   # Document chunks
└── metadata.json    # Index metadata
```

## Troubleshooting

### No Embeddings Generated

1. Check OpenAI API key in `.env`
2. Verify API quota
3. Check logs in `logs/embed.log`

### Poor Search Results

1. Run incremental update: `python embed.py --incremental`
2. Increase chunk size
3. Add more documents to index

### Memory Issues

FAISS loads entire index into memory. For large indexes:
- Use smaller embedding model
- Reduce chunk overlap
- Split into multiple indexes
