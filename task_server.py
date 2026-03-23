#!/usr/bin/env python3
"""Simple task server - queue_processor calls this to notify me"""
import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)
BRIDGE_DIR = 'bridge_data'
TASK_FILE = os.path.join(BRIDGE_DIR, 'opencode_task.txt')

@app.route('/task', methods=['POST'])
def add_task():
    data = request.json
    task = data.get('text', '')
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        f.write(task)
    return jsonify({'status': 'ok', 'task': task[:50]})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            tasks.append(f.read())
    return jsonify({'tasks': tasks})

@app.route('/result', methods=['POST'])
def add_result():
    result = request.json.get('result', '')
    result_file = os.path.join(BRIDGE_DIR, 'opencode_result.txt')
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result)
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    os.makedirs(BRIDGE_DIR, exist_ok=True)
    print("Task server running on http://localhost:5555")
    app.run(port=5555, debug=False)