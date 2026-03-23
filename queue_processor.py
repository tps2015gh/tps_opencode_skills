#!/usr/bin/env python3
"""
Telegram Queue Processor
Real file monitoring - processes inbox immediately on change
No external dependencies needed
"""

import os
import sys
import json
import time
import subprocess
import threading

BRIDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge_data')
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
OUTBOX_FILE = os.path.join(BRIDGE_DIR, 'outbox.json')
LAST_RESPONSE_FILE = os.path.join(BRIDGE_DIR, 'last_response.txt')

os.makedirs(BRIDGE_DIR, exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

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
    
    if text_lower.startswith('git '):
        cmd = text_lower[4:]
        if 'status' in cmd:
            return f"```\n{run_command('git status')}\n```"
        if 'log' in cmd:
            return f"```\n{run_command('git log --oneline -5')}\n```"
        if 'branch' in cmd:
            return f"```\n{run_command('git branch -a')}\n```"
        return f"```\n{run_command('git ' + cmd)}\n```"
    
    if text_lower.startswith('cmd '):
        return f"```\n{run_command(text_lower[4:])}\n```"
    
    return None

def process_inbox():
    try:
        if not os.path.exists(INBOX_FILE):
            return 0, 0
        
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
        pending = 0
        
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
                    log(f"AUTO: {text[:40]}...")
                else:
                    pending += 1
        
        with open(INBOX_FILE, 'w', encoding='utf-8') as f:
            json.dump(inbox, f, ensure_ascii=False, indent=2)
        
        with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
            json.dump(outbox, f, ensure_ascii=False, indent=2)
        
        return processed, pending
        
    except Exception as e:
        log(f"ERROR: {e}")
        return 0, 0

class FileMonitor:
    def __init__(self):
        self.last_inbox_mtime = 0
        self.last_inbox_size = 0
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        
    def start(self):
        log("START: Starting file monitor")
        # Initial state
        if os.path.exists(INBOX_FILE):
            stat = os.stat(INBOX_FILE)
            self.last_inbox_mtime = stat.st_mtime
            self.last_inbox_size = stat.st_size
        
        self.thread.start()
        log("START: Monitor thread running")
        
    def _monitor(self):
        log("MONITOR: Watching for file changes...")
        while self.running:
            try:
                if os.path.exists(INBOX_FILE):
                    stat = os.stat(INBOX_FILE)
                    
                    # Check for changes
                    if stat.st_mtime != self.last_inbox_mtime or stat.st_size != self.last_inbox_size:
                        log(f"CHANGE: Inbox modified!")
                        self.last_inbox_mtime = stat.st_mtime
                        self.last_inbox_size = stat.st_size
                        
                        # Wait a bit for file to finish writing
                        time.sleep(0.3)
                        
                        # Process
                        processed, pending = process_inbox()
                        if processed > 0:
                            log(f"DONE: Processed {processed} messages")
                        if pending > 0:
                            log(f"WAIT: {pending} need OpenCode AI")
            except Exception as e:
                log(f"ERROR: {e}")
            
            time.sleep(0.5)  # Check every 0.5 seconds
            
        log("MONITOR: Stopped")
    
    def stop(self):
        self.running = False
        self.thread.join(timeout=2)

def main():
    log("=" * 50)
    log("  Telegram Queue Processor - FILE MONITOR")
    log("=" * 50)
    log(f"")
    log(f"Bridge Dir: {BRIDGE_DIR}")
    log(f"Inbox: {INBOX_FILE}")
    log(f"")
    log("START: Initializing...")
    
    monitor = FileMonitor()
    monitor.start()
    
    log("READY: Watching for messages...")
    log("Press Ctrl+C to stop")
    log("")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("")
        log("STOP: Shutting down...")
        monitor.stop()
        log("STOP: Done!")

if __name__ == "__main__":
    main()
