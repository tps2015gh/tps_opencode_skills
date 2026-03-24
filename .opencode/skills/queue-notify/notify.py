#!/usr/bin/env python3
"""Queue Notify - Mailbox checker, notifies when queue has messages"""

import os
import sys
import json
import time
import subprocess

BRIDGE_DIR = 'bridge_data'
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
STATUS_FILE = os.path.join(BRIDGE_DIR, 'queue_status.json')
SEND_SCRIPT = os.path.join('.opencode', 'skills', 'telegram-send', 'send.py')
CHAT_ID = '7815216214'


def get_pending_count():
    try:
        if not os.path.exists(INBOX_FILE):
            return 0
        with open(INBOX_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            inbox = json.loads(content) if content else []
        return len([m for m in inbox if m.get('_ai') and not m.get('processed')])
    except:
        return 0


def send_tg(text):
    try:
        subprocess.run(
            ['python', SEND_SCRIPT, 'text', CHAT_ID, text],
            capture_output=True, timeout=15
        )
    except:
        pass


def save_status(count):
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'count': count, 'time': time.time()}, f)
    except:
        pass


def run(interval=30, debug=False):
    last_notified = 0
    last_debug = 0

    if debug:
        send_tg(f"Queue Notify started (debug mode, {interval}s)")

    print(f"Queue Notify - every {interval}s (debug={debug})")

    while True:
        try:
            now = time.time()
            count = get_pending_count()
            save_status(count)

            # Debug heartbeat
            if debug and (now - last_debug >= interval):
                t = time.strftime('%H:%M:%S')
                send_tg(f"Queue check at {t}: {count} pending")
                last_debug = now

            # Notify on new messages
            if count > 0 and count != last_notified:
                send_tg(f"Mailbox: {count} message{'s' if count > 1 else ''} waiting")
                last_notified = count
            elif count == 0:
                last_notified = 0

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)


if __name__ == '__main__':
    interval = 30
    debug = False

    for arg in sys.argv[1:]:
        if arg == '--debug':
            debug = True
        elif arg.isdigit():
            interval = int(arg)

    run(interval, debug)
