#!/bin/bash
# =============================================================================
# Google Drive Sync Script - Rclone-based Backup
# =============================================================================
# Syncs projects/ and Obsidian/ folders to Google Drive with deduping and retries.
#
# Usage:
#   bash sync_drive.sh                    # Run full sync
#   bash sync_drive.sh projects           # Sync only projects
#   bash sync_drive.sh obsidian           # Sync only Obsidian vault
#   bash sync_drive.sh dry-run            # Show what would be synced
#   bash sync_drive.sh check              # Check rclone config
#
# Prerequisites:
#   1. Install rclone: https://rclone.org/install/
#   2. Configure Google Drive: rclone config
#   3. Set DRIVE_REMOTE in .env or environment variable
#
# Configuration:
#   Set RCLONE_DRIVE_REMOTE in .env (default: "gdrive")
#   Set RCLONE_CONFIG_PATH in .env for custom rclone.conf location
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/drive_sync_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Load environment variables
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# Rclone configuration
DRIVE_REMOTE="${RCLONE_DRIVE_REMOTE:-gdrive}"
PROJECTS_DIR="${SCRIPT_DIR}"
OBSIDIAN_DIR="${SCRIPT_DIR}/../Obsidian/AI-Vault"

# Retry settings
MAX_RETRIES=3
RETRY_DELAY=5
RETRY_BACKOFF=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "${GREEN}$*${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

log_error() {
    log "ERROR" "${RED}$*${NC}"
}

log_debug() {
    if [ "${VERBOSE:-false}" = "true" ]; then
        log "DEBUG" "${BLUE}$*${NC}"
    fi
}

# Create log directory
mkdir -p "${LOG_DIR}"

# =============================================================================
# Rclone Functions
# =============================================================================

check_rclone() {
    if ! command -v rclone &> /dev/null; then
        log_error "rclone not found. Install with: brew install rclone"
        return 1
    fi
    
    log_info "rclone version: $(rclone version --short)"
}

check_config() {
    log_info "Checking rclone configuration..."
    
    if ! rclone listremotes | grep -q "^${DRIVE_REMOTE}$"; then
        log_error "Remote '${DRIVE_REMOTE}' not configured."
        log_info "Run 'rclone config' to set up Google Drive."
        return 1
    fi
    
    log_info "Using remote: ${DRIVE_REMOTE}"
    return 0
}

check_connection() {
    log_info "Checking Google Drive connection..."
    
    if rclone about "${DRIVE_REMOTE}:" &> /dev/null; then
        local total=$(rclone about "${DRIVE_REMOTE}:" --json 2>/dev/null | grep -o '"quota":[0-9]*' | cut -d: -f2 | numfmt --from=iec 2>/dev/null || echo "Unknown")
        log_info "Google Drive connection OK"
        return 0
    else
        log_error "Cannot connect to Google Drive"
        return 1
    fi
}

sync_directory() {
    local source_dir="$1"
    local dest_path="$2"
    local description="$3"
    local extra_args="${4:-}"
    
    if [ ! -d "${source_dir}" ]; then
        log_warn "Source directory not found: ${source_dir}"
        return 0
    fi
    
    log_info "Syncing ${description}..."
    log_info "  From: ${source_dir}"
    log_info "  To: ${DRIVE_REMOTE}:${dest_path}"
    
    local attempt=1
    local success=false
    
    while [ $attempt -le $MAX_RETRIES ]; do
        log_info "Attempt ${attempt}/${MAX_RETRIES}..."
        
        # Build rclone command with deduping options
        local cmd="rclone sync"
        cmd="${cmd} '${source_dir}'"
        cmd="${cmd} '${DRIVE_REMOTE}:${dest_path}'"
        cmd="${cmd} --verbose"
        cmd="${cmd} --log-file '${LOG_FILE}'"
        cmd="${cmd} --stats-one-line"
        cmd="${cmd} --stats 10s"
        cmd="${cmd} --dedup-mode older"  # Prefer older files when duplicate
        cmd="${cmd} --ignore-size"       # Ignore size for faster sync
        cmd="${cmd} --modify-window 1s"  # Allow 1s timestamp variance
        
        # Add extra args if provided
        if [ -n "${extra_args}" ]; then
            cmd="${cmd} ${extra_args}"
        fi
        
        log_debug "Running: ${cmd}"
        
        if eval "${cmd}" 2>&1 | tee -a "${LOG_FILE}"; then
            success=true
            log_info "✅ ${description} synced successfully"
            break
        else
            log_warn "Sync attempt ${attempt} failed"
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                local wait_time=$((RETRY_DELAY * RETRY_BACKOFF ** (attempt - 1)))
                log_info "Waiting ${wait_time} seconds before retry..."
                sleep ${wait_time}
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    if [ "$success" = false ]; then
        log_error "❌ Failed to sync ${description} after ${MAX_RETRIES} attempts"
        return 1
    fi
    
    return 0
}

