# Restructuring Guide

## What Changed

All skill Python scripts moved inside `.opencode/skills/<name>/` folders.

### Before
```
/
  telegram_bridge.py
  queue_processor.py
  thai_tts.py        <- was at root
  play_audio.py      <- was at root
  .opencode/
    skills/
      thai-tts/SKILL.md
      play-audio/SKILL.md
```

### After
```
/
  telegram_bridge.py
  queue_processor.py
  .opencode/
    skills/
      thai-tts/
        SKILL.md
        thai_tts.py    <- moved here
      play-audio/
        SKILL.md
        play_audio.py  <- moved here
      telegram-send/
        SKILL.md
        send.py
      queue-check/
        SKILL.md
        check.py
      queue-notify/
        SKILL.md
        notify.py
      file-list/
        SKILL.md
        list.py
```

## Why

- Skills are self-contained in their folders
- Copy `.opencode` to any project = all skills come along
- No orphaned files at project root

## How to Copy to Another Project

```powershell
# Option 1: Use install script
install.bat C:\other_project

# Option 2: Manual copy
xcopy /E /I .opencode C:\other_project\.opencode
copy .env C:\other_project\.env
```

## Skills Overview

| Skill | File | Purpose |
|-------|------|---------|
| telegram-send | send.py | Send text/MP3 to Telegram |
| queue-check | check.py | Check pending messages |
| queue-notify | notify.py | Monitor queue, notify |
| file-list | list.py | List files |
| thai-tts | thai_tts.py | Text-to-speech |
| play-audio | play_audio.py | Play audio |
