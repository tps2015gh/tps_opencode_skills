---
name: telegram-send
description: Send text messages, MP3 audio, and documents to Telegram chat using Bot API.
---

## Telegram Send Skill

Send text messages, audio files, and documents to any Telegram chat via Bot API.

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

### Send Document (PDF, DOC, XLS, ZIP)

```bash
python .opencode/skills/telegram-send/send.py document <chat_id> <file.pdf> [caption] [reply_to_message_id]
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

### Document Mode

| Parameter | Required | Description |
|-----------|----------|-------------|
| chat_id | Yes | Telegram chat ID |
| file.pdf | Yes | Path to document file |
| caption | No | Text caption for the document |
| reply_to_message_id | No | Original message ID to reply to |

Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT, ZIP

## Examples

```bash
# Send text reply
python .opencode/skills/telegram-send/send.py text 7815216214 "Hello!" 2272

# Send audio reply
python .opencode/skills/telegram-send/send.py audio 7815216214 output.mp3 "Here is your news" 2276

# Send PDF document
python .opencode/skills/telegram-send/send.py document 7815216214 report.pdf "Monthly report" 2280
```

## Python Usage

```python
import sys
sys.path.insert(0, '.opencode/skills/telegram-send')
from send import send_message, send_audio, send_document

# Send text
result = send_message('7815216214', 'Hello!', '2272')

# Send audio
result = send_audio('7815216214', 'output.mp3', 'Your reply', '2276')

# Send PDF
result = send_document('7815216214', 'report.pdf', 'Monthly report', '2280')
```

## Notes

- **No emojis** in text - causes encoding errors on Windows
- Token is loaded from `.env` file automatically
- Returns JSON with `ok: true` on success
- Document upload timeout is 60 seconds (larger files)
