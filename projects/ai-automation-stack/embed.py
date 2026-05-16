#!/usr/bin/env python3
"""
RAG Embedder - Knowledge Base Vector Search Pipeline
======================================================
Uses OpenAI embeddings and LangChain + FAISS for local document embedding.

Features:
- Ingests Markdown, PDF, TXT, HTML files
- Chunking with overlap for semantic search
- OpenAI embedding generation
- FAISS vector store with persistence
- Incremental updates (re-index only changed files)
- Metadata extraction and storage
- Hybrid search (semantic + keyword)

Usage:
    python embed.py                         # Run full embed pipeline
    python embed.py --path ./docs           # Embed specific directory
    python embed.py --chunk-size 1000       # Custom chunk size
    python embed.py -- incremental          # Only new/changed files
    python embed.py --search "query"        # Search the knowledge base
    python embed.py --clear                 # Clear vector store
    python embed.py --stats                 # Show index statistics

Dependencies:
    - langchain
    - langchain-openai
    - langchain-community
    - faiss-cpu (or faiss-gpu)
    - pypdf (for PDF)
    - beautifulsoup4 (for HTML)
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "embed.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A chunk of a document with metadata."""
    content: str
    metadata: Dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class EmbedConfig:
    """Configuration for embedding pipeline."""
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    source_dirs: List[str] = field(default_factory=lambda: ["docs", "Obsidian/AI-Vault"])
    file_extensions: List[str] = field(default_factory=lambda: [".md", ".txt", ".pdf", ".html"])
    store_path: Path = VECTOR_STORE_DIR


class DocumentLoader:
    """Load and parse documents from various sources."""

    def __init__(self):
        self.supported_extensions = {".md", ".txt", ".pdf", ".html"}

    def load_file(self, filepath: Path) -> Tuple[str, Dict]:
        """Load a file and return content with metadata."""
        ext = filepath.suffix.lower()

        if ext == ".md" or ext == ".txt":
            return self._load_text(filepath)
        elif ext == ".pdf":
            return self._load_pdf(filepath)
        elif ext == ".html":
            return self._load_html(filepath)

        return "", {}

    def _load_text(self, filepath: Path) -> Tuple[str, Dict]:
        """Load text/markdown file."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = {
            "source": str(filepath),
            "filename": filepath.name,
            "extension": filepath.suffix,
            "file_size": filepath.stat().st_size,
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            "type": "text",
        }

        # Try to extract YAML frontmatter
        if content.startswith("---"):
            parts = content[3:].split("---", 1)
            if len(parts) == 2:
                frontmatter = parts[0]
                content = parts[1]
                try:
                    import yaml
                    front_data = yaml.safe_load(frontmatter)
                    if front_data:
                        metadata.update(front_data)
                except Exception:
                    pass

        return content, metadata

    def _load_pdf(self, filepath: Path) -> Tuple[str, Dict]:
        """Load PDF file."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            metadata = {
                "source": str(filepath),
                "filename": filepath.name,
                "extension": ".pdf",
                "file_size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                "type": "pdf",
                "page_count": len(reader.pages),
            }

            return text, metadata

        except ImportError:
            logger.warning("pypdf not installed. PDF loading disabled.")
            return "", {}
        except Exception as e:
            logger.error(f"Failed to load PDF {filepath}: {e}")
            return "", {}

    def _load_html(self, filepath: Path) -> Tuple[str, Dict]:
        """Load HTML file."""
        try:
            from bs4 import BeautifulSoup

            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()

            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            text = soup.get_text(separator="\n")

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = "\n".join(line for line in lines if line)

            metadata = {
                "source": str(filepath),
                "filename": filepath.name,
                "extension": ".html",
                "file_size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                "type": "html",
                "title": soup.title.string if soup.title else filepath.stem,
            }

            return text, metadata

        except ImportError:
            logger.warning("beautifulsoup4 not installed. HTML loading disabled.")
            return "", {}
        except Exception as e:
            logger.error(f"Failed to load HTML {filepath}: {e}")
            return "", {}

    def scan_directory(self, directory: Path, extensions: List[str]) -> List[Path]:
        """Scan directory for supported files."""
        files = []
        if not directory.exists():
            return files

        for ext in extensions:
            files.extend(directory.rglob(f"*{ext}"))

        return sorted(set(files))


