# OpenCode Task Processor Skill

## Overview
Check task server for pending tasks, process them, and send results back.

## Setup
Start task server first:
```bash
python task_server.py
```

## Usage

### 1. Check for tasks
When user says "check tasks" or "/tasks", I will:
- Call GET http://localhost:5555/tasks
- If there are pending tasks, process each one

### 2. Process task
- Read the task from the server
- Process it (run commands, read files, etc.)
- Send result via POST to http://localhost:5555/result

### 3. Flow
```
Telegram → queue_processor → task_server → I check → Process → result to task_server → queue_processor → Telegram
```

## Commands
- `check tasks` - Check for pending tasks
- `/tasks` - Same as above