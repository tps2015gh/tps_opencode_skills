---
description: Recursively search folders. Usage: /search <path> <keyword> [mode]
---

Recursively search through all folders and files.

**Arguments:**
- `$1` = path (optional, directory to search, default: current directory)
- `$2` = keyword (search term, case-insensitive)
- `$3` = mode (optional: "stop" (default) or "all")

**Examples:**
```
/search . function stop    # search current dir for "function"
/search .. test all         # search parent dir for "test"
/search ./src component      # search ./src for "component"
/search . import             # search current dir for "import"
```

**Mode options:**
- `stop` (default) - stops at first match found
- `all` - returns ALL matches

**Implementation:**
1. Use `glob` tool to recursively find all files
2. Use `grep` tool to search for keyword in file contents
3. Show progress: `[PROGRESS] Searching... [X] files scanned`
4. Skip directories: `.git`, `node_modules`, `.cache`, `__pycache__`, `.next`, `dist`, `build`

**For each match display:**
- File path
- Line number (if content match)
- Preview of matching line

**Output format:**
```
=== Search Complete ===
Path: [path]
Keyword: "[keyword]"
Mode: [mode]
Files scanned: [count]
Matches found: [count]

1. /path/to/file.ext (line X)
   Preview: ...matching text...
```
