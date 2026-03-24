---
name: file-list
description: List files in a directory. Shows filename, size, and modified date.
---

## File List Skill

List files in any directory.

## Usage

```bash
# List current directory
python .opencode/skills/file-list/list.py

# List specific path
python .opencode/skills/file-list/list.py <path>

# List only .mp3 files
python .opencode/skills/file-list/list.py . .mp3

# List bridge_data
python .opencode/skills/file-list/list.py bridge_data
```

## Output

```
Files in .:

  2026-03-24 09:58       10,512 bytes  test_tts_input.mp3
  2026-03-24 08:30       12,816 bytes  output.mp3
  2026-03-24 07:15  [DIR]              bridge_data

Total: 3 items
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| path | No | Directory to list (default: current) |
| pattern | No | File extension filter (e.g. `.mp3`) |

## Notes

- Sorted by modified date (newest first)
- Shows file size and modification time
- Pattern filter by extension