run_dry_run() {
    log_info "🔍 Dry run - showing what would be synced..."
    
    echo ""
    echo "Projects Directory:"
    rclone size "${PROJECTS_DIR}" 2>/dev/null || echo "  Not found"
    echo ""
    echo "Obsidian Directory:"
    rclone size "${OBSIDIAN_DIR}" 2>/dev/null || echo "  Not found"
    echo ""
    
    echo "Projects changes:"
    rclone sync "${PROJECTS_DIR}" "${DRIVE_REMOTE}:ai-automation/projects" --dry-run 2>&1 | head -20
    echo ""
    echo "Obsidian changes:"
    rclone sync "${OBSIDIAN_DIR}" "${DRIVE_REMOTE}:ai-automation/obsidian" --dry-run 2>&1 | head -20
}

show_status() {
    log_info "Google Drive Status:"
    echo ""
    echo "Remotes configured:"
    rclone listremotes
    echo ""
    echo "Disk usage:"
    rclone about "${DRIVE_REMOTE}:" 2>/dev/null || echo "  Could not get usage info"
    echo ""
    echo "Recent changes in destination:"
    rclone ls "${DRIVE_REMOTE}:ai-automation" --max-age 24h 2>/dev/null | head -20 || echo "  No recent changes"
}

cleanup_old_logs() {
    log_info "Cleaning up old logs..."
    find "${LOG_DIR}" -name "drive_sync_*.log" -mtime +30 -delete 2>/dev/null || true
    log_info "Logs older than 30 days removed"
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local mode="${1:-all}"
    
    echo ""
    echo "========================================"
    echo "  Google Drive Sync - Rclone Backup"
    echo "========================================"
    echo ""
    echo "Started: ${TIMESTAMP}"
    echo "Log file: ${LOG_FILE}"
    echo ""
    
    # Parse arguments
    case "${mode}" in
        dry-run)
            VERBOSE=true
            check_rclone || exit 1
            check_config || exit 1
            run_dry_run
            ;;
        check)
            check_rclone || exit 1
            check_config || exit 1
            check_connection || exit 1
            show_status
            ;;
        projects)
            check_rclone || exit 1
            check_config || exit 1
            sync_directory "${PROJECTS_DIR}" "ai-automation/projects" "Projects directory"
            ;;
        obsidian)
            check_rclone || exit 1
            check_config || exit 1
            sync_directory "${OBSIDIAN_DIR}" "ai-automation/obsidian" "Obsidian vault"
            ;;
        all|*)
            check_rclone || exit 1
            check_config || exit 1
            check_connection || exit 1
            
            # Sync projects first
            sync_directory "${PROJECTS_DIR}" "ai-automation/projects" "Projects directory" || true
            
            # Sync Obsidian vault
            sync_directory "${OBSIDIAN_DIR}" "ai-automation/obsidian" "Obsidian vault" || true
            
            # Cleanup old logs
            cleanup_old_logs
            
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
