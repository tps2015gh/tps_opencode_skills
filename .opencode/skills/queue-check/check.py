#!/usr/bin/env python3
"""Queue Check - Monitor inbox.json and report pending messages"""

import os
import sys
import json
import time


INBOX_FILE = os.path.join('bridge_data', 'inbox.json')


def get_pending():
    try:
        if not os.path.exists(INBOX_FILE):
            return []
        with open(INBOX_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            inbox = json.loads(content) if content else []
        return [m for m in inbox if m.get('_ai') and not m.get('processed')]
    except:
        return []


def check_once():
    pending = get_pending()
    if not pending:
        return None

    lines = []
    for i, msg in enumerate(pending, 1):
        ts = msg.get('timestamp', '?')[:16]
        user = msg.get('username', '?')
        text = msg.get('text', '?')[:80]
        lines.append(f"  {i}. [{ts}] @{user}: {text}")

    return {
        'count': len(pending),
        'messages': pending,
        'summary': f"Que: {len(pending)}\n" + "\n".join(lines)
    }


def watch(interval=5):
    print(f"Watching {INBOX_FILE} every {interval}s (Ctrl+C to stop)")
    last_count = -1

    while True:
        try:
            pending = get_pending()
            count = len(pending)

            if count > 0 and count != last_count:
                print(f"\nQue: {count}")
                for i, msg in enumerate(pending, 1):
                    ts = msg.get('timestamp', '?')[:16]
                    user = msg.get('username', '?')
                    text = msg.get('text', '?')[:80]
                    print(f"  {i}. [{ts}] @{user}: {text}")
                last_count = count
            elif count == 0 and last_count != 0:
                print("Que: 0 (empty)")
                last_count = 0

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped")
            break


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'watch':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        watch(interval)
    else:
        result = check_once()
        if result:
            print(result['summary'])
        else:
            print("Que: 0 (empty)")
