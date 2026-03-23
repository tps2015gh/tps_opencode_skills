---
name: telegram-bot
description: Connect Telegram to OpenCode Agent. Messages go to inbox.json, Agent processes and writes replies to outbox.json. No external AI needed.
---

## Telegram OpenCode Bridge

Connect Telegram chatroom to OpenCode Agent.

## Setup

### 1. Create Telegram Bot
1. Open Telegram, search for @BotFather
2. Send `/newbot`
3. Copy the bot token

### 2. Set Environment Variable

**PowerShell (current session):**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_token_here"
```

**PowerShell (permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "your_token_here", "User")
```

**CMD:**
```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
```

### 3. Install Dependencies
```bash
pip install python-telegram-bot
```

## How It Works

```
Telegram Message → inbox.json → You run /telegram → Agent reads → outbox.json → Bot sends reply
```

## Usage

### 1. Start Bridge (keep running)
```bash
python telegram_bridge.py
```

### 2. Send message in Telegram
Bot will reply: "Got your message! Waiting for OpenCode Agent..."

### 3. Run in OpenCode
```
/telegram
```

### 4. Bot sends your reply to Telegram

### Files
- `bridge_data/inbox.json` - Queue for incoming messages
- `bridge_data/outbox.json` - Queue for outgoing replies

### Commands (in Telegram)
- `/start` - Start
- `/status` - Check status
- `/pending` - View pending messages
- `/clear` - Clear data
- `/help` - Help

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `TELEGRAM_BRIDGE_DIR` | Bridge directory (default: ./bridge_data) | No |
