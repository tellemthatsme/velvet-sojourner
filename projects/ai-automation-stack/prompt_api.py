#!/usr/bin/env python3
"""
Prompt API Server - Flask-based Prompt Management
===================================================
RESTful API to store, load, tag, and version prompts.

Features:
- CRUD operations for prompts
- Tagging and categorization
- Version history
- Bulk import/export
- Search functionality
- JSON/YAML support

Usage:
    python prompt_api.py                    # Start server (default port 5000)
    python prompt_api.py --port 8080        # Custom port
    python prompt_api.py --debug            # Debug mode

API Endpoints:
    GET    /api/prompts                    # List all prompts
    POST   /api/prompts                    # Create new prompt
    GET    /api/prompts/<id>               # Get specific prompt
    PUT    /api/prompts/<id>               # Update prompt
    DELETE /api/prompts/<id>               # Delete prompt
    GET    /api/prompts/<id>/versions      # Get version history
    POST   /api/prompts/<id>/restore       # Restore version
    GET    /api/search?q=                  # Search prompts
    GET    /api/tags                       # List all tags
    GET    /api/export                     # Export all prompts
    POST   /api/import                     # Import prompts

Dependencies:
    - flask
    - flask-cors
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
PROMPTS_DIR = BASE_DIR / "prompts"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "prompt_api.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class PromptStore:
    """Store and manage prompts."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.prompts: Dict[str, Dict] = {}
        self._load_all()

    def _load_all(self):
        """Load all prompts from storage."""
        for prompt_file in self.storage_dir.glob("*.json"):
            try:
                with open(prompt_file, "r") as f:
                    data = json.load(f)
                    self.prompts[data["id"]] = data
            except Exception as e:
                logger.error(f"Failed to load {prompt_file}: {e}")

        logger.info(f"Loaded {len(self.prompts)} prompts")

    def _save(self, prompt_id: str, data: Dict):
        """Save a prompt to storage."""
        filepath = self.storage_dir / f"{prompt_id}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _generate_id(self, title: str) -> str:
        """Generate unique ID for a prompt."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{title}{timestamp}".encode()
        short_hash = hashlib.md5(hash_input).hexdigest()[:8]
        return f"prompt_{short_hash}"

    def create(
        self,
        title: str,
        content: str,
        description: str = "",
        tags: List[str] = None,
        category: str = "general",
        metadata: Dict = None,
    ) -> Dict:
        """Create a new prompt."""
        prompt_id = self._generate_id(title)

        now = datetime.now().isoformat()

        prompt = {
            "id": prompt_id,
            "title": title,
            "content": content,
            "description": description,
            "tags": tags or [],
            "category": category,
            "metadata": metadata or {},
            "version": 1,
            "versions": [
                {
                    "version": 1,
                    "content": content,
                    "created_at": now,
                    "note": "Initial version",
                }
            ],
            "created_at": now,
            "updated_at": now,
            "usage_count": 0,
            "favorite": False,
        }

        self.prompts[prompt_id] = prompt
        self._save(prompt_id, prompt)

        logger.info(f"Created prompt: {prompt_id} - {title}")
        return prompt

    def get(self, prompt_id: str) -> Optional[Dict]:
        """Get a prompt by ID."""
        return self.prompts.get(prompt_id)

    def update(
        self,
        prompt_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict] = None,
        note: str = "Updated",
    ) -> Optional[Dict]:
        """Update a prompt with version tracking."""
        if prompt_id not in self.prompts:
            return None

        prompt = self.prompts[prompt_id]
        now = datetime.now().isoformat()

        # Track changes for versioning
        changes = {}
        if title and title != prompt.get("title"):
            changes["title"] = {"from": prompt.get("title"), "to": title}
            prompt["title"] = title
        if content and content != prompt.get("content"):
            changes["content"] = {"from": "content changed", "to": "content changed"}
            # Create new version
            new_version = len(prompt["versions"]) + 1
            prompt["versions"].append({
                "version": new_version,
                "content": content,
                "created_at": now,
                "note": note,
            })
            prompt["content"] = content
            prompt["version"] = new_version
        if description is not None:
            prompt["description"] = description
        if tags is not None:
            prompt["tags"] = tags
        if category:
            prompt["category"] = category
        if metadata:
            prompt["metadata"] = {**prompt.get("metadata", {}), **metadata}

        prompt["updated_at"] = now

        self._save(prompt_id, prompt)

        logger.info(f"Updated prompt: {prompt_id}")
        return prompt

    def delete(self, prompt_id: str) -> bool:
        """Delete a prompt."""
        if prompt_id not in self.prompts:
            return False

        filepath = self.storage_dir / f"{prompt_id}.json"
        if filepath.exists():
            filepath.unlink()

        del self.prompts[prompt_id]

        logger.info(f"Deleted prompt: {prompt_id}")
        return True

    def list_all(
        self,
        tag: Optional[str] = None,
        category: Optional[str] = None,
        favorite: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """List prompts with filtering."""
        results = []

        for prompt in self.prompts.values():
            # Filter by tag
            if tag and tag not in prompt.get("tags", []):
                continue

            # Filter by category
            if category and prompt.get("category") != category:
                continue

            # Filter by favorite
            if favorite is not None and prompt.get("favorite") != favorite:
                continue

            # Filter by search
            if search:
                search_lower = search.lower()
                if not (
                    search_lower in prompt.get("title", "").lower()
                    or search_lower in prompt.get("content", "").lower()
                    or search_lower in prompt.get("description", "").lower()
                ):
                    continue

            results.append(prompt)

        # Sort by updated_at descending
        results.sort(key=lambda p: p.get("updated_at", ""), reverse=True)

        return results[offset : offset + limit]

    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search across prompts."""
        query_lower = query.lower()
        results = []

        for prompt in self.prompts.values():
            score = 0

            # Title match (highest weight)
            if query_lower in prompt.get("title", "").lower():
                score += 10

            # Content match
            if query_lower in prompt.get("content", "").lower():
                score += 5

            # Description match
            if query_lower in prompt.get("description", "").lower():
                score += 3

            # Tag match
            for tag in prompt.get("tags", []):
                if query_lower in tag.lower():
                    score += 4

            if score > 0:
                result = prompt.copy()
                result["search_score"] = score
                results.append(result)

        # Sort by score descending
        results.sort(key=lambda p: p.get("search_score", 0), reverse=True)

        return results[:limit]

    def get_versions(self, prompt_id: str) -> Optional[List[Dict]]:
        """Get version history for a prompt."""
        prompt = self.get(prompt_id)
        if not prompt:
            return None
        return prompt.get("versions", [])

    def restore_version(self, prompt_id: str, version: int) -> Optional[Dict]:
        """Restore a prompt to a specific version."""
        prompt = self.get(prompt_id)
        if not prompt:
            return None

        versions = prompt.get("versions", [])
        target_version = next((v for v in versions if v["version"] == version), None)

        if not target_version:
            return None

        # Update to the restored version
        return self.update(
            prompt_id,
            content=target_version["content"],
            note=f"Restored from version {version}",
        )

    def toggle_favorite(self, prompt_id: str) -> Optional[Dict]:
        """Toggle favorite status."""
        prompt = self.get(prompt_id)
        if not prompt:
            return None

        prompt["favorite"] = not prompt.get("favorite", False)
        prompt["updated_at"] = datetime.now().isoformat()

        self._save(prompt_id, prompt)
        return prompt

    def increment_usage(self, prompt_id: str) -> Optional[Dict]:
        """Increment usage count."""
        prompt = self.get(prompt_id)
        if not prompt:
            return None

        prompt["usage_count"] = prompt.get("usage_count", 0) + 1
        self._save(prompt_id, prompt)
        return prompt

    def get_tags(self) -> Dict[str, int]:
        """Get all tags with counts."""
        tags = {}
        for prompt in self.prompts.values():
            for tag in prompt.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1
        return dict(sorted(tags.items(), key=lambda x: x[1], reverse=True))

    def get_categories(self) -> List[str]:
        """Get all categories."""
        categories = set()
        for prompt in self.prompts.values():
            cat = prompt.get("category")
            if cat:
                categories.add(cat)
        return sorted(categories)

    def export_all(self) -> Dict:
        """Export all prompts."""
        return {
            "exported_at": datetime.now().isoformat(),
            "count": len(self.prompts),
            "prompts": list(self.prompts.values()),
        }

    def import_prompts(self, data: Dict, replace: bool = False) -> Dict:
        """Import prompts from data."""
        imported = 0
        skipped = 0

        for prompt_data in data.get("prompts", []):
            if not replace and prompt_data["id"] in self.prompts:
                skipped += 1
                continue

            # Normalize prompt data
            prompt = {
                "id": prompt_data["id"],
                "title": prompt_data.get("title", "Imported"),
                "content": prompt_data.get("content", ""),
                "description": prompt_data.get("description", ""),
                "tags": prompt_data.get("tags", []),
                "category": prompt_data.get("category", "imported"),
                "metadata": prompt_data.get("metadata", {}),
                "version": prompt_data.get("version", 1),
                "versions": prompt_data.get("versions", []),
                "created_at": prompt_data.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "usage_count": prompt_data.get("usage_count", 0),
                "favorite": prompt_data.get("favorite", False),
            }

            self.prompts[prompt["id"]] = prompt
            self._save(prompt["id"], prompt)
            imported += 1

        return {"imported": imported, "skipped": skipped}


