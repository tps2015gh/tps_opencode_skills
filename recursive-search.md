# Recursive File Search Skill

## Purpose
Recursively search through all folders and files in a directory with keyword matching.

## Usage
```
/search [keyword] [mode]
```

## Parameters
- **keyword**: Search term (case-insensitive)
- **mode**: `stop` (default) - stops at first match, or `all` - shows all matches

## Behavior
1. Recursively traverses all subdirectories starting from the current working directory
2. Searches file names and contents for the keyword (case-insensitive)
3. Shows real-time progress: "Searching... [count] files scanned"
4. **Mode `stop`**: Returns first match and stops
5. **Mode `all`**: Continues and returns all matches

## Output
Returns a list of matching files with:
- Full file path
- Line number (if content match)
- Matching line preview

## Example
```
/search function stop
/search import all
```

## Progress Updates
During search, the agent will display progress messages:
- "Searching... [X] files scanned"
- Updates every 50 files or 2 seconds

## Notes
- Search is case-insensitive
- Scans both file names and file contents
- Skips binary files and common ignore patterns (.git, node_modules, etc.)
