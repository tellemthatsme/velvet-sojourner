# AI Automation Stack

A comprehensive local AI productivity suite with voice automation, chat export organization, RAG knowledge base, social media automation, and more.

## 🚀 Quick Start

```bash
# Clone and enter directory
cd projects/ai-automation-stack

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Launch dashboard
python launch.py --dashboard

# Or use CLI
python launch.py --interactive
```

## 📦 Features

### 🎙️ Voice Assistant
- Local Whisper-based hotword detection
- Voice commands mapped to scripts
- Runs completely offline
- Command: `python run_voice.py`

### 🔄 Sync Stack
- GitHub repository sync with rate limiting
- Google Drive backup via rclone
- Obsidian vault synchronization
- Commands:
  - `python sync.py --repo owner/repo`
  - `bash sync_drive.sh`
  - `bash sync_obsidian_vault.sh`

### 📁 Chat Exporter
- Parse exports from ChatGPT, Claude, Gemini
- Organize by date, topic, source
- Convert PDF/HTML to Markdown
- Deduplicate and tag automatically
- Command: `python export_sorter.py`

### 🧠 RAG Knowledge Base
- OpenAI embeddings with FAISS
- Semantic search across documents
- Supports Markdown, PDF, HTML, TXT
- Commands:
  - `python embed.py` - Build index
  - `python embed.py --search "query"` - Search

### 📱 Social Media Automation
- AI-powered post generation
- Multiple style templates
- Daily scheduling
- Twitter/X + Bluesky support
- Commands:
  - `python post_gen.py --topic "your topic"`
  - `python send_posts.py`

### 📚 Wiki Builder
- Static HTML documentation via mdbook
- Full-text search
- Auto-generated navigation
- Command: `bash mdbook_build.sh`

### 🌐 APIs
- **Prompt API** (port 5000): Store, tag, version prompts
- **Search API** (port 5001): Full-text markdown search
- Endpoints:
  - `GET /api/prompts` - List prompts
  - `GET /api/search?q=` - Search documents

### 🎨 Dashboard
- Web interface for all modules
- Real-time status monitoring
- Quick action buttons
- Log viewer
- Open: `index.html` in browser

### 🔌 Browser Extension
- Auto-scrape chats from lovable.dev, v0.dev, bolt.new
- Save to localStorage
- Export to JSON
- Hotkey: Ctrl+Shift+E

## 📁 Directory Structure

```
projects/ai-automation-stack/
├── launch.py              # Master launcher
├── cli_trigger.py         # CLI module trigger
├── run_voice.py           # Voice assistant
├── commands.json          # Voice command mappings
├── sync.py                # GitHub sync
├── sync_drive.sh          # Drive backup
├── sync_obsidian_vault.sh # Vault sync
├── post_gen.py            # Post generator
├── send_posts.py          # Post scheduler
├── embed.py               # RAG embedder
├── prompt_api.py          # Prompt API server
├── search_server.py       # Search API server
├── mdbook_build.sh        # Wiki builder
├── export_sorter.py       # Chat exporter
├── index.html             # Dashboard
├── chrome-extension/      # Browser extension
├── logs/                  # Log files
├── schedule/              # Post schedules
├── posts/                 # Generated posts
├── docs/                  # Documentation
└── exports/               # Sorted chat exports

Obsidian/
└── AI-Vault/              # Obsidian vault

.github/
└── workflows/
    └── obsidian-vault.yml # Auto-backup workflow
```

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Git
- FFmpeg (for audio processing)
- rclone (for cloud sync)
- mdbook (for wiki, optional)

### Python Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
- `flask` - Web server
- `flask-cors` - CORS support
- `openai` - AI API client
- `requests` - HTTP client
- `python-dotenv` - Environment variables
- `langchain` - RAG framework
- `faiss-cpu` - Vector database
- `pypdf` - PDF processing
- `beautifulsoup4` - HTML parsing
- `tweepy` - Twitter API
- `atproto` - Bluesky API

### System Dependencies

