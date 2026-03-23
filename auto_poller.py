#!/usr/bin/env python3
"""Auto-poller - Only reads local files, no network/tokens"""
import os
import time

BRIDGE_DIR = 'bridge_data'
TASK_FILE = os.path.join(BRIDGE_DIR, 'opencode_task.txt')
RESULT_FILE = os.path.join(BRIDGE_DIR, 'opencode_result.txt')

os.makedirs(BRIDGE_DIR, exist_ok=True)

print("🔄 Auto-poller started - checking files only")
print("   Task file: bridge_data/opencode_task.txt")
print("   Result file: bridge_data/opencode_result.txt")
print()

last_task = ""

while True:
    try:
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, 'r', encoding='utf-8') as f:
                task = f.read().strip()
            
            if task and task != last_task:
                print(f"\n📝 NEW TASK: {task[:100]}")
                print("   Waiting for OpenCode to process...")
                last_task = task
        
        if os.path.exists(RESULT_FILE):
            with open(RESULT_FILE, 'r', encoding='utf-8') as f:
                result = f.read().strip()
            if result:
                print(f"✅ RESULT READY: {result[:80]}...")
                # Result will be picked up by queue_processor
        
        time.sleep(3)
        print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nStopped")
        break
    except Exception as e:
        print(f"\nError: {e}")
        time.sleep(5)