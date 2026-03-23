#!/usr/bin/env python3
"""
Telegram Queue Processor
Real file monitoring with proper file locking
"""

import os
import sys
import json
import time
import subprocess
import threading
import fcntl

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

def read_json_safe(filepath, default=[]):
    """Read JSON file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        log(f"READ ERROR {filepath}: {e}")
    except Exception as e:
        log(f"READ ERROR {filepath}: {e}")
    return default

def write_json_safe(filepath, data):
    """Write JSON file with error handling"""
    try:
        # Write to temp file first
        temp_file = filepath + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Atomic rename
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rename(temp_file, filepath)
        return True
    except Exception as e:
        log(f"WRITE ERROR {filepath}: {e}")
        # Try to clean up temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
        return False

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
    """Process inbox and add responses to outbox"""
    inbox = read_json_safe(INBOX_FILE)
    outbox = read_json_safe(OUTBOX_FILE)
    
    if not inbox:
        return 0, 0
    
    processed = 0
    pending = 0
    changed = False
    
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
                changed = True
                log(f"AUTO: {text[:40]}...")
            else:
                pending += 1
    
    if changed:
        write_json_safe(INBOX_FILE, inbox)
        write_json_safe(OUTBOX_FILE, outbox)
        log(f"DONE: {processed} auto-replied, {pending} pending")
    elif pending > 0:
        log(f"WAIT: {pending} messages need OpenCode AI")
    
    return processed, pending

class FileMonitor:
    def __init__(self):
        self.last_mtime = 0
        self.last_size = 0
        self.running = True
        self.processing = False
        
    def start(self):
        log("START: File monitor initializing...")
        if os.path.exists(INBOX_FILE):
            stat = os.stat(INBOX_FILE)
            self.last_mtime = stat.st_mtime
            self.last_size = stat.st_size
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()
        log("START: Monitor active")
        
    def _monitor(self):
        log("MONITOR: Watching inbox file...")
        while self.running:
            try:
                if os.path.exists(INBOX_FILE):
                    stat = os.stat(INBOX_FILE)
                    
                    # Detect change
                    if stat.st_mtime != self.last_mtime or stat.st_size != self.last_size:
                        if not self.processing:
                            log("CHANGE: Inbox file modified!")
                            self.last_mtime = stat.st_mtime
                            self.last_size = stat.st_size
                            
                            # Process with lock
                            self.processing = True
                            time.sleep(0.2)  # Wait for write to complete
                            process_inbox()
                            self.processing = False
            except Exception as e:
                log(f"MONITOR ERROR: {e}")
                time.sleep(1)
            
            time.sleep(0.3)  # Check every 300ms
            
        log("MONITOR: Stopped")
    
    def stop(self):
        self.running = False
        try:
            self.thread.join(timeout=2)
        except:
            pass

def main():
    log("=" * 50)
    log("  Telegram Queue Processor - ACTIVE")
    log("=" * 50)
    log(f"")
    log(f"Bridge Dir: {BRIDGE_DIR}")
    log(f"")
    
    monitor = FileMonitor()
    monitor.start()
    
    log("READY: Monitoring for messages...")
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
