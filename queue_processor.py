#!/usr/bin/env python3
"""
Telegram Queue Processor
Continuously checks inbox and auto-responds or forwards to outbox
Run this separately from the bridge
"""

import os
import sys
import json
import time
import asyncio
import subprocess

# Set UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BRIDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge_data')
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
OUTBOX_FILE = os.path.join(BRIDGE_DIR, 'outbox.json')
LAST_RESPONSE_FILE = os.path.join(BRIDGE_DIR, 'last_response.txt')

# Create bridge dir if not exists
os.makedirs(BRIDGE_DIR, exist_ok=True)

def log(msg):
    """Safe print with Unicode handling"""
    try:
        print(msg)
    except:
        print(str(msg))

def save_last_response(text: str):
    """Save last response"""
    try:
        with open(LAST_RESPONSE_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        pass

def run_command(cmd: str) -> str:
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return result.stdout.strip() or result.stderr.strip() or "Done!"
    except Exception as e:
        return f"Error: {e}"

def get_auto_response(text: str) -> str:
    """Get auto response for simple queries"""
    text_lower = text.lower().strip()
    
    # Simple greetings
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
    
    # Git commands
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
    
    # System commands
    if text_lower.startswith('cmd '):
        cmd = text_lower[4:]
        return f"```\n{run_command(cmd)}\n```"
    
    return None

def process_inbox():
    """Process inbox and add responses to outbox"""
    if not os.path.exists(INBOX_FILE):
        return 0
    
    try:
        with open(INBOX_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                inbox = []
            else:
                inbox = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        inbox = []
    
    outbox = []
    if os.path.exists(OUTBOX_FILE):
        try:
            with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                outbox = json.loads(f.read().strip() or "[]")
        except:
            outbox = []
    
    processed = 0
    pending_for_ai = 0
    
    for msg in inbox:
        if not msg.get('processed', False):
            text = msg.get('text', '')
            
            # Get auto response
            auto_reply = get_auto_response(text)
            if auto_reply:
                # Simple query - auto respond
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
                log(f"[AUTO] Query processed")
            else:
                # Complex query - mark for OpenCode processing
                pending_for_ai += 1
                log(f"[PENDING] Complex query waiting for OpenCode AI")
    
    if pending_for_ai > 0:
        log(f"[WAIT] {pending_for_ai} messages need OpenCode AI processing")
    
    # Save files
    with open(INBOX_FILE, 'w', encoding='utf-8') as f:
        json.dump(inbox, f, ensure_ascii=False, indent=2)
    
    with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
        json.dump(outbox, f, ensure_ascii=False, indent=2)
    
    return processed

def main():
    log("=" * 50)
    log("  Telegram Queue Processor - ACTIVE")
    log("=" * 50)
    log(f"\nBridge Dir: {BRIDGE_DIR}")
    log("\n[START] Starting inbox processor...")
    log("[HEARTBEAT] Status updates every 5 seconds\n")
    
    last_count = -1
    heartbeat_counter = 0
    
    try:
        while True:
            heartbeat_counter += 1
            
            count = process_inbox()
            if count > 0:
                log(f"[OK] Processed {count} messages")
            
            # Check pending messages
            if os.path.exists(INBOX_FILE):
                try:
                    with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                        inbox = json.loads(f.read().strip() or "[]")
                    pending = len([m for m in inbox if not m.get('processed', False)])
                    if pending != last_count:
                        log(f"[UPDATE] {pending} messages pending")
                        last_count = pending
                except:
                    pass
            
            # Heartbeat every 5 iterations (10 seconds)
            if heartbeat_counter % 5 == 0:
                log(f"[ALIVE] Processor running... {last_count} pending")
            
            time.sleep(2)  # Check every 2 seconds
    
    except KeyboardInterrupt:
        log("\n\n[STOP] Stopping processor...")
        log("[STOP] Done!")

if __name__ == "__main__":
    main()
