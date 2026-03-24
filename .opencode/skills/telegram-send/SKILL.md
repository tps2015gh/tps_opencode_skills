---
name: telegram-send
description: Send text messages and MP3 audio to Telegram chat using Bot API.
---

## Telegram Send Skill

Send text messages and audio files to any Telegram chat via Bot API.

## Prerequisites

- `TELEGRAM_BOT_TOKEN` set in `.env` file at project root

## Usage

### Send Text

```bash
python .opencode/skills/telegram-send/send.py text <chat_id> <text> [reply_to_message_id]
```

### Send Audio (MP3)

```bash
python .opencode/skills/telegram-send/send.py audio <chat_id> <file.mp3> [caption] [reply_to_message_id]
```

## Parameters

### Text Mode

| Parameter | Required | Description |
|-----------|----------|-------------|
| chat_id | Yes | Telegram chat ID (from inbox.json) |
| text | Yes | Message text (no emojis) |
| reply_to_message_id | No | Original message ID to reply to |

### Audio Mode

| Parameter | Required | Description |
|-----------|----------|-------------|
| chat_id | Yes | Telegram chat ID |
| file.mp3 | Yes | Path to MP3 file |
| caption | No | Text caption for the audio |
| reply_to_message_id | No | Original message ID to reply to |

## Examples

```bash
# Send text reply
python .opencode/skills/telegram-send/send.py text 7815216214 "Hello!" 2272

# Send audio reply
python .opencode/skills/telegram-send/send.py audio 7815216214 output.mp3 "Here is your news" 2276
```

## Python Usage

```python
import sys
sys.path.insert(0, '.opencode/skills/telegram-send')
from send import send_message, send_audio

# Send text
result = send_message('7815216214', 'Hello!', '2272')

# Send audio
result = send_audio('7815216214', 'output.mp3', 'Your reply', '2276')
```

## Notes

- **No emojis** in text - causes encoding errors on Windows
- Token is loaded from `.env` file automatically
- Returns JSON with `ok: true` on success
