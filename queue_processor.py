#!/usr/bin/env python3
"""
Telegram Queue Processor
Real file monitoring with watchdog - processes inbox immediately on change
"""

import os
import sys
import json
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BRIDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge_data')
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
OUTBOX_FILE = os.path.join(BRIDGE_DIR, 'outbox.json')
LAST_RESPONSE_FILE = os.path.join(BRIDGE_DIR, 'last_response.txt')

os.makedirs(BRIDGE_DIR, exist_ok=True)

def log(msg):
    try:
        print(msg)
    except:
        print(str(msg))

def save_last_response(text: str):
    try:
        with open(LAST_RESPONSE_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        pass

def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30,
                             cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.stdout.strip() or result.stderr.strip() or "Done!"
    except Exception as e:
        return f"Error: {e}"

def get_auto_response(text: str) -> str:
    text_lower = text.lower().strip()
    
    if text_lower in ['ok', 'okay', 'ครับ', 'ขอบคุณ', 'thanks', 'thank you']:
        return "OK!"
    
    if 'time' in text_lower or 'เวลา' in text_lower or 'กี่โมง' in text_lower:
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%H:%M')} ICT"
    
    if 'date' in text_lower or 'วันที่' in text_lower or 'today' in text_lower:
        from datetime import datetime
        return f"Today: {datetime.now().strftime('%d/%m/%Y')}"
    
    if 'status' in text_lower or 'สถานะ' in text_lower:
        return "System is running normally."
    
    if 'hello' in text_lower or 'hi' in text_lower or 'สวัสดี' in text_lower:
        return "Hello! I'm here. What can I help you with?"
    
    if 'help' in text_lower or 'ช่วย' in text_lower:
        return "Commands:\n/ai <message> - Forward to AI\n/git status - Git status"
    
    if text_lower.startswith('git '):
        cmd = text_lower[4:]
        if 'status' in cmd:
            return f"```\n{run_command('git status')}\n```"
        if 'log' in cmd:
            return f"```\n{run_command('git log --oneline -5')}\n```"
        if 'branch' in cmd:
            return f"```\n{run_command('git branch -a')}\n```"
        if 'diff' in cmd:
            return f"```\n{run_command('git diff')}\n```"
        return f"```\n{run_command('git ' + cmd)}\n```"
    
    if text_lower.startswith('cmd '):
        cmd = text_lower[4:]
        return f"```\n{run_command(cmd)}\n```"
    
    return None

class InboxFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0
        self.processing = False
        
    def on_modified(self, event):
        if event.src_path.endswith('inbox.json') and not self.processing:
            # Debounce - wait 0.5 seconds for file to settle
            time.sleep(0.5)
            self.process_inbox()
    
    def on_created(self, event):
        if event.src_path.endswith('inbox.json'):
            log(f"[WATCH] New inbox file detected")
            self.process_inbox()
    
    def process_inbox(self):
        self.processing = True
        try:
            if not os.path.exists(INBOX_FILE):
                return
            
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                inbox = json.loads(content) if content else []
            
            outbox = []
            if os.path.exists(OUTBOX_FILE):
                try:
                    with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                        outbox = json.loads(f.read().strip() or "[]")
                except:
                    outbox = []
            
            processed = 0
            pending_for_ai = 0
            new_pending = 0
            
            for msg in inbox:
                if not msg.get('processed', False):
                    text = msg.get('text', '')
                    auto_reply = get_auto_response(text)
                    
                    if auto_reply:
                        outbox.append({
                            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                            'chat_id': msg['chat_id'],
                            'reply_to_message_id': msg['message_id'],
                            'text': auto_reply,
                            'sent': False
                        })
                        msg['processed'] = True
                        save_last_response(auto_reply)
                        processed += 1
                        log(f"[AUTO] Processed: {text[:30]}...")
                    else:
                        pending_for_ai += 1
            
            # Count new pending messages
            new_pending = len([m for m in inbox if not m.get('processed', False)])
            
            # Save files
            with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                json.dump(inbox, f, ensure_ascii=False, indent=2)
            
            with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
                json.dump(outbox, f, ensure_ascii=False, indent=2)
            
            if processed > 0:
                log(f"[OK] Auto-replied to {processed} messages")
            if new_pending > 0:
                log(f"[WAIT] {new_pending} messages need OpenCode AI")
                
        except Exception as e:
            log(f"[ERROR] {e}")
        finally:
            self.processing = False

def main():
    log("=" * 50)
    log("  Telegram Queue Processor - WATCH MODE")
    log("=" * 50)
    log(f"\nBridge Dir: {BRIDGE_DIR}")
    log(f"Inbox File: {INBOX_FILE}")
    log("\n[WATCH] Starting real file monitoring...")
    log("[INFO] Will process messages immediately on file change\n")
    
    # Create handler
    handler = InboxFileHandler()
    
    # Create observer
    observer = Observer()
    observer.schedule(handler, BRIDGE_DIR, recursive=False)
    observer.start()
    
    log(f"[WATCH] Monitoring: {BRIDGE_DIR}")
    log("[READY] Waiting for inbox changes...\n")
    
    try:
        # Initial check
        handler.process_inbox()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        log("\n\n[STOP] Stopping processor...")
        observer.stop()
        
    observer.join()
    log("[STOP] Done!")

if __name__ == "__main__":
    main()
