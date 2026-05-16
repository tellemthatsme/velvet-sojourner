#!/usr/bin/env python3
"""
Search Server - Markdown Full-Text Search API
==============================================
Flask API for real-time full-text search of markdown content.

Features:
- Full-text search across all markdown files
- Keyword highlighting
- File and line number results
- Case-insensitive search
- Regex support
- Recent files filter

Usage:
    python search_server.py                    # Start server (port 5001)
    python search_server.py --port 8080        # Custom port
    python search_server.py --path ./docs      # Search directory

API Endpoints:
    GET /search?q=                    Search for term
    GET /search?q=&regex=true         Regex search
    GET /file/<path>                  Get file content
    GET /list                         List all files
    GET /stats                        Search statistics

Dependencies:
    - flask
    - flask-cors
"""

import argparse
import glob
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_SEARCH_DIRS = ["docs", "Obsidian/AI-Vault"]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "search.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@dataclass
class SearchResult:
    """Search result with line context."""
    file_path: str
    file_name: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int
    context_before: List[str] = None
    context_after: List[str] = None

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "match_start": self.match_start,
            "match_end": self.match_end,
            "context_before": self.context_before or [],
            "context_after": self.context_after or [],
        }


class MarkdownSearcher:
    """Full-text search across markdown files."""

    def __init__(self, search_dirs: List[str]):
        self.search_dirs = [BASE_DIR / d for d in search_dirs if (BASE_DIR / d).exists()]
        self.file_cache: Dict[str, str] = {}
        self.last_indexed: Optional[datetime] = None

    def _get_all_files(self) -> List[Path]:
        """Get all markdown files in search directories."""
        files = []
        for search_dir in self.search_dirs:
            files.extend(search_dir.rglob("*.md"))
        return sorted(set(files))

    def _read_file(self, filepath: Path) -> str:
        """Read file content with caching."""
        if filepath in self.file_cache:
            return self.file_cache[filepath]

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.file_cache[str(filepath)] = content
            return content
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return ""

    def _search_file(
        self,
        filepath: Path,
        query: str,
        use_regex: bool = False,
        case_sensitive: bool = False,
    ) -> List[SearchResult]:
        """Search within a single file."""
        content = self._read_file(filepath)
        if not content:
            return []

        results = []
        lines = content.split("\n")

        try:
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
            else:
                if case_sensitive:
                    pattern = re.compile(re.escape(query), re.IGNORECASE)
                else:
                    pattern = re.compile(re.escape(query), re.IGNORECASE)
        except re.error as e:
            logger.error(f"Invalid regex: {e}")
            return []

        for line_num, line in enumerate(lines, 1):
            matches = list(pattern.finditer(line))

            for match in matches:
                result = SearchResult(
                    file_path=str(filepath),
                    file_name=filepath.name,
                    line_number=line_num,
                    line_content=line,
                    match_start=match.start(),
                    match_end=match.end(),
                    context_before=lines[max(0, line_num - 3) : line_num - 1],
                    context_after=lines[line_num : min(len(lines), line_num + 2)],
                )
                results.append(result)

        return results

    def search(
        self,
        query: str,
        use_regex: bool = False,
        case_sensitive: bool = False,
        limit: int = 100,
        file_pattern: Optional[str] = None,
    ) -> Dict:
        """Search across all files."""
        if not query:
            return {"results": [], "count": 0, "query": query}

        start_time = datetime.now()
        all_results: List[SearchResult] = []

        files = self._get_all_files()

        # Filter by file pattern if specified
        if file_pattern:
            files = [f for f in files if file_pattern in f.name]

        for filepath in files:
            file_results = self._search_file(
                filepath,
                query,
                use_regex=use_regex,
                case_sensitive=case_sensitive,
            )
            all_results.extend(file_results)

            if len(all_results) >= limit:
                break

        # Sort results by file path and line number
        all_results.sort(key=lambda r: (r.file_path, r.line_number))

        # Format results
        formatted_results = [r.to_dict() for r in all_results[:limit]]

        search_time = (datetime.now() - start_time).total_seconds()

        return {
            "query": query,
            "count": len(formatted_results),
            "total_found": len(all_results),
            "search_time": search_time,
            "results": formatted_results,
        }

    def search_files(self, query: str, case_sensitive: bool = False) -> List[str]:
        """Find files containing the query."""
        files = self._get_all_files()
        matching_files = []

        for filepath in files:
            content = self._read_file(filepath)
            if content:
                try:
                    if case_sensitive:
                        if query in content:
                            matching_files.append(str(filepath))
                    else:
                        if query.lower() in content.lower():
                            matching_files.append(str(filepath))
                except Exception:
                    pass

        return sorted(matching_files)

    def get_file_list(self) -> List[Dict]:
        """Get list of all searchable files."""
        files = self._get_all_files()

        result = []
        for filepath in files:
            stat = filepath.stat()
            result.append({
                "path": str(filepath),
                "name": filepath.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        return result

    def get_stats(self) -> Dict:
        """Get search statistics."""
        files = self._get_all_files()

        total_size = sum(f.stat().st_size for f in files)
        total_lines = 0

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    total_lines += sum(1 for _ in f)
            except Exception:
                pass

        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_formatted": self._format_size(total_size),
            "total_lines": total_lines,
            "search_dirs": [str(d) for d in self.search_dirs],
        }

    def _format_size(self, size: int) -> str:
        """Format size in bytes to human readable."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def read_file(self, filepath: str) -> Optional[Dict]:
        """Read a specific file."""
        path = Path(filepath)
        if not path.exists():
            return None

        content = self._read_file(path)

        return {
            "path": str(path),
            "name": path.name,
            "content": content,
            "size": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "lines": len(content.split("\n")),
        }

    def invalidate_cache(self, filepath: Optional[str] = None):
        """Invalidate file cache."""
        if filepath and filepath in self.file_cache:
            del self.file_cache[filepath]
        else:
            self.file_cache.clear()
            self.last_indexed = datetime.now()


# Initialize searcher
searcher = MarkdownSearcher(DEFAULT_SEARCH_DIRS)


# =============================================================================
# API Routes
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/search", methods=["GET"])
def search():
    """Search for term in markdown files."""
    query = request.args.get("q", "").strip()
    use_regex = request.args.get("regex", "").lower() == "true"
    case_sensitive = request.args.get("case", "").lower() == "true"
    limit = int(request.args.get("limit", 100))
    file_pattern = request.args.get("file")

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = searcher.search(
        query=query,
        use_regex=use_regex,
        case_sensitive=case_sensitive,
        limit=limit,
        file_pattern=file_pattern,
    )

    return jsonify(results)


@app.route("/api/search/files", methods=["GET"])
def search_files():
    """Find files containing the query."""
    query = request.args.get("q", "").strip()
    case_sensitive = request.args.get("case", "").lower() == "true"

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    files = searcher.search_files(query, case_sensitive)

    return jsonify({
        "query": query,
        "count": len(files),
        "files": files,
    })


@app.route("/api/file", methods=["GET"])
def get_file():
    """Get file content."""
    filepath = request.args.get("path", "")

    if not filepath:
        return jsonify({"error": "Path parameter is required"}), 400

    result = searcher.read_file(filepath)

    if result is None:
        return jsonify({"error": "File not found"}), 404

    return jsonify(result)


@app.route("/api/list", methods=["GET"])
def list_files():
    """List all searchable files."""
    return jsonify({
        "files": searcher.get_file_list(),
        "count": len(searcher.get_file_list()),
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get search statistics."""
    return jsonify(searcher.get_stats())


@app.route("/api/cache/invalidate", methods=["POST"])
def invalidate_cache():
    """Invalidate file cache."""
    filepath = request.args.get("path")
    searcher.invalidate_cache(filepath)
    return jsonify({"success": True, "message": "Cache invalidated"})


@app.route("/api/reindex", methods=["POST"])
def reindex():
    """Force reindex of all files."""
    searcher.invalidate_cache()
    return jsonify({
        "success": True,
        "message": "Reindex triggered",
        "files_count": len(searcher.get_file_list()),
    })


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search Server - Markdown Full-Text Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_server.py                    Start server (port 5001)
  python search_server.py --port 8080        Custom port
  python search_server.py --path ./docs      Search directory

API Usage:
  curl "http://localhost:5001/api/search?q=python"
  curl "http://localhost:5001/api/search?q=def.*&regex=true"
  curl "http://localhost:5001/api/list"
  curl "http://localhost:5001/api/stats"
        """,
    )

    parser.add_argument("--port", type=int, default=5001, help="Server port (default: 5001)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument(
        "--path",
        action="append",
        help="Directory to search (can be specified multiple times)",
    )
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    # Update search directories if specified
    if args.path:
        searcher.search_dirs = [BASE_DIR / d for d in args.path if (BASE_DIR / d).exists()]
        logger.info(f"Search directories: {searcher.search_dirs}")

    logger.info(f"Starting Search Server on {args.host}:{args.port}")
    logger.info(f"Searching in: {[str(d) for d in searcher.search_dirs]}")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
