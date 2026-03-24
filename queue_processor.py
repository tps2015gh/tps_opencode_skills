#!/usr/bin/env python3
"""Telegram Queue Processor - Marks messages for OpenCode to process"""

import os
import json
import time

VERSION = "7.0"
BRIDGE_DIR = 'bridge_data'
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')

os.makedirs(BRIDGE_DIR, exist_ok=True)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_json(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []


def write_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


def main():
    log(f"Queue Processor v{VERSION} - Marks messages for OpenCode")
    log(f"Watching: {INBOX_FILE}")

    while True:
        try:
            inbox = read_json(INBOX_FILE)

            # Find messages not yet marked for AI
            new_msgs = [m for m in inbox if not m.get('_ai') and not m.get('processed')]

            if new_msgs:
                for msg in new_msgs:
                    msg['_ai'] = True
                    log(f"Marked for AI: {msg.get('text', '')[:50]}")
                write_json(INBOX_FILE, inbox)

            time.sleep(2)

        except KeyboardInterrupt:
            log("\nStop!")
            break
        except Exception as e:
            log(f"ERR: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
