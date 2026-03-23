# Recursive File Search - Agent Implementation

## IDENTIFIER
`/search`

## EXECUTION PATTERN

### Input Handling
1. Parse command: `/search [keyword] [mode]`
2. Default mode to `stop` if not specified
3. Validate mode is either `stop` or `all`

### Search Implementation

```javascript
// Recursive search with progress tracking
async function recursiveSearch(keyword, mode = 'stop', currentPath = process.cwd()) {
  const results = [];
  let filesScanned = 0;
  const keywordLower = keyword.toLowerCase();
  
  async function scanDir(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    
    for (const entry of entries) {
      // Skip common ignore patterns
      if (['.git', 'node_modules', '.cache', '__pycache__'].includes(entry.name)) {
        continue;
      }
      
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await scanDir(fullPath);
      } else if (entry.isFile()) {
        filesScanned++;
        
        // Progress update every 50 files
        if (filesScanned % 50 === 0) {
          console.log(`[PROGRESS] Searching... ${filesScanned} files scanned`);
        }
        
        const fileNameLower = entry.name.toLowerCase();
        
        // Check filename match
        if (fileNameLower.includes(keywordLower)) {
          results.push({ path: fullPath, type: 'filename', line: null, preview: entry.name });
          
          if (mode === 'stop') {
            return results;
          }
        }
        
        // Check file content
        try {
          const content = fs.readFileSync(fullPath, 'utf-8');
          const lines = content.split('\n');
          
          for (let i = 0; i < lines.length; i++) {
            if (lines[i].toLowerCase().includes(keywordLower)) {
              results.push({
                path: fullPath,
                type: 'content',
                line: i + 1,
                preview: lines[i].trim().substring(0, 100)
              });
              
              if (mode === 'stop') {
                return results;
              }
            }
          }
        } catch {
          // Skip binary/unreadable files
        }
      }
    }
  }
  
  await scanDir(currentPath);
  
  return { results, filesScanned };
}
```

### Output Format

**Progress during search:**
```
[PROGRESS] Searching... 50 files scanned
[PROGRESS] Searching... 100 files scanned
...
```

**Final results:**
```
=== Search Complete ===
Keyword: [keyword]
Mode: [mode]
Files scanned: [count]
Matches found: [count]

[MODE STOP - First Match]
/path/to/file.ext (line 5)
  Preview: ...matching content...

[MODE ALL - All Matches]
/path/to/file1.ext (filename match)
  file.ext

/path/to/file2.ext (line 10)
  Preview: ...matching content...
```

## MODES

### Mode: `stop` (Default)
- Stops immediately when first match is found
- Returns only the first match
- Fastest for finding any single match

### Mode: `all`
- Scans all files completely
- Returns all matches found
- Use when you need to find every occurrence

## ERROR HANDLING
- Skip directories/files without read permissions
- Skip binary files gracefully
- Handle circular symlinks
- Report search statistics even on partial completion

## PERFORMANCE
- Skip `.git`, `node_modules`, and other common non-relevant directories
- Progress updates every 50 files or 2 seconds
- Case-insensitive matching is optimized
