---
description: Process Telegram messages with AI
---

## Command: /telegram

Process Telegram messages with OpenCode AI.

## Flow

```
Telegram message → telegram_bridge → inbox.json
                                       ↓
                               queue_processor.py
                               (marks _ai: true)
                                       ↓
OpenCode reads inbox → reply → send via skill → clean inbox
```

## Steps

1. Read `bridge_data/inbox.json`
2. Find messages where `"_ai": true` and `"processed": false`
3. Reply to message naturally
4. Send reply to Telegram using skill:
   ```bash
   python .opencode/skills/telegram-send/send.py text <chat_id> "<reply>" <reply_to_message_id>
   ```
5. **Mark message as `"processed": true`** in inbox
6. **Remove processed messages from inbox**

## Example

```
/telegram
```

I will:
- Read inbox.json
- Find messages needing AI
- Reply to each using telegram-send skill
- Clean up inbox

## Notes

- **ALL messages go to AI** (no auto-reply)
- queue_processor only marks messages as queued
- You send actual replies from OpenCode via telegram-send skill
- Always cleanup inbox after replying
