#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const MODE_VALUES = ['stop', 'all'];

let searchPath = process.cwd();
let keyword = '';
let mode = 'stop';

if (args.length === 0) {
  console.error('Usage: node search.js <path> <keyword> [mode]');
  console.error('  path:   Directory to search (default: current dir)');
  console.error('  keyword: String to search for (case-insensitive)');
  console.error('  mode:   "stop" (default) or "all"');
  process.exit(1);
}

if (args.length === 1) {
  keyword = args[0];
} else if (args.length === 2) {
  searchPath = path.resolve(args[0]);
  keyword = args[1];
} else {
  searchPath = path.resolve(args[0]);
  keyword = args[1];
  if (MODE_VALUES.includes(args[2])) {
    mode = args[2];
  }
}

if (!keyword) {
  console.error('Error: keyword is required');
  process.exit(1);
}

const IGNORE_DIRS = ['.git', 'node_modules', '.cache', '__pycache__', '.next', 'dist', 'build', '.svn', 'vendor'];
const KEYWORD = keyword.toLowerCase();
const results = [];
let filesScanned = 0;
let matchesFound = 0;
let lastProgressUpdate = Date.now();
let stopRequested = false;

const MAX_RESULTS = mode === 'all' ? 10000 : 1;
const MAX_FILE_SIZE = 5 * 1024 * 1024;

function logProgress() {
  const now = Date.now();
  if (now - lastProgressUpdate >= 2000 || filesScanned % 100 === 0) {
    process.stdout.write(`\r[PROGRESS] ${filesScanned} files scanned | ${matchesFound} matches`);
    lastProgressUpdate = now;
  }
}

function searchDirectory(dir) {
  if (stopRequested) return true;

  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return false;
  }

  for (const entry of entries) {
    if (stopRequested) return true;

    if (IGNORE_DIRS.includes(entry.name)) continue;

    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      if (searchDirectory(fullPath) && mode === 'stop') return true;
    } else if (entry.isFile()) {
      filesScanned++;
      logProgress();

      const fileNameLower = entry.name.toLowerCase();
      
      if (fileNameLower.includes(KEYWORD)) {
        matchesFound++;
        results.push({ path: fullPath, type: 'filename', line: null, preview: entry.name });
        console.log(`\n  [MATCH] ${fullPath} (filename)`);
        if (mode === 'stop') { stopRequested = true; return true; }
        if (matchesFound >= MAX_RESULTS) { console.log('\n  [LIMIT] Max results reached'); return true; }
      }

      let stats;
      try {
        stats = fs.statSync(fullPath);
      } catch {
        continue;
      }

      if (stats.size > MAX_FILE_SIZE) continue;

      try {
        const content = fs.readFileSync(fullPath, 'utf-8');
        const lines = content.split('\n');

        for (let i = 0; i < lines.length; i++) {
          if (stopRequested) return true;
          if (lines[i].toLowerCase().includes(KEYWORD)) {
            matchesFound++;
            const preview = lines[i].trim().substring(0, 150);
            results.push({ path: fullPath, type: 'content', line: i + 1, preview });
            console.log(`\n  [MATCH] ${fullPath} (line ${i + 1})`);
            console.log(`         ${preview}`);
            if (mode === 'stop') { stopRequested = true; return true; }
            if (matchesFound >= MAX_RESULTS) { console.log('\n  [LIMIT] Max results reached'); return true; }
          }
        }
      } catch {
        // Skip binary/unreadable files
      }
    }
  }
  return false;
}

console.log(`\n=== Recursive Search ===`);
console.log(`Keyword: "${keyword}" | Mode: ${mode}`);
console.log(`Path: ${searchPath}`);
console.log(`Max results: ${MAX_RESULTS}\n`);

searchDirectory(searchPath);

console.log(`\n\n=== Search Complete ===`);
console.log(`Files scanned: ${filesScanned}`);
console.log(`Matches found: ${matchesFound}`);

if (results.length > 0 && results.length <= 50) {
  console.log('\n--- All Results ---');
  results.forEach((r, i) => {
    console.log(`${i + 1}. ${r.path}${r.line ? ` (line ${r.line})` : ' (filename)'}`);
    if (r.preview) console.log(`   ${r.preview}`);
  });
}
