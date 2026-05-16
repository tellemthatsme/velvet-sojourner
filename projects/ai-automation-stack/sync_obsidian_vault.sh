#!/bin/bash
# =============================================================================
# Obsidian Vault Sync Script
# =============================================================================
# Exports chat files to Obsidian vault and syncs with rclone to Google Drive.
#
# Usage:
#   bash sync_obsidian_vault.sh              # Run full sync (export + rclone)
#   bash sync_obsidian_vault.sh export       # Only export new chats
#   bash sync_obsidian_vault.sh rclone       # Only run rclone sync
#   bash sync_obsidian_vault.sh dry-run      # Show what would be synced
#
# Input:
#   - exports/ folder with sorted chat exports
#
# Output:
#   - Obsidian/AI-Vault/ directory
#   - Google Drive backup
#
# Configuration:
#   Set RCLONE_DRIVE_REMOTE in .env (default: "gdrive")
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORTS_DIR="${SCRIPT_DIR}/exports"
OBSIDIAN_DIR="${SCRIPT_DIR}/../Obsidian/AI-Vault"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/vault_sync_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Load environment variables
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# Rclone configuration
DRIVE_REMOTE="${RCLONE_DRIVE_REMOTE:-gdrive}"

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
log_debug() { log "DEBUG" "${BLUE}$*${NC}"; }

# Create log directory
mkdir -p "${LOG_DIR}"

# =============================================================================
# Export Functions
# =============================================================================

find_exports() {
    log_info "Finding new exports..."
    
    local count=0
    local total=0
    
    # Find all markdown files in exports
    while IFS= read -r -d '' file; do
        total=$((total + 1))
        
        # Get relative path
        rel_path="${file#$EXPORTS_DIR/}"
        
        # Get target path in Obsidian vault
        target_path="${OBSIDIAN_DIR}/${rel_path}"
        
        # Check if file needs to be copied
        if [ ! -f "${target_path}" ]; then
            # New file - copy it
            mkdir -p "$(dirname "${target_path}")"
            cp "${file}" "${target_path}"
            log_info "  📄 New: ${rel_path}"
            count=$((count + 1))
        elif [ "${file}" -nt "${target_path}" ]; then
            # Updated file - copy it
            cp "${file}" "${target_path}"
            log_info "  🔄 Updated: ${rel_path}"
            count=$((count + 1))
        fi
    done < <(find "${EXPORTS_DIR}" -type f -name "*.md" -print0 2>/dev/null || true)
    
    log_info "Found ${total} files, ${count} new/updated"
    echo "${count}"
}

create_daily_note() {
    local date_str=$(date +%Y-%m-%d)
    local daily_note="${OBSIDIAN_DIR}/Daily/${date_str}.md"
    
    log_info "Creating daily note..."
    
    mkdir -p "$(dirname "${daily_note}")"
    
    cat > "${daily_note}" << EOF
---
title: Daily Notes $(date +%Y-%m-%d)
created: ${TIMESTAMP}
tags: [daily, log]
---

# $(date +%A, %B %d, %Y)

## Today's Exports

EOF

    # List today's exports
    find "${EXPORTS_DIR}" -type f -name "*$(date +%Y-%m-%d)*.md" -printf "  - [[%P]]\n" >> "${daily_note}" 2>/dev/null || true
    
    echo "" >> "${daily_note}"
    echo "## Inbox" >> "${daily_note}" >> "${daily_note}"
    echo "" >> "${daily_note}"
    echo "## Notes" >> "${daily_note}"
    
    log_info "Daily note created: ${daily_note}"
}

update_index() {
    log_info "Updating vault index..."
    
    local index_file="${OBSIDIAN_DIR}/.vault_index.md"
    
    cat > "${index_file}" << EOF
---
title: Vault Index
last_updated: ${TIMESTAMP}
---

# AI Automation Vault Index

Generated: ${TIMESTAMP}

## Directory Structure

\`\`\`
$(cd "${OBSIDIAN_DIR}" && find . -type f -name "*.md" | sed 's|^\./||' | head -100)
\`\`\`

## Tags

$(cd "${OBSIDIAN_DIR}" && find . -type f -name "*.md" -exec grep -h '^tags:' {} \; 2>/dev/null | sed 's/tags: //' | tr ',' '\n' | sort | uniq -c | sort -rn | head -20)

## Recently Added

$(find "${OBSIDIAN_DIR}" -type f -name "*.md" -mtime -7 -printf "  - [[%P]] (%Tm/%Td)\n" 2>/dev/null | head -20 || echo "  No recent files")

EOF

    log_info "Index updated: ${index_file}"
}

# =============================================================================
# Rclone Functions
# =============================================================================

sync_vault() {
    log_info "Syncing vault to Google Drive..."
    
    if ! command -v rclone &> /dev/null; then
        log_error "rclone not found. Install with: brew install rclone"
        return 1
    fi
    
    if ! rclone listremotes | grep -q "^${DRIVE_REMOTE}$"; then
        log_error "Remote '${DRIVE_REMOTE}' not configured."
        return 1
    fi
    
    # Sync with deduping
    rclone sync "${OBSIDIAN_DIR}" "${DRIVE_REMOTE}:ai-automation/obsidian" \
        --verbose \
        --log-file "${LOG_FILE}" \
        --stats-one-line \
        --dedup-mode older \
        --modify-window 1s
    
    log_info "Vault synced to Google Drive"
}

# =============================================================================
# Main Functions
# =============================================================================

run_export() {
    log_info "========================================"
    log_info "  Export Phase"
    log_info "========================================"
    
    # Ensure directories exist
    mkdir -p "${EXPORTS_DIR}"
    mkdir -p "${OBSIDIAN_DIR}"
    
    # Find and copy new exports
    local count
    count=$(find_exports)
    
    # Create daily note
    create_daily_note
    
    # Update index
    update_index
    
    log_info "Export phase complete: ${count} files processed"
}

run_rclone() {
    log_info "========================================"
    log_info "  Rclone Sync Phase"
    log_info "========================================"
    
    sync_vault
    
    log_info "Rclone sync complete"
}

run_dry_run() {
    log_info "🔍 Dry run - showing what would be synced..."
    
    echo ""
    echo "Exports directory:"
    du -sh "${EXPORTS_DIR}" 2>/dev/null || echo "  Not found"
    echo ""
    echo "Obsidian directory:"
    du -sh "${OBSIDIAN_DIR}" 2>/dev/null || echo "  Not found"
    echo ""
    echo "Files that would be copied:"
    find "${EXPORTS_DIR}" -type f -name "*.md" -newer "${OBSIDIAN_DIR}" 2>/dev/null | head -20 || echo "  None"
    echo ""
    echo "Rclone would sync ${OBSIDIAN_DIR} to ${DRIVE_REMOTE}:ai-automation/obsidian"
}

cleanup() {
    log_info "Cleaning up old logs..."
    find "${LOG_DIR}" -name "vault_sync_*.log" -mtime +30 -delete 2>/dev/null || true
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local mode="${1:-all}"
    
    echo ""
    echo "========================================"
    echo "  Obsidian Vault Sync"
    echo "========================================"
    echo ""
    echo "Started: ${TIMESTAMP}"
    echo "Log file: ${LOG_FILE}"
    echo ""
    
    case "${mode}" in
        export)
            run_export
            ;;
        rclone)
            run_rclone
            ;;
        dry-run)
            run_dry_run
            ;;
        all|*)
            run_export
            run_rclone
            cleanup
            log_info "========================================"
            log_info "  Sync Complete"
            log_info "========================================"
            ;;
    esac
    
    echo ""
    echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Run main function
main "$@"
