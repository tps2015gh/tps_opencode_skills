#!/usr/bin/env python3
"""Telegram Queue Processor v6 - Internal Todo List + Full Response"""

import os
import json
import time
import uuid

VERSION = "6.4"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TASK_SERVER = "http://localhost:5555"

print(f"TELEGRAM_TOKEN: {'SET' if TELEGRAM_TOKEN else 'NOT SET'}")
print(f"TASK_SERVER: {TASK_SERVER}")
BRIDGE_DIR = 'bridge_data'
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
OUTBOX_FILE = os.path.join(BRIDGE_DIR, 'outbox.json')
TODO_FILE = os.path.join(BRIDGE_DIR, 'todo.json')

os.makedirs(BRIDGE_DIR, exist_ok=True)

todo_list = []

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

def add_todo(text, chat_id, message_id, qid):
    global todo_list
    todo = {
        'id': qid,
        'text': text,
        'chat_id': chat_id,
        'message_id': message_id,
        'status': 'pending',
        'created_at': time.time()
    }
    todo_list.append(todo)
    save_todo()
    log(f"TODO ADD [{qid}]: {text[:30]}...")

def update_todo(qid, status, response=None):
    global todo_list
    for t in todo_list:
        if t['id'] == qid:
            t['status'] = status
            if response:
                t['response'] = response
            t['updated_at'] = time.time()
            save_todo()
            log(f"TODO UPDATE [{qid}]: {status}")
            break

def get_pending_todos():
    return [t for t in todo_list if t['status'] == 'pending']

def get_thinking_todos():
    return [t for t in todo_list if t['status'] == 'thinking']

def save_todo():
    write_json(TODO_FILE, todo_list)

def load_todo():
    global todo_list
    todo_list = read_json(TODO_FILE)

def send_telegram(chat_id, text, reply_to=None):
    log(f"SEND to {chat_id}: {text[:30]}...")
    if not TELEGRAM_TOKEN:
        log("FAIL: No TELEGRAM_TOKEN")
        return False
    import urllib.request, urllib.parse
    data = {'chat_id': str(chat_id), 'text': text}
    if reply_to:
        data['reply_to_message_id'] = reply_to
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
        resp = urllib.request.urlopen(req, timeout=10)
        log(f"OK: Sent to {chat_id}")
        return True
    except Exception as e:
        log(f"FAIL: {e}")
        return False

def call_ai(text):
    if not AI_API_KEY:
        return "No AI_API_KEY configured"
    import urllib.request, urllib.parse
    import json
    
    log(f"AI_API_BASE: {AI_API_BASE}")
    log(f"AI_MODEL: {AI_MODEL}")
    
    headers = {'Authorization': f'Bearer {AI_API_KEY}', 'Content-Type': 'application/json'}
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 2000
    }
    
def call_ai(text):
    try:
        import urllib.request, urllib.parse, json
        
        req = urllib.request.Request(
            f"{TASK_SERVER}/task",
            data=json.dumps({'text': text}).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=10)
        log(f"Task sent to server: {text[:30]}...")
        
        for i in range(60):
            time.sleep(2)
            try:
                req = urllib.request.Request(f"{TASK_SERVER}/result", method='GET')
                resp = urllib.request.urlopen(req, timeout=5)
                result = json.loads(resp.read().decode())
                if result.get('result'):
                    result_text = result['result']
                    log(f"Got result: {result_text[:50]}...")
                    return result_text
            except:
                pass
        
        return f"⏱️ Task sent to OpenCode: {text[:80]}"
    except Exception as e:
        log(f"ERROR calling task server: {e}")
        return f"Error: {e}"

def process_message(msg, qid):
    chat_id = msg['chat_id']
    message_id = msg['message_id']
    text = msg['text']
    
    log(f"PROCESS [{qid}]: {text}")
    send_telegram(chat_id, f"🔄 Processing: {text[:50]}...", message_id)
    update_todo(qid, 'processing')
    
    log(f"CALLING AI for: {text[:50]}...")
    response = call_ai(text)
    
    log(f"RESPONSE [{qid}]: {response[:100]}...")
    
    result = send_telegram(chat_id, f"✅ Done!\n\n{response}", message_id)
    log(f"SEND RESULT: {result}")
    update_todo(qid, 'completed', response)
    
    return response

def main():
    global todo_list
    load_todo()
    log(f"Queue Processor v{VERSION} - Todo List Enabled")
    log(f"Active jobs: {len(get_pending_todos())}")
    
    while True:
        try:
            inbox = read_json(INBOX_FILE)
            
            new_msgs = [m for m in inbox if not m.get('_qid')]
            
            if new_msgs:
                for msg in new_msgs:
                    qid = str(uuid.uuid4())[:8]
                    msg['_qid'] = qid
                    msg['_status'] = 'queued'
                    add_todo(msg.get('text', ''), msg['chat_id'], msg['message_id'], qid)
                    log(f"QUEUED [{qid}]: {msg.get('text', '')[:25]}")
                write_json(INBOX_FILE, inbox)
            
            pending = [m for m in inbox if m.get('_status') == 'queued']
            
            if pending:
                for msg in pending:
                    qid = msg.get('_qid', '???')
                    chat_id = msg['chat_id']
                    message_id = msg['message_id']
                    
                    if send_telegram(chat_id, "⏳ Thinking...", message_id):
                        msg['_status'] = 'sent'
                        update_todo(qid, 'thinking')
                        log(f"SENT [{qid}]")
                    else:
                        log(f"FAIL [{qid}] - retry next loop")
                write_json(INBOX_FILE, inbox)
            
            todos = get_thinking_todos()
            if todos:
                for t in todos:
                    if t['status'] == 'thinking':
                        process_message(
                            {'chat_id': t['chat_id'], 'message_id': t['message_id'], 'text': t['text']},
                            t['id']
                        )
            
            print(".", end="", flush=True)
            time.sleep(3)
            
        except KeyboardInterrupt:
            log("\nStop!")
            break
        except Exception as e:
            log(f"ERR: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
