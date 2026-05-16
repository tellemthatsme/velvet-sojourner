# Knowledge Base & Wiki Organization Plan

## Overview
Process 4 ChatGPT exports (leah, tellem, woods, ash), organize all txt files, and build a searchable wiki/RAG system.

## Source Data
- **ChatGPT Exports:** `C:\Users\karma\chatgptexports\`
  - leahchatgptexport/ (conversations.json, chat.html)
  - woodschatgptexport/ (conversations.json, chat.html)
  - tellemchatgptexport/ (conversations.json, chat.html)
  - ashchatgptexpot.zip (needs extraction)
- **Additional Sources:** Downloads folder txt files, Documents folder

## Target Output
- **Wiki Location:** `C:/KARMA_WIKI/`
- **RAG Data:** `C:/KARMA_WIKI/rag_data/`
- **Code Archive:** `C:/KARMA_WIKI/code_archive/`

## Processing Steps

### Phase 1: Export Processing (4 accounts)
1. [ ] Extract ashchatgptexpot.zip
2. [ ] Load each conversations.json:
   - leahchatgptexport
   - woodschatgptexport
   - tellemchatgptexport
   - ashchatgptexport
3. [ ] For each conversation extract:
   - Conversation ID
   - First 1-2 messages (starting prompt)
   - Last message / summary
   - Number of messages
   - Category tags
   - All user prompts (requests for prompts)
   - All code blocks (move to code_archive)

### Phase 2: Per-Conversation Analysis
1. [ ] Identify project/topic for each conversation
2. [ ] Extract all user prompts (especially requests like "provide a prompt for...")
3. [ ] Extract all AI-generated prompts
4. [ ] Extract guides and tutorials
5. [ ] Extract links and resources
6. [ ] Remove all code blocks → move to code_archive by topic

### Phase 3: Categorization & Sorting
1. [ ] Create category structure:
   - AI Development (code, scripts, tools)
   - Prompts & Instructions
   - Documentation & Guides
   - Business & Revenue
   - APIs & Integrations
   - Configuration & Setup
   - Other/Personal
2. [ ] Sort conversations into categories
3. [ ] Merge conversations about same project across accounts

### Phase 4: Wiki Structure Creation
```
C:/KARMA_WIKI/
├── 00_INDEX.md                    # Main index
├── 01_PROMPTS/                    # All extracted prompts
│   ├── BY_CATEGORY/               # Prompts by type
│   └── BY_PROJECT/                # Prompts by project
├── 02_CONVERSATIONS/              # Organized conversations
│   ├── LEAH/
│   ├── WOODS/
│   ├── TELLEM/
│   └── ASH/
├── 03_GUIDES/                     # All extracted guides
├── 04_CODE/                       # Code archive by topic
├── 05_PROJECTS/                   # Project-based organization
├── 06_LINKS/                      # All extracted links
├── rag_data/
│   ├── chunks.json               # RAG-ready text chunks
│   ├── embeddings_index.json      # Embeddings index
│   └── metadata.json             # Source tracking
└── exports/                       # Original exports backup
```

### Phase 5: RAG Memory Population
1. [ ] Split all content into chunks (512-1024 tokens)
2. [ ] Generate metadata for each chunk
3. [ ] Create search index
4. [ ] Build source attribution

## Deliverables
1. **Wiki:** Fully navigable markdown wiki at C:/KARMA_WIKI/
2. **Prompts Library:** All prompts organized by category and project
3. **Code Archive:** All code extracted and sorted by topic
4. **RAG System:** Ready-to-use RAG data with search capabilities
5. **Conversation Summaries:** Quick-reference for all conversations

## Notes
- All original files remain untouched
- Code separated from conversations for easier reference
- Each conversation tagged with project/topic
- Cross-references between related conversations
