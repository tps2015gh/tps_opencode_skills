---
name: queue-check
description: Check pending messages in inbox.json queue. Report when queue has messages.
---

## Queue Check Skill

Monitor the Telegram message queue (inbox.json) and report pending messages.

## Usage

### One-time check

```bash
python .opencode/skills/queue-check/check.py
```

### Watch mode (loop)

```bash
python .opencode/skills/queue-check/check.py watch [interval_seconds]
```

Default interval: 5 seconds

## Output

```
Que: 3
  1. [2026-03-24T07:35] @p400: read news
  2. [2026-03-24T07:44] @p400: get traffic news
  3. [2026-03-24T07:46] @p400: hello
```

## Python Usage

```python
import sys
sys.path.insert(0, '.opencode/skills/queue-check')
from check import check_once, get_pending

# One-time check
result = check_once()
if result:
    print(result['summary'])  # Human-readable summary
    print(result['count'])    # Number count
    print(result['messages']) # Raw message list

# Just get pending list
msgs = get_pending()
```

## Notes

- Reads `bridge_data/inbox.json`
- Only shows messages with `_ai: true` and `processed: false`
- Returns None if queue is empty
