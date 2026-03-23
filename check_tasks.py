#!/usr/bin/env python3
"""Check for OpenCode tasks and notify"""
import os, time, json

BRIDGE_DIR = 'bridge_data'
TASK_FILE = os.path.join(BRIDGE_DIR, 'opencode_task.txt')
TODO_FILE = os.path.join(BRIDGE_DIR, 'todo.json')

def check():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            task = f.read().strip()
        print(f"\n" + "="*50)
        print(f"📝 NEW TASK: {task[:100]}")
        print("="*50)
        print("\nProcess this task? (yes/no)")
        
        todo = []
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                todo = json.load(f)
        todo.append({'task': task, 'time': time.time()})
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            json.dump(todo, f, ensure_ascii=False, indent=2)
        
        return task
    return None

if __name__ == "__main__":
    while True:
        task = check()
        if task:
            break
        time.sleep(5)