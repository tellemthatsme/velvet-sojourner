# Charm Crush Session Manager - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Session Management](#session-management)
5. [File Editing](#file-editing)
6. [User Accounts](#user-accounts)
7. [Settings and Preferences](#settings-and-preferences)
8. [Cloud Sync](#cloud-sync)
9. [Session Sharing](#session-sharing)
10. [Search](#search)
11. [Plugins](#plugins)
12. [Keyboard Shortcuts](#keyboard-shortcuts)
13. [Troubleshooting](#troubleshooting)
14. [FAQ](#faq)

---

## Introduction

Charm Crush Session Manager is a powerful Windows desktop application designed to help you organize, edit, and manage configuration files and sessions across multiple projects.

### Key Features

- **Session Management**: Create, organize, and manage sessions with tags and templates
- **Secure Storage**: AES-128 encrypted storage for sensitive configurations
- **Multi-User Support**: Multiple user accounts with individual session libraries
- **File Editing**: Advanced text editor with syntax highlighting (JSON, YAML, INI, TXT)
- **Cloud Sync**: Synchronize sessions across devices via Dropbox, Google Drive, or OneDrive
- **Session Sharing**: Share sessions with others via secure share links
- **Search**: Powerful search across all sessions and file content
- **Plugins**: Extensible architecture for adding custom functionality

---

## Getting Started

### Installation

1. Download the latest Charm Crush installer (CharmCrush.exe)
2. Run the installer and follow the on-screen instructions
3. Launch Charm Crush from the Start Menu or desktop shortcut

### First Launch

On first launch, you'll be prompted to create an account:

1. Enter a username (3+ characters)
2. Enter a password (8+ characters)
3. Click "Register"
4. Log in with your new credentials

---

## User Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar: [File] [Session] [Edit] [View] [Help]             │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  Session Tree    │           Tabbed Editor Area             │
│  (Left Panel)    │                                          │
│                  │    ┌──────────────────────────────┐      │
│  • Session 1     │    │  Tab 1      Tab 2      ...   │      │
│    └─ file1.json │    ├──────────────────────────────┤      │
│    └─ file2.yaml │    │                              │      │
│  • Session 2     │    │     Editor Content            │      │
│    └─ config.ini │    │                              │      │
│  • Session 3     │    │                              │      │
│    └─ ...        │    └──────────────────────────────┘      │
│                  │                                          │
├──────────────────┴──────────────────────────────────────────┤
│ Status Bar: Ready | User: john | Sessions: 15              │
└─────────────────────────────────────────────────────────────┘
```

### Panels

**Session Tree Panel (Left)**
- Displays all your sessions organized hierarchically
- Expand/collapse sessions to view associated files
- Double-click sessions to expand/collapse
- Click files to open in editor

**Editor Panel (Right)**
- Tabbed interface for multiple open files
- Syntax highlighting for supported formats
- Line numbers and bracket matching
- Find/replace functionality

### Status Bar

The status bar shows:
- Current operation status
- Logged-in username
- Session count
- Memory usage (optional)

---

## Session Management

### Creating a New Session

1. Click **File → New Session** or press `Ctrl+N`
2. Enter a name for your session
3. (Optional) Add a description
4. (Optional) Select a template:
   - Empty Session
   - Web Config
   - Database Config
   - API Config
   - Custom templates
5. Click **OK**

### Managing Sessions

**Rename a Session**
1. Select the session in the tree
2. Press `F2` or right-click → **Rename**
3. Enter new name
4. Press Enter

**Duplicate a Session**
1. Select the session
2. Right-click → **Duplicate**
3. A copy will be created with " (Copy)" suffix

**Delete a Session**
1. Select the session
2. Press `Delete` or right-click → **Delete**
3. Confirm deletion (this cannot be undone)

### Adding Files to Sessions

1. Select a session in the tree
2. Click **Session → Add File to Session** or right-click → **Add File**
3. Select a config file (JSON, YAML, INI, TXT)
4. The file will be added to the session

### Session Tags

**Adding Tags**
1. Select a session
2. Right-click → **Add Tag**
3. Enter tag name
4. Press Enter

**Filtering by Tags**
1. Use the search box with tag: prefix
   - Example: `tag:web`
2. Or use Batch Operations to add/remove tags

### Session Templates

Create reusable session structures:

1. Create a session with your desired files
2. Use it as a template when creating new sessions
3. Available templates: Empty, Web Config, Database Config, API Config

---

## File Editing

### Supported File Formats

| Format | Extension | Syntax Highlighting |
|--------|-----------|---------------------|
| JSON   | .json     | Yes (braces, keys) |
| YAML   | .yaml, .yml | Yes (indentation) |
| INI    | .ini      | Yes (sections) |
| Text   | .txt      | Basic |

### Editor Features

**Syntax Highlighting**
- Automatic detection based on file extension
- Color-coded keys, values, strings

**Line Numbers**
- Toggle in Settings (View → Settings)
- Click line number to go to line

**Bracket Matching**
- Highlights matching brackets
- Shows cursor position
- Toggle in Settings

**Find and Replace**
1. Press `Ctrl+F` to find
2. Press `Ctrl+H` to find and replace
3. Options: case sensitive, whole word, regex

**Keyboard Shortcuts in Editor**
| Shortcut | Action |
|----------|--------|
| Ctrl+Z   | Undo |
| Ctrl+Y   | Redo |
| Ctrl+X   | Cut |
| Ctrl+C   | Copy |
| Ctrl+V   | Paste |
| Ctrl+S   | Save |
| Ctrl+A   | Select All |
| Ctrl+F   | Find |
| Ctrl+H   | Find/Replace |

### Saving Files

**Save**
- Click **File → Save** or press `Ctrl+S`
- Saves the current file

**Save As**
- Click **File → Save As...** or `Ctrl+Shift+S`
- Save to a new location

**Auto-Save**
Enable in Settings → Editor → Auto-save
- Configure interval (30-600 seconds)

---

## User Accounts

### Creating an Account

1. Launch Charm Crush
2. Click **Register** tab
3. Enter username and password
4. Click **Register**
5. Log in with new credentials

### Managing Password

**Change Password**
1. Go to Settings
2. Navigate to Security section
3. Enter current and new password
4. Click **Change Password**

### Multiple Users

Each user has:
- Separate encrypted database
- Private sessions (not visible to other users)
- Individual settings and preferences

### User Preferences

Store user-specific settings:
- Window position/size
- Recent files list
- Custom templates

---

## Settings and Preferences

### Opening Settings

1. Click **View → Settings...**
2. Or press `Ctrl+,`

### General Settings

| Setting | Description |
|---------|-------------|
| Theme | Dark/Light mode |
| Auto-Save | Enable automatic saving |
| Auto-Save Interval | Seconds between saves (30-600) |
| Recent Sessions | Number of items in recent list |
| Remember Last Session | Restore on startup |
| Check Updates | Check for new versions |

### Editor Settings

| Setting | Description |
|---------|-------------|
| Font Size | Editor font size (8-24) |
| Tab Size | Tab/space indentation (2-8) |
| Use Spaces | Convert tabs to spaces |
| Line Numbers | Show/hide line numbers |
| Word Wrap | Wrap long lines |
| Highlight Current Line | Highlight active line |
| Bracket Matching | Highlight matching brackets |
| Syntax Highlighting | Enable/disable colors |

### Cloud Sync Settings

| Setting | Description |
|---------|-------------|
| Enable Sync | Turn on cloud synchronization |
| Provider | Dropbox, Google Drive, OneDrive |
| Auto-Sync | Automatically sync changes |
| Sync Interval | Seconds between syncs |

### Sharing Settings

| Setting | Description |
|---------|-------------|
| Allow Sharing | Enable session sharing |
| Default Permission | View/Edit/Admin for shares |

---

## Cloud Sync

### Supported Providers

- **Dropbox** - Full support with encrypted storage
- **Google Drive** - Basic support
- **OneDrive** - Basic support

### Setting Up Cloud Sync

1. Go to **Settings → Cloud Sync**
2. Enable cloud synchronization
3. Select your provider
4. Enter credentials:
   - Dropbox: Access Token
   - Google Drive: OAuth token
   - OneDrive: OAuth token
5. Click **Connect**
6. Test the connection

### Syncing Sessions

**Manual Sync**
- Click **Sync Now** button in toolbar
- Or use `Ctrl+Shift+U`

**Auto-Sync**
- Enable in Settings
- Sessions sync automatically on changes
- Configure interval (default: 5 minutes)

### Conflict Resolution

When changes are detected on both sides:
- **Keep Local**: Use local version
- **Keep Remote**: Use cloud version
- **Merge**: Combine changes (basic implementation)

### Sync Status

Icon in status bar shows:
- ✓ Synced
- ⟳ Syncing
- ✗ Error
- ⚠ Conflict

---

## Session Sharing

### Creating a Share Link

1. Select a session
2. Click **Session → Share...** or `Ctrl+Shift+S`
3. Configure sharing options:
   - **Permission**: View/Edit/Admin
   - **Expiration**: Never, 1 day, 7 days, 30 days
   - **Access Limit**: Unlimited or specific number
   - **Password**: Optional password protection
4. Click **Create Link**
5. Copy the generated link

### Share Permissions

| Permission | Actions |
|------------|---------|
| View | Read-only access |
| Edit | Modify session content |
| Admin | Full control including delete |

### Managing Shares

**View Active Shares**
- Go to Session → Sharing → Manage Shares
- See all share links for a session

**Revoke a Share**
1. Open Manage Shares
2. Select the share link
3. Click **Revoke**

**Delete a Share**
- Permanently remove a share link

### Accessing Shared Sessions

1. Open the share link
2. If password protected, enter password
3. View or edit session based on permission
4. Optionally import to your account

### Sharing Statistics

Track sharing activity:
- Total shares created
- Access count per share
- Expiration dates

---

## Search

### Basic Search

1. Use the search box in the toolbar
2. Enter search term
3. Results update as you type
4. Click result to open session

### Advanced Search

1. Click **Search → Advanced Search...** or `Ctrl+Shift+F`
2. Configure options:
   - **Search Mode**: Simple, Advanced, Regex
   - **Scope**: Current session, All sessions, Recent
   - **Case Sensitive**: Match case
   - **Whole Word**: Match whole words only
   - **File Types**: Filter by format (JSON, YAML, etc.)
3. Click **Search**

### Search Results

Results show:
- Session name
- File path (if in file content)
- Match type (session name, file content, tag)
- Match text with context
- Relevance score

### Search History

- Recent searches appear in dropdown
- Clear history in Search options
- Export/import search history

### Search Suggestions

As you type, suggestions appear:
- From search history
- From session names
- From tags

---

## Plugins

### Installing Plugins

1. Go to **Plugins → Manage Plugins**
2. Click **Install Plugin**
3. Select plugin file (.py)
4. Review permissions
5. Click **Install**

### Managing Plugins

**Enable/Disable**
1. Open Plugin Manager
2. Find the plugin
3. Toggle enable/disable

**Configure**
1. Click **Settings** for the plugin
2. Adjust options
3. Click **Save**

### Creating Plugins

1. Go to **Plugins → Create Plugin**
2. Enter plugin ID and name
3. A template file will be created
4. Implement required methods
5. Test and install

### Plugin Events

Plugins can respond to events:
- Session created/opened/saved/deleted
- File opened/saved
- Application startup/shutdown

### Plugin Permissions

Plugins request permissions:
- File system access
- Network access
- Session data access
- UI modification

---

## Keyboard Shortcuts

### File Operations

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Session |
| Ctrl+O | Open File |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+I | Import Session |
| Ctrl+E | Export Session |
| Ctrl+Q | Exit |

### Session Operations

| Shortcut | Action |
|----------|--------|
| F2 | Rename Session |
| Delete | Delete Session |
| Ctrl+D | Duplicate Session |
| Ctrl+T | Add File to Session |

### Edit Operations

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+X | Cut |
| Ctrl+C | Copy |
| Ctrl+V | Paste |
| Ctrl+A | Select All |
| Ctrl+F | Find |
| Ctrl+H | Find/Replace |

### View Operations

| Shortcut | Action |
|----------|--------|
| Ctrl+, | Settings |
| Ctrl+Shift+F | Advanced Search |
| Ctrl+Shift+U | Sync Now |
| F11 | Toggle Fullscreen |

### Navigation

| Shortcut | Action |
|----------|--------|
| Ctrl+Tab | Next Tab |
| Ctrl+Shift+Tab | Previous Tab |
| Ctrl+W | Close Tab |
| Ctrl+Shift+T | Reopen Closed Tab |
| Home/End | Go to Line Start/End |

### Quick Actions

| Shortcut | Action |
|----------|--------|
| Ctrl+1 through Ctrl+9 | Switch to Tab 1-9 |
| Alt+S | Show/Hide Session Panel |
| Alt+E | Focus Editor |

---

## Troubleshooting

### Common Issues

**Application Won't Start**
- Check that .NET Framework 4.8+ is installed
- Try running as administrator
- Check log file: `%APPDATA%\CharmCrush\logs\app.log`

**Can't Connect to Cloud**
- Verify credentials are correct
- Check internet connection
- Try disconnecting and reconnecting

**Slow Performance**
- Reduce recent sessions limit
- Disable auto-sync
- Close unused tabs
- Clear search history

**Forgotten Password**
- Password cannot be recovered
- Contact support for account recovery
- Data is encrypted and cannot be accessed without password

### Log Files

Location: `%APPDATA%\CharmCrush\logs\`
- `app.log` - Main application log
- `sync.log` - Cloud sync log
- `error.log` - Error details

### Reset Settings

To reset all settings to defaults:
1. Close Charm Crush
2. Delete: `%APPDATA%\CharmCrush\settings.json`
3. Restart application

---

## FAQ

### Q: Is my data secure?

Yes. All data is encrypted using AES-128 encryption before storage. Passwords are hashed using PBKDF2-HMAC-SHA256.

### Q: Can I use Charm Crush offline?

Yes. All features work offline except cloud sync and share link creation.

### Q: How many sessions can I create?

Unlimited. Performance may degrade with very large numbers (10,000+ sessions).

### Q: Can I import sessions from other users?

Only if they share a session with you. Import is not possible from exported files created by other users.

### Q: Does Charm Crush work with version control?

Not directly. You can export sessions to JSON files and commit those to Git.

### Q: Can I create custom themes?

Not yet. Future versions will support custom CSS themes.

### Q: Is there a mobile app?

Not currently. Mobile apps are planned for future releases.

### Q: How do I report bugs?

Email bugs@charmcrush.app or use the Issue Tracker on our website.

### Q: Can I contribute to Charm Crush?

Yes! Visit our GitHub repository to contribute.

---

## Support

- **Email**: support@charmcrush.app
- **Website**: https://charmcrush.app
- **GitHub**: https://github.com/charm-crush
- **Documentation**: https://docs.charmcrush.app

---

*Charm Crush Session Manager v2.0*
*© 2024 Charm Crush. All rights reserved.*
