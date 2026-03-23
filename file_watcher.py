#!/usr/bin/env python3
"""File watcher - uses watchdog, no polling"""
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BRIDGE_DIR = 'bridge_data'
TASK_FILE = os.path.join(BRIDGE_DIR, 'opencode_task.txt')
RESULT_FILE = os.path.join(BRIDGE_DIR, 'opencode_result.txt')

os.makedirs(BRIDGE_DIR, exist_ok=True)

class TaskHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('opencode_task.txt'):
            self.on_new_task()
    
    def on_created(self, event):
        if event.src_path.endswith('opencode_task.txt'):
            self.on_new_task()
    
    def on_new_task(self):
        try:
            if os.path.exists(TASK_FILE):
                with open(TASK_FILE, 'r', encoding='utf-8') as f:
                    task = f.read().strip()
                if task:
                    print(f"\n📝 TASK DETECTED: {task[:100]}")
                    print("   Waiting for OpenCode to process...")
        except Exception as e:
            print(f"Error reading task: {e}")

print("🔄 File watcher started")
print(f"   Watching: {TASK_FILE}")
print()

event_handler = TaskHandler()
observer = Observer()
observer.schedule(event_handler, BRIDGE_DIR, recursive=False)
observer.start()

print("Watching for file changes... (Ctrl+C to stop)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()