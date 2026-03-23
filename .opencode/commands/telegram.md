---
description: Check Telegram inbox and reply to messages
---

## Command: /telegram

Read pending messages from Telegram bridge and reply.

## Setup (PowerShell)

```powershell
# Set token (current session)
$env:TELEGRAM_BOT_TOKEN="your_token_here"

# Install dependency
pip install python-telegram-bot

# Start bridge (keep running)
python telegram_bridge.py
```

## How to Use

1. Start bridge server: `python telegram_bridge.py`
2. Send message from Telegram
3. Bot shows: "Waiting for OpenCode Agent..."
4. Run `/telegram` in OpenCode
5. I read inbox.json, write reply to outbox.json
6. Bot sends reply to Telegram (auto-check every 2 seconds)

## Steps

1. Read `bridge_data/inbox.json`
2. Find messages where `"processed": false`
3. Reply to each message naturally
4. Write reply to `bridge_data/outbox.json`:
   ```json
   {
     "chat_id": <number>,
     "reply_to_message_id": <number>,
     "text": "Your reply here",
     "sent": false
   }
   ```
5. Mark message as `"processed": true` in inbox

## Response

- **No pending**: "No pending Telegram messages"
- **Pending messages**: Show count, reply to each, write to outbox, mark as processed