# Initialize store
prompt_store = PromptStore(PROMPTS_DIR)


# =============================================================================
# API Routes
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/api/prompts", methods=["GET"])
def list_prompts():
    """List all prompts with filtering."""
    tag = request.args.get("tag")
    category = request.args.get("category")
    favorite = request.args.get("favorite")
    search = request.args.get("search")
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))

    if favorite is not None:
        favorite = favorite.lower() == "true"

    prompts = prompt_store.list_all(
        tag=tag,
        category=category,
        favorite=favorite,
        search=search,
        limit=limit,
        offset=offset,
    )

    return jsonify({
        "count": len(prompts),
        "prompts": prompts,
    })


@app.route("/api/prompts", methods=["POST"])
def create_prompt():
    """Create a new prompt."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if not data.get("content"):
        return jsonify({"error": "Content is required"}), 400

    prompt = prompt_store.create(
        title=data.get("title", "Untitled"),
        content=data["content"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
        category=data.get("category", "general"),
        metadata=data.get("metadata", {}),
    )

    return jsonify(prompt), 201


@app.route("/api/prompts/<prompt_id>", methods=["GET"])
def get_prompt(prompt_id):
    """Get a specific prompt."""
    prompt = prompt_store.get(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    # Increment usage
    prompt_store.increment_usage(prompt_id)
    prompt["usage_count"] += 1

    return jsonify(prompt)


@app.route("/api/prompts/<prompt_id>", methods=["PUT"])
def update_prompt(prompt_id):
    """Update a prompt."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    prompt = prompt_store.update(
        prompt_id,
        title=data.get("title"),
        content=data.get("content"),
        description=data.get("description"),
        tags=data.get("tags"),
        category=data.get("category"),
        metadata=data.get("metadata"),
        note=data.get("note", "Updated"),
    )

    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    return jsonify(prompt)


