---
name: queue-notify
description: Lightweight mailbox agent. Checks queue every 30 seconds, sends Telegram notification when messages arrive.
---

## Queue Notify Agent

Background agent that checks inbox.json every 30 seconds. When messages arrive, sends a Telegram notification like "Mailbox: 3 messages waiting". Low token usage.

## Usage

```bash
python .opencode/skills/queue-notify/notify.py [interval] [--debug]
```

| Arg | Default | Description |
|-----|---------|-------------|
| interval | 30 | Check interval in seconds |
| --debug | off | Send heartbeat every check |

## Examples

```bash
# Normal mode - only notify when messages arrive
python .opencode/skills/queue-notify/notify.py 30

# Debug mode - send status every 30s
python .opencode/skills/queue-notify/notify.py 30 --debug

# Background (PowerShell)
Start-Process python -ArgumentList '".opencode/skills/queue-notify/notify.py"', '30', '--debug' -WindowStyle Hidden
```

## How It Works

```
Normal:  Every 30s -> count > 0? -> "Mailbox: X messages" to Telegram
Debug:   Every 30s -> "Queue check at [time]: X pending" to Telegram
```

## Flow

```
notify.py (30s loop)  -->  "Mailbox: 3 messages"  -->  Telegram
                                                       you see it
                                                       run /telegram
```

## Notes

- Uses telegram-send skill to send notifications
- Status saved to `bridge_data/queue_status.json`
- Only notifies on count change in normal mode (no spam)
- Debug mode sends every check - good for testing
