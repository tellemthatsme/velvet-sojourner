# Full System Audit & Organization Plan

## Phase 1: AUDIT & REPORT (Do NOT move anything)
### 1.1 Audit E: Drive
- [ ] List all folders on E: drive
- [ ] Count files by type (FB exports, videos, photos, backups)
- [ ] Calculate total size by category
- [ ] Identify backup folders and their sizes
- [ ] Flag large/duplicate files
- [ ] **OUTPUT:** E_DRIVE_AUDIT_REPORT.md

### 1.2 Audit C: Downloads\Text_Files
- [ ] List all txt files
- [ ] Categorize by type (claude chats, notes, exports, etc.)
- [ ] Calculate total size
- [ ] Identify duplicates across folders
- [ ] **OUTPUT:** DOWNLOADS_TXT_AUDIT.md

### 1.3 Audit C: Documents
- [ ] List all txt files in Documents
- [ ] Categorize by type
- [ ] Calculate total size
- [ ] **OUTPUT:** DOCUMENTS_TXT_AUDIT.md

### 1.4 Audit ChatGPT Exports
- [ ] leahchatgptexport/ - count conversations, extract metadata
- [ ] woodschatgptexport/ - count conversations, extract metadata
- [ ] tellemchatgptexport/ - count conversations, extract metadata
- [ ] ashchatgptexpot.zip - extract and audit
- [ ] C:/ChatGPT_Complete_Archive/ - analyze existing processed archive
- [ ] **OUTPUT:** CHATGPT_EXPORTS_AUDIT.md

### 1.5 Combined Audit Report
- [ ] Create MASTER_AUDIT_REPORT.md with:
  - Summary of all data sources
  - Total sizes by category
  - Recommendations for organization
  - Space savings estimates

## Phase 2: STRATEGIC ORGANIZATION (DNT PROTECTED)
### 2.1 Consolidate General Backups on E:
- [x] Create `E:/MASTER_ARCHIVE_2026/`
- [x] Move `E:/Archive/` content to `E:/MASTER_ARCHIVE_2026/LEGACY_ARCHIVE/`
- [x] Move `E:/AI_ARMY_BACKUP_20260202/` to `E:/MASTER_ARCHIVE_2026/AI_ARMY_BACKUPS/`
- [x] Move `E:/Chrome_Backup_*` to `E:/MASTER_ARCHIVE_2026/SYSTEM_BACKUPS/Chrome/`
- [x] **SAFETY:** Skip any folder containing `DNT_PROTECTION.md`

### 2.2 Relocate OS-Drive Text Logs
- [x] Create `E:/MASTER_ARCHIVE_2026/OS_DRIVE_DATA/Documents_Text/`
- [x] Move identified `.txt` files from `C:/Users/karma/Documents/` to E: drive.
- [x] **NOTE:** Skip the `Downloads/Text_Files` (Audit returned 0 files).

### 2.3 Skip ChatGPT Exports (MANUAL ONLY)
- [x] **OFF-LIMITS:** Do not move `C:/Users/karma/chatgptexports/`
- [x] **OFF-LIMITS:** Do not move `E:/chatgptexports/`
- [x] **OFF-LIMITS:** Do not move `C:/Users/karma/Documents/chatgptexports/`

## Output Reports
1. **E_DRIVE_AUDIT_REPORT.md** - COMPLETE
2. **DOWNLOADS_TXT_AUDIT.md** - COMPLETE
3. **DOCUMENTS_TXT_AUDIT.md** - COMPLETE
4. **CHATGPT_EXPORTS_AUDIT.md** - COMPLETE
5. **MASTER_AUDIT_REPORT.md** - COMPLETE
6. **ORGANIZATION_LOG_2026.md** - COMPLETE