@app.route("/api/prompts/<prompt_id>", methods=["DELETE"])
def delete_prompt(prompt_id):
    """Delete a prompt."""
    if prompt_store.delete(prompt_id):
        return jsonify({"success": True})
    return jsonify({"error": "Prompt not found"}), 404


@app.route("/api/prompts/<prompt_id>/versions", methods=["GET"])
def get_versions(prompt_id):
    """Get version history."""
    versions = prompt_store.get_versions(prompt_id)
    if versions is None:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify({"versions": versions})


@app.route("/api/prompts/<prompt_id>/restore", methods=["POST"])
def restore_version(prompt_id):
    """Restore a prompt to a specific version."""
    data = request.get_json()
    version = data.get("version")

    if not version:
        return jsonify({"error": "Version number required"}), 400

    prompt = prompt_store.restore_version(prompt_id, version)
    if not prompt:
        return jsonify({"error": "Prompt or version not found"}), 404

    return jsonify(prompt)


@app.route("/api/prompts/<prompt_id>/favorite", methods=["POST"])
def toggle_favorite(prompt_id):
    """Toggle favorite status."""
    prompt = prompt_store.toggle_favorite(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify(prompt)


@app.route("/api/search", methods=["GET"])
def search_prompts():
    """Search prompts."""
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))

    if not query:
        return jsonify({"results": []})

    results = prompt_store.search(query, limit)
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route("/api/tags", methods=["GET"])
def list_tags():
    """List all tags."""
    return jsonify({"tags": prompt_store.get_tags()})


@app.route("/api/categories", methods=["GET"])
def list_categories():
    """List all categories."""
    return jsonify({"categories": prompt_store.get_categories()})


@app.route("/api/export", methods=["GET"])
def export_prompts():
    """Export all prompts."""
    return jsonify(prompt_store.export_all())


@app.route("/api/import", methods=["POST"])
def import_prompts():
    """Import prompts."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    replace = data.get("replace", False)
    result = prompt_store.import_prompts(data, replace)

    return jsonify(result), 201


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get overall statistics."""
    prompts = list(prompt_store.prompts.values())
    return jsonify({
        "total_prompts": len(prompts),
        "total_tags": len(prompt_store.get_tags()),
        "total_categories": len(prompt_store.get_categories()),
        "favorite_count": sum(1 for p in prompts if p.get("favorite")),
        "most_used": sorted(prompts, key=lambda p: p.get("usage_count", 0), reverse=True)[:5],
    })


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Prompt API Server - Flask-based Prompt Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prompt_api.py                    Start server (port 5000)
  python prompt_api.py --port 8080        Custom port
  python prompt_api.py --debug            Debug mode
        """,
    )

    parser.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    logger.info(f"Starting Prompt API Server on {args.host}:{args.port}")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