**macOS:**
```bash
brew install ffmpeg rclone
pip install torch torchvision torchaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg rclone
pip install torch torchvision torchaudio
```

**Windows:**
```powershell
winget install ffmpeg
# Download rclone from https://rclone.org/downloads/
```

### API Keys

Copy `.env.example` to `.env` and configure:

```env
# OpenAI (required for most features)
OPENAI_API_KEY=sk-...

# GitHub (for sync.py)
GITHUB_TOKEN=ghp_...

# Twitter/X (for send_posts.py)
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...

# Bluesky (for send_posts.py)
BLUESKY_HANDLE=handle.bsky.social
BLUESKY_APP_PASSWORD=...

# Google Drive (for sync_drive.sh)
RCLONE_DRIVE_REMOTE=gdrive
```

## 📖 Usage

### CLI Launcher

```bash
# Interactive menu
python launch.py --interactive

# Launch specific modules
python launch.py --voice          # Voice assistant
python launch.py --sync-github    # GitHub sync
python launch.py --embed          # Build RAG index
python launch.py --wiki           # Build wiki
python launch.py --dashboard      # Open dashboard

# Launch all modules
python launch.py --all
```

### Voice Commands

Configure in `commands.json`:
```json
{
  "start voice": {"type": "launcher", "command": "voice"},
  "sync github": {"type": "launcher", "command": "sync-github"},
  "export chats": {"type": "launcher", "command": "export"}
}
```

### Cron Scheduling

Add to crontab (`crontab -e`):

```bash
# Daily sync at 2 AM
0 2 * * * cd /path/to/projects/ai-automation-stack && bash sync_drive.sh

# Hourly GitHub sync
0 * * * * cd /path/to/projects/ai-automation-stack && python sync.py --repo owner/repo

# Daily post generation at 9 AM
0 9 * * * cd /path/to/projects/ai-automation-stack && python post_gen.py --topic "AI news"

# Weekly RAG index update
0 3 * * 0 cd /path/to/projects/ai-automation-stack && python embed.py
```

## 🔌 API Reference

### Prompt API (Port 5000)

```bash
# List prompts
curl http://localhost:5000/api/prompts

# Create prompt
curl -X POST http://localhost:5000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{"title": "My Prompt", "content": "...", "tags": ["ai"]}'

# Search prompts
curl "http://localhost:5000/api/search?q=python"

# Export all
curl http://localhost:5000/api/export
```

### Search API (Port 5001)

```bash
# Search documents
curl "http://localhost:5001/api/search?q=automation"

# List files
curl http://localhost:5001/api/list

# Get stats
curl http://localhost:5001/api/stats
```

## 🧩 Browser Extension

1. Open `chrome-extension/`
2. Load in Chrome/Firefox:
   - Chrome: chrome://extensions → "Load unpacked"
   - Firefox: about:debugging → "This Firefox" → "Load Temporary Add-on"
3. Visit lovable.dev, v0.dev, or bolt.new
4. Press Ctrl+Shift+E to export chat

## 🛠️ Development

### Running Tests

```bash
python run_tests.py
```

### Adding New Modules

1. Create Python script in `projects/ai-automation-stack/`
2. Add to `MODULES` dict in `launch.py`
3. Update `commands.json` if voice control needed
4. Add docs in `docs/`

### Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📝 Logging

Logs are stored in `logs/`:
- `launcher.log` - Master launcher
- `sync.log` - GitHub sync
- `drive_sync.log` - Drive backup
- `voice.log` - Voice assistant
- `post_gen.log` - Post generation
- `embed.log` - RAG embedding
- `export_sort.log` - Chat export

## 🔒 Security

- Store API keys in `.env`, never commit
- Use environment variables for secrets
- Review permissions before installing extension
- Keep dependencies updated

## 📄 License

MIT License - See LICENSE file

## 🙏 Credits

Built with:
- OpenAI API
- Whisper (OpenAI)
- LangChain
- FAISS
- Flask
- mdbook
- rclone
