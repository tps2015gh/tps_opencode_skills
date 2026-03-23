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
OpenCode reads inbox → reply → send to Telegram → mark processed
```

## Steps

1. Read `bridge_data/inbox.json`
2. Find messages where `"_ai": true` and `"processed": false`
3. Reply to message naturally
4. Send reply to Telegram:
   ```python
   import urllib.request, urllib.parse, os
   token = os.getenv('TELEGRAM_BOT_TOKEN')
   url = f"https://api.telegram.org/bot{token}/sendMessage"
   data = urllib.parse.urlencode({
       'chat_id': CHAT_ID, 
       'text': 'Your AI reply here', 
       'reply_to_message_id': MSG_ID
   }).encode()
   urllib.request.urlopen(url, data=data)
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
- Reply to each
- Send to Telegram
- Clean up inbox

## Notes

- **ALL messages go to AI** (no auto-reply)
- queue_processor only marks messages as queued
- You send actual replies from OpenCode
- Always cleanup inbox after replying
