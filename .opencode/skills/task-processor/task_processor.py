import urllib.request, urllib.parse, json
import os

TASK_SERVER = "http://localhost:5555"

def check_tasks():
    try:
        req = urllib.request.Request(f"{TASK_SERVER}/tasks", method="GET")
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        return data.get('tasks', [])
    except Exception as e:
        return []

def send_result(result):
    try:
        data = json.dumps({'result': result}).encode()
        req = urllib.request.Request(
            f"{TASK_SERVER}/result",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Error sending result: {e}")
        return False

async def process_task(task_text):
    print(f"Processing task: {task_text[:100]}")
    
    # This is where I would process the task
    # For now, return a placeholder
    result = f"Processed: {task_text[:100]}"
    
    send_result(result)
    return result