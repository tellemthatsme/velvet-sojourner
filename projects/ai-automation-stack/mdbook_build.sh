#!/bin/bash
# =============================================================================
# Markdown Wiki Builder - mdbook Static Site Generator
# =============================================================================
# Scans markdown folders and builds static HTML wiki using mdbook.
#
# Usage:
#   bash mdbook_build.sh                    Build wiki (default: docs/)
#   bash mdbook_build.sh ./my-docs          Build from custom directory
#   bash book_build.sh serve                Serve locally for testing
#   bash mdbook_build.sh watch              Watch for changes and rebuild
#   bash mdbook_build.sh clean              Clean build artifacts
#
# Prerequisites:
#   - mdbook installed: cargo install mdbook
#   - Or: brew install mdbook
#
# Configuration:
#   Set MDBOOK_SOURCE in .env (default: docs/)
#   Set MDBOOK_TITLE in .env (default: AI Automation Wiki)
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/wiki_build_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Load environment variables
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# mdbook configuration
MDBOOK_SOURCE="${MDBOOK_SOURCE:-docs}"
MDBOOK_TITLE="${MDBOOK_TITLE:-AI Automation Wiki}"
MDBOOK_DEST="${MDBOOK_DEST:-book}"
MDBOOK_THEME="${SCRIPT_DIR}/.mdbook_theme"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() { log "INFO" "${GREEN}$*${NC}"; }
log_warn() { log "WARN" "${YELLOW}$*${NC}"; }
log_error() { log "ERROR" "${RED}$*${NC}"; }
log_step() { log "STEP" "${CYAN}$*${NC}"; }

# Create log directory
mkdir -p "${LOG_DIR}"

# =============================================================================
# Helper Functions
# =============================================================================

check_mdbook() {
    if ! command -v mdbook &> /dev/null; then
        log_error "mdbook not found."
        log_info "Install with: cargo install mdbook"
        log_info "Or: brew install mdbook"
        return 1
    fi
    log_info "mdbook version: $(mdbook --version)"
    return 0
}

create_book_toml() {
    local source_dir="$1"
    local book_toml="${source_dir}/book.toml"

    log_info "Creating book.toml..."

    cat > "${book_toml}" << EOF
[book]
title = "${MDBOOK_TITLE}"
authors = ["AI Automation System"]
description = "Auto-generated wiki from markdown files"
language = "en"

[build]
build-dir = "${MDBOOK_DEST}"
create-missing = true

[preprocess]
markdown = { header-links = true }

[output.html]
git-repository-url = ""
edit-url-template = ""
site-url = "/"
theme = "${MDBOOK_THEME}"
table-of-contents = { collapse = "section" }
search = { use-ingress-defaults = false }
EOF

    log_info "book.toml created at ${book_toml}"
}

scan_markdown_files() {
    local source_dir="$1"

    log_info "Scanning for markdown files in ${source_dir}..."

    local count=$(find "${source_dir}" -name "*.md" -type f | wc -l)

    if [ "${count}" -eq 0 ]; then
        log_warn "No markdown files found in ${source_dir}"
        log_info "Create some .md files or check MDBOOK_SOURCE setting"
        return 1
    fi

    log_info "Found ${count} markdown files"
    echo "${count}"
}

generate_summary() {
    local source_dir="$1"
    local summary_file="${source_dir}/SUMMARY.md"

    log_info "Generating SUMMARY.md..."

    # Get all markdown files, sorted
    local files
    files=$(find "${source_dir}" -name "*.md" -type f ! -name "book.toml" ! -name "SUMMARY.md" | sort)

    # Generate SUMMARY content
    {
        echo "# Summary"
        echo ""
        echo "- [Introduction](./README.md)"
        echo ""
        echo "## Core Documentation"

        # Group files by directory
        local prev_dir=""

        while IFS= read -r file; do
            local relative="${file#$source_dir/}"
            local dir=$(dirname "${relative}")

            # Handle root level files
            if [ "${dir}" = "." ]; then
                if [ "${prev_dir}" != "." ]; then
                    echo ""
                fi
                echo "- [${file:t:r}](./${relative})"
                prev_dir="."
            else
                # Handle nested files
                if [ "${dir}" != "${prev_dir}" ]; then
                    echo ""
                    echo "### ${dir}"
                    prev_dir="${dir}"
                fi
                local title=$(head -1 "${file}" | sed 's/^#* *//' | tr -d '\r\n')
                [ -z "${title}" ] && title="${file:t:r}"
                echo "- [${title}](./${relative})"
            fi
        done <<< "${files}"

        echo ""
        echo "---"
        echo ""
        echo "*Generated on ${TIMESTAMP}*"

    } > "${summary_file}"

    log_info "SUMMARY.md created with $(echo "${files}" | wc -l) entries"
}

build_wiki() {
    local source_dir="${1:-$MDBOOK_SOURCE}"

    log_step "Building Wiki"
    echo "========================================"
    echo ""

    if [ ! -d "${source_dir}" ]; then
        log_error "Source directory not found: ${source_dir}"
        log_info "Create directory or set MDBOOK_SOURCE in .env"
        return 1
    fi

    # Check for at least one markdown file
    local file_count=$(find "${source_dir}" -name "*.md" -type f ! -name "book.toml" | wc -l)
    if [ "${file_count}" -eq 0 ]; then
        log_warn "No markdown files found. Creating sample..."
        create_sample_docs "${source_dir}"
    fi

    # Create book.toml if missing
    if [ ! -f "${source_dir}/book.toml" ]; then
        create_book_toml "${source_dir}"
    fi

    # Create SUMMARY.md if missing
    if [ ! -f "${source_dir}/SUMMARY.md" ]; then
        generate_summary "${source_dir}"
    fi

    # Run mdbook build
    log_info "Running mdbook build..."

    if mdbook build "${source_dir}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_info "✅ Wiki built successfully!"
        log_info "Output: ${source_dir}/${MDBOOK_DEST}/index.html"

        # Show statistics
        local html_count=$(find "${source_dir}/${MDBOOK_DEST}" -name "*.html" | wc -l)
        log_info "Generated ${html_count} HTML files"

        return 0
    else
        log_error "mdbook build failed"
        return 1
    fi
}

