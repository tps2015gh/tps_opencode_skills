# OpenCode Skills Collection

A collection of AI-powered skills and tools for OpenCode AI Agent.

## Team

| Role | Name | Description |
|------|------|-------------|
| Director Supervisor | @p400 | Project owner, strategy, and direction |
| Lead Developer & Tech Lead | **Big Pickle** (OpenCode Zen AI) | Architecture, development, and technical decisions |
| Human Debugger & Deadlock Consultant | @p400 | Real-world testing, deadlock detection, semaphore suggestions |

## Project Opinion

This project represents a powerful bridge between Telegram and OpenCode AI Agent, enabling remote collaboration through natural language. The combination of real-time messaging with AI processing creates a seamless workflow where developers can manage their projects from anywhere using just their phone.

**Key Strengths:**
- Fully autonomous message processing
- No external AI API dependencies for basic commands
- Secure token management via environment variables
- Extensible architecture for new skills

**Future Vision:**
- Multi-platform support (Discord, Slack, Line)
- Voice commands and audio responses
- Automated task scheduling and notifications
- Integration with more AI models

## Features & Functions

### 1. Telegram Bridge (`telegram_bridge.py`)
**Function:** Connects Telegram chatroom to OpenCode Agent

**Features:**
- Auto-respond to simple messages (hello, ok, time, date)
- Git commands via chat (status, log, branch, diff)
- Command execution via `cmd <command>`
- TTS audio generation for responses
- Real-time message polling

**Auto-Commands:**
```
hello, hi       → Greeting response
ok, thanks      → Simple acknowledgment
time            → Current time
date            → Today's date
git status      → Git status
git log         → Recent commits
git branch      → Branch list
cmd <command>    → Execute command
```

### 2. Thai TTS (`thai_tts.py`)
**Function:** Convert Thai text to speech using Edge TTS

**Features:**
- Natural Thai voices (PremwadeeNeural, NiwatNeural)
- Speed control (+0% to +20%)
- Volume adjustment
- File or direct text input
- MP3 output

**Usage:**
```bash
python thai_tts.py "สวัสดีครับ" female +0% +0%
```

### 3. Recursive Search (`search.js`)
**Function:** Recursive file search with progress tracking

**Features:**
- Case-insensitive search
- Two modes: `stop` (first match) or `all` (all matches)
- Real-time progress updates
- Skip binary files and common directories

**Usage:**
```bash
node search.js <path> <keyword> [stop|all]
```

### 4. Audio Player (`play_audio.py`)
**Function:** Play audio files from command line

**Features:**
- MP3, WAV, OGG support
- Cross-platform (Windows/Mac/Linux)
- Simple command interface

## OpenCode Commands

| Command | Function |
|---------|----------|
| `/telegram` | Check and reply to Telegram messages |
| `/search` | Recursive file search |
| `/tts` | Convert text to Thai speech |
| `/play` | Play audio file |

## Installation

```bash
# Set Telegram token
$env:TELEGRAM_BOT_TOKEN="your_token_here"

# Install dependencies
pip install python-telegram-bot edge-tts pygame

# Start bridge
python telegram_bridge.py
```

## License

MIT License with commercial clause for 60,000+ users.

---

*Built with OpenCode AI Agent and Big Pickle (Lead Developer)*
