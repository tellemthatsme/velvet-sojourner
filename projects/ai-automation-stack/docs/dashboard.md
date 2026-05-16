# Dashboard Documentation

## Overview

The web dashboard provides a unified interface to control and monitor all AI Automation Stack modules.

## Access

Open `index.html` in any modern web browser:
```bash
# From the projects/ai-automation-stack directory
open index.html
# Or double-click index.html in file explorer
```

## Features

### Status Indicators

- **Voice**: Green when voice assistant is running
- **Sync**: Green when sync operations are active
- **APIs**: Green when API servers are online

### Quick Actions

Click icons to launch modules:
- 🎙️ Voice Assistant
- 🔄 Sync All
- 📁 Export Chats
- 🧠 Embed Knowledge
- 📱 Generate Posts
- 📚 Build Wiki

### Module Controls

Each module card provides:
- **Start/Stop** buttons
- **View Logs** link
- **Documentation** link

### API Interfaces

#### Prompt API Panel

1. Enter search term
2. Click "Search"
3. View results below

#### Search API Panel

1. Enter search query
2. Click "Search"
3. View document matches

### Logs

View recent logs for:
- Launcher
- Sync
- Voice

Click "Refresh" to update.

### Terminal

Execute commands directly:

```
help          - Show commands
voice start   - Start voice
voice stop    - Stop voice
sync all      - Run sync
export        - Run exporter
embed         - Build index
wiki build    - Build wiki
status        - Show status
clear         - Clear terminal
```

## Troubleshooting

### Dashboard Won't Load

1. Check file exists: `ls index.html`
2. Try different browser
3. Check browser console for errors

### APIs Not Showing Status

1. Start API servers: `python prompt_api.py` and `python search_server.py`
2. Check ports aren't blocked
3. Verify no firewall restrictions

### Modules Not Launching

Modules require CLI execution. Use terminal:
```bash
python launch.py --voice
```