serve_wiki() {
    local source_dir="${1:-$MDBOOK_SOURCE}"

    log_info "Starting mdbook server..."
    log_info "Press Ctrl+C to stop"
    log_info ""
    log_info "View at: http://localhost:3000"

    mdbook serve "${source_dir}" --port 3000 --hostname 0.0.0.0
}

watch_wiki() {
    local source_dir="${1:-$MDBOOK_SOURCE}"

    log_info "Watching for changes..."
    log_info "Press Ctrl+C to stop"

    # Use entr if available, otherwise use mdbook watch
    if command -v entr &> /dev/null; then
        find "${source_dir}" -name "*.md" | entr -c mdbook build "${source_dir}"
    else
        mdbook watch "${source_dir}" --port 3000
    fi
}

clean_wiki() {
    local source_dir="${1:-$MDBOOK_SOURCE}"

    log_info "Cleaning build artifacts..."

    # Remove build directory
    if [ -d "${source_dir}/${MDBOOK_DEST}" ]; then
        rm -rf "${source_dir}/${MDBOOK_DEST}"
        log_info "Removed ${MDBOOK_DEST}/ directory"
    fi

    # Remove generated files
    rm -f "${source_dir}/book.toml"
    rm -f "${source_dir}/SUMMARY.md"

    log_info "Clean complete"
}

create_sample_docs() {
    local source_dir="$1"

    log_info "Creating sample documentation..."

    mkdir -p "${source_dir}"

    # Create README
    cat > "${source_dir}/README.md" << 'EOF'
# AI Automation Wiki

Welcome to the AI Automation System documentation.

## Contents

See the [Summary](./SUMMARY.md) for all available documentation.

## Quick Links

- [Core Modules](./core-modules.md)
- [API Documentation](./api.md)
- [Setup Guide](./setup.md)

---
*Auto-generated by mdbook_build.sh*
EOF

    # Create sample pages
    cat > "${source_dir}/core-modules.md" << 'EOF'
# Core Modules

## Overview

The AI Automation Stack consists of several core modules:

### 1. Voice Assistant

Voice-controlled command execution using local Whisper.

### 2. GitHub Sync

Automated repository synchronization with rate limiting.

### 3. RAG Embedder

Knowledge base vector search using FAISS and OpenAI.

### 4. Post Generator

AI-powered social media content creation.

## Usage

See individual module documentation for detailed usage.
EOF

    cat > "${source_dir}/setup.md" << 'EOF'
# Setup Guide

## Prerequisites

- Python 3.8+
- OpenAI API key
- GitHub token (for sync features)
- rclone (for cloud backup)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` with your API keys
4. Run: `python launch.py`

## Configuration

Copy `.env.example` to `.env` and fill in your API keys.
EOF

    cat > "${source_dir}/api.md" << 'EOF'
# API Documentation

## Prompt API

Running on port 5000 by default.

### Endpoints

- `GET /api/prompts` - List all prompts
- `POST /api/prompts` - Create a prompt
- `GET /api/prompts/<id>` - Get a prompt
- `PUT /api/prompts/<id>` - Update a prompt
- `DELETE /api/prompts/<id>` - Delete a prompt

## Search API

Running on port 5001 by default.

### Endpoints

- `GET /api/search?q=` - Full-text search
- `GET /api/list` - List all files
- `GET /api/stats` - Get statistics
EOF

    log_info "Sample documentation created in ${source_dir}"
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local mode="${1:-build}"

    echo ""
    echo "========================================"
    echo "  Markdown Wiki Builder - mdbook"
    echo "========================================"
    echo ""
    echo "Started: ${TIMESTAMP}"
    echo "Log file: ${LOG_FILE}"
    echo ""

    case "${mode}" in
        build)
            check_mdbook || exit 1
            build_wiki
            ;;
        serve)
            check_mdbook || exit 1
            serve_wiki
            ;;
        watch)
            check_mdbook || exit 1
            watch_wiki
            ;;
        clean)
            clean_wiki
            ;;
        init)
            source_dir="${2:-$MDBOOK_SOURCE}"
            mkdir -p "${source_dir}"
            create_sample_docs "${source_dir}"
            generate_summary "${source_dir}"
            create_book_toml "${source_dir}"
            log_info "Wiki initialized in ${source_dir}"
            ;;
        *)
            echo "Usage: $0 {build|serve|watch|clean|init} [source_dir]"
            echo ""
            echo "Commands:"
            echo "  build [dir]  - Build wiki (default: ${MDBOOK_SOURCE})"
            echo "  serve        - Serve locally on port 3000"
            echo "  watch        - Watch for changes and rebuild"
            echo "  clean        - Clean build artifacts"
            echo "  init [dir]   - Initialize new wiki with sample docs"
            exit 1
            ;;
    esac

    echo ""
    echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Run main function
main "$@"
