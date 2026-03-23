#!/usr/bin/env python3
"""Safe task poller - I check files, no HTTP/tokens involved"""
import os
import json
import time

BRIDGE_DIR = 'bridge_data'
TASK_FILE = os.path.join(BRIDGE_DIR, 'opencode_task.txt')
RESULT_FILE = os.path.join(BRIDGE_DIR, 'opencode_result.txt')
POLL_FLAG = os.path.join(BRIDGE_DIR, 'poll.txt')

os.makedirs(BRIDGE_DIR, exist_ok=True)

def check_for_tasks():
    """Called periodically - check if there's work"""
    if not os.path.exists(TASK_FILE):
        return None
    
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        task = f.read().strip()
    
    return task

def write_result(result):
    """Write result - queue_processor will pick it up"""
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        f.write(result)
    # Clear task file
    if os.path.exists(TASK_FILE):
        os.remove(TASK_FILE)

def poll():
    """Poll for new tasks - you can call this"""
    task = check_for_tasks()
    if task:
        print("\n" + "="*50)
        print(f"📝 TASK: {task[:100]}")
        print("="*50)
        return task
    return None

if __name__ == "__main__":
    print("Polling for tasks every 10 seconds...")
    print("Tell me 'check tasks' to process manually")
    while True:
        task = poll()
        if task:
            print(f"\nNew task found! Process it now.")
            print(f"Task: {task[:200]}")
            print("\nWrite result to bridge_data/opencode_result.txt when done")
        time.sleep(10)