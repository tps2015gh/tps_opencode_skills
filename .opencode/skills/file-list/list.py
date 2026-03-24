#!/usr/bin/env python3
"""File List - List files in a directory"""

import os
import sys
import json
import time


def list_files(path='.', pattern=None, show_size=True):
    results = []
    try:
        for f in os.listdir(path):
            full = os.path.join(path, f)
            if pattern and not f.endswith(pattern):
                continue
            size = os.path.getsize(full) if os.path.isfile(full) else 0
            mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(full)))
            kind = 'file' if os.path.isfile(full) else 'dir'
            results.append({'name': f, 'size': size, 'modified': mtime, 'type': kind})
    except Exception as e:
        return {'error': str(e)}
    return results


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    pattern = sys.argv[2] if len(sys.argv) > 2 else None

    files = list_files(path, pattern)

    if isinstance(files, dict) and 'error' in files:
        print(f"Error: {files['error']}")
        sys.exit(1)

    if not files:
        print(f"No files in {path}")
    else:
        print(f"Files in {path}:\n")
        for f in sorted(files, key=lambda x: x['modified'], reverse=True):
            size = f'{f["size"]:,} bytes' if f['type'] == 'file' else '[DIR]'
            print(f"  {f['modified']}  {size:>15}  {f['name']}")
        print(f"\nTotal: {len(files)} items")