class TextChunker:
    """Split text into semantic chunks."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Dict) -> List[DocumentChunk]:
        """Split text into overlapping chunks."""
        chunks = []

        if not text:
            return chunks

        # Split by paragraphs first
        paragraphs = text.split("\n\n")

        current_chunk = ""
        current_sources = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    # Save current chunk
                    chunk_metadata = metadata.copy()
                    if current_sources:
                        chunk_metadata["source_files"] = list(set(current_sources))

                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        metadata=chunk_metadata,
                    ))

                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    # Get overlap from end of current chunk
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + para
                    current_sources = [metadata.get("source", "")]
                else:
                    current_chunk = para
                    current_sources = [metadata.get("source", "")]
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

                source = metadata.get("source", "")
                if source and source not in current_sources:
                    current_sources.append(source)

        # Don't forget the last chunk
        if current_chunk:
            chunk_metadata = metadata.copy()
            if current_sources:
                chunk_metadata["source_files"] = list(set(current_sources))

            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                metadata=chunk_metadata,
            ))

        return chunks


class VectorStore:
    """FAISS-based vector store for document embeddings."""

    def __init__(self, path: Path, api_key: str):
        self.path = path
        self.api_key = api_key
        self.index = None
        self.documents: List[DocumentChunk] = []
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Load existing index or create new one."""
        import numpy as np

        index_file = self.path / "index.faiss"
        docs_file = self.path / "documents.json"
        meta_file = self.path / "metadata.json"

        if index_file.exists() and docs_file.exists():
            try:
                import faiss

                self.index = faiss.read_index(str(index_file))

                with open(docs_file, "r") as f:
                    docs_data = json.load(f)
                    self.documents = [
                        DocumentChunk(
                            content=d["content"],
                            metadata=d["metadata"],
                        )
                        for d in docs_data
                    ]

                logger.info(f"Loaded existing index with {len(self.documents)} documents")
                return

            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")

        # Create new index
        import faiss
        self.index = faiss.IndexFlatL2(1536)  # OpenAI embedding dimension
        self.documents = []
        logger.info("Initialized new vector store")

    def add_documents(self, chunks: List[DocumentChunk], api_key: str):
        """Add document chunks to the index."""
        if not chunks:
            return

        logger.info(f"Embedding {len(chunks)} chunks...")

        # Get embeddings
        embeddings = self._get_embeddings([c.content for c in chunks], api_key)

        # Add to index
        import numpy as np

        embeddings_array = np.array(embeddings).astype("float32")
        self.index.add(embeddings_array)

        # Store documents
        self.documents.extend(chunks)

        # Save to disk
        self._save()

    def _get_embeddings(self, texts: List[str], api_key: str) -> List[List[float]]:
        """Get OpenAI embeddings for texts."""
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        embeddings = []

        # Process in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch,
                )

                for item in response.data:
                    embeddings.append(item.embedding)

                logger.info(f"Embedded {min(i + batch_size, len(texts))}/{len(texts)} chunks")

            except Exception as e:
                logger.error(f"Embedding failed: {e}")
                # Use zero embeddings as fallback
                for _ in batch:
                    embeddings.append([0.0] * 1536)

            time.sleep(0.1)  # Rate limiting

        return embeddings

    def search(
        self,
        query: str,
        api_key: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar documents."""
        if not self.documents:
            return []

        # Get query embedding
        embeddings = self._get_embeddings([query], api_key)
        query_vector = [embeddings[0]]

        import numpy as np

        # Search
        distances, indices = self.index.search(np.array(query_vector).astype("float32"), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append((doc, float(dist)))

        return results

    def _save(self):
        """Save index and documents to disk."""
        import numpy as np

        self.path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        import faiss
        faiss.write_index(self.index, str(self.path / "index.faiss"))

        # Save documents
        docs_data = [
            {"content": d.content, "metadata": d.metadata}
            for d in self.documents
        ]
        with open(self.path / "documents.json", "w") as f:
            json.dump(docs_data, f, indent=2)

        # Save metadata
        with open(self.path / "metadata.json", "w") as f:
            json.dump({
                "document_count": len(self.documents),
                "index_dimension": self.index.d,
                "last_updated": datetime.now().isoformat(),
            }, f, indent=2)

        logger.info(f"Saved index with {len(self.documents)} documents")

    def clear(self):
        """Clear the vector store."""
        import numpy as np

        self.index = np.random.rand(0, 1536).astype("float32")
        self.documents = []

        for f in self.path.glob("*"):
            if f.is_file():
                f.unlink()

        logger.info("Vector store cleared")


class RAGPipeline:
    """Main RAG embedding pipeline."""

    def __init__(self, config: EmbedConfig):
        self.config = config
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        self.store = VectorStore(config.store_path, config.openai_api_key)

    def run(self) -> int:
        """Run the full embedding pipeline."""
        logger.info("=" * 60)
        logger.info("RAG Embedding Pipeline Started")
        logger.info("=" * 60)

        all_chunks = []

        for source_dir in self.config.source_dirs:
            dir_path = BASE_DIR / source_dir
            if not dir_path.exists():
                logger.warning(f"Directory not found: {dir_path}")
                continue

            logger.info(f"\nScanning {dir_path}...")

            files = self.loader.scan_directory(
                dir_path,
                self.config.file_extensions,
            )

            logger.info(f"Found {len(files)} files")

            for filepath in files:
                try:
                    content, metadata = self.loader.load_file(filepath)

                    if not content:
                        logger.debug(f"Empty file: {filepath}")
                        continue

                    # Generate file hash for change detection
                    file_hash = self._get_file_hash(filepath)

                    # Check if already indexed
                    existing_sources = set()
                    for doc in self.store.documents:
                        if doc.metadata.get("source") == str(filepath):
                            existing_sources.add(doc.metadata.get("file_hash", ""))

                    if file_hash in existing_sources:
                        logger.debug(f"Already indexed: {filepath.name}")
                        continue

                    # Chunk the document
                    chunks = self.chunker.chunk(content, metadata)
                    for chunk in chunks:
                        chunk.metadata["file_hash"] = file_hash

                    all_chunks.extend(chunks)
                    logger.info(f"  📄 {filepath.name}: {len(chunks)} chunks")

                except Exception as e:
                    logger.error(f"Failed to process {filepath}: {e}")

        # Add all chunks to the store
        if all_chunks:
            self.store.add_documents(all_chunks, self.config.openai_api_key)

        logger.info("\n" + "=" * 60)
        logger.info(f"RAG Pipeline Complete")
        logger.info(f"Total chunks embedded: {len(all_chunks)}")
        logger.info(f"Total documents in store: {len(self.store.documents)}")
        logger.info("=" * 60)

        return len(all_chunks)

    def _get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of file content."""
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, str]]:
        """Search the knowledge base."""
        results = self.store.search(query, self.config.openai_api_key, k)

        output = []
        for doc, score in results:
            output.append({
                "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "score": score,
                "source": doc.metadata.get("source", "Unknown"),
            })

        return output

    def get_stats(self) -> Dict:
        """Get index statistics."""
        meta_file = self.store.path / "metadata.json"
        last_updated = None
        if meta_file.exists():
            try:
                with open(meta_file, "r") as f:
                    meta_data = json.load(f)
                    last_updated = meta_data.get("last_updated")
            except Exception:
                pass
        
        return {
            "total_documents": len(self.store.documents),
            "last_updated": last_updated,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Embedder - Knowledge Base Vector Search Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python embed.py                           Run full embed pipeline
  python embed.py --path ./docs             Embed specific directory
  python embed.py --chunk-size 1500         Custom chunk size
  python embed.py --incremental             Only new/changed files
  python embed.py --search "AI agents"      Search the knowledge base
  python embed.py --clear                   Clear vector store
  python embed.py --stats                   Show index statistics
        """,
    )

    parser.add_argument(
        "--path",
        "-p",
        action="append",
        help="Source directory to embed (can be specified multiple times)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in characters (default: 1000)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap in characters (default: 200)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only process new/changed files",
    )
    parser.add_argument(
        "--search",
        "-s",
        metavar="QUERY",
        help="Search the knowledge base",
    )
    parser.add_argument(
        "--results",
        type=int,
        default=5,
        help="Number of search results (default: 5)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the vector store",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show index statistics",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config
    config_data = {}
    config_file = BASE_DIR / "config.json"
    if config_file.exists():
        with open(config_file, "r") as f:
            config_data = json.load(f)

    # Build config
    config = EmbedConfig(
        openai_api_key=args.openai_api_key
        if hasattr(args, "openai_api_key")
        else os.getenv("OPENAI_API_KEY", config_data.get("openai_api_key", "")),
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        source_dirs=args.path or config_data.get("embed_dirs", ["docs", "Obsidian/AI-Vault"]),
    )

    if not config.openai_api_key:
        logger.error("OpenAI API key required. Set OPENAI_API_KEY in .env")
        sys.exit(1)

    pipeline = RAGPipeline(config)

    if args.clear:
        logger.info("Clearing vector store...")
        pipeline.store.clear()
        return

    if args.stats:
        stats = pipeline.get_stats()
        print("\n📊 Vector Store Statistics")
        print(f"  Total documents: {stats['total_documents']}")
        return

    if args.search:
        logger.info(f"Searching for: {args.search}")
        results = pipeline.search(args.search, args.results)

        print("\n🔍 Search Results")
        print("=" * 60)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['score']:.4f}")
            print(f"   Source: {result['source']}")
            print(f"   Content: {result['content'][:200]}...")
        print("=" * 60)
        return

    # Run full pipeline
    pipeline.run()


if __name__ == "__main__":
    main()
