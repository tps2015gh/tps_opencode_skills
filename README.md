# TPS OpenCode Skills

AI-powered Telegram bridge with reusable skills for OpenCode.

## Agent

| Field | Value |
|-------|-------|
| Model | MiMo V2 Pro Free (OpenCode) |
| Role | AI Developer & Assistant |
| Capabilities | Code development, skill creation, queue processing, web search, report generation |

## Development Team

| Role | Name | Description |
|------|------|-------------|
| Director Supervisor | @p400 | Project owner, strategy, and direction |
| AI Developer | **MiMo V2 Pro Free (OpenCode)** | Full-stack development, skill creation, system architecture |
| Human Debugger | @p400 | Testing, deadlock detection |

### MiMo V2 Pro Free - Development Contributions

| Area | Work Done |
|------|-----------|
| **Report System** | Built html-report skill with multi-page support, SVG bar/line graphs, border frames |
| **Facebook Converter** | Built html-to-facebook skill to convert HTML reports to Facebook posts with graph images |
| **PDF to Telegram** | Built pdf-to-telegram skill to list PDFs and send selected to Telegram |
| **Queue Monitor** | Created inbox polling system with 2-min interval, auto-reply, status updates |
| **Piano Skill** | Implemented piano note generation (C3-C6), WAV output, tempo control |
| **Thai TTS** | Integrated Microsoft Edge TTS for Thai text-to-speech |
| **Telegram Bridge** | Enhanced telegram-send with reply_to_message support |
| **Web Search** | Integrated news search and data extraction for reports |
| **Documentation** | Wrote SKILL.md files for all skills |
| **Bug Fixes** | Fixed multi-page iteration, border rendering, graph positioning |

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| telegram-send | `send.py text\|audio` | Send text/MP3 to Telegram |
| queue-check | `check.py` | Check pending messages |
| queue-notify | `notify.py` | Monitor queue, notify via Telegram |
| file-list | `list.py` | List files in directory |
| thai-tts | `thai_tts.py` | Text-to-speech (Thai) |
| play-audio | `play_audio.py` | Play audio files |
| piano | `piano.py` | Play piano notes, generate WAV |
| html-report | `report.py` | Create A4 portrait HTML reports |
| html-to-facebook | `convert.py` | Convert HTML reports to Facebook posts |
| pdf-to-telegram | `pdf_send.py` | List PDFs and send selected to Telegram |

## Quick Install to Other Project

```powershell
install.bat C:\your_project
```

Or manually:
```powershell
xcopy /E /I .opencode C:\your_project\.opencode
copy .env C:\your_project\.env
```

## Project Structure

```
.opencode/
  skills/
    telegram-send/    send messages to Telegram
    queue-check/      check inbox queue
    queue-notify/     background queue monitor
    file-list/        list files
    thai-tts/         text-to-speech
    play-audio/       play audio
    piano/            play piano notes
    html-report/      create A4 HTML reports
    html-to-facebook/ convert HTML to Facebook posts
    pdf-to-telegram/  list PDFs and send to Telegram
  commands/
    telegram.md       /telegram command
.env                  TELEGRAM_BOT_TOKEN
install.bat           install to other project
reports/              generated HTML reports (gitignored)
```

## Skill Docs

| Skill | File |
|-------|------|
| telegram-send | [.opencode/skills/telegram-send/SKILL.md](.opencode/skills/telegram-send/SKILL.md) |
| queue-check | [.opencode/skills/queue-check/SKILL.md](.opencode/skills/queue-check/SKILL.md) |
| queue-notify | [.opencode/skills/queue-notify/SKILL.md](.opencode/skills/queue-notify/SKILL.md) |
| file-list | [.opencode/skills/file-list/SKILL.md](.opencode/skills/file-list/SKILL.md) |
| thai-tts | [.opencode/skills/thai-tts/SKILL.md](.opencode/skills/thai-tts/SKILL.md) |
| play-audio | [.opencode/skills/play-audio/SKILL.md](.opencode/skills/play-audio/SKILL.md) |
| piano | [.opencode/skills/piano/SKILL.md](.opencode/skills/piano/SKILL.md) |
| html-report | [.opencode/skills/html-report/SKILL.md](.opencode/skills/html-report/SKILL.md) |
| html-to-facebook | [.opencode/skills/html-to-facebook/SKILL.md](.opencode/skills/html-to-facebook/SKILL.md) |
| pdf-to-telegram | [.opencode/skills/pdf-to-telegram/SKILL.md](.opencode/skills/pdf-to-telegram/SKILL.md) |

## How It Works

```
Telegram user sends message
  -> telegram_bridge.py writes to inbox.json
  -> queue_processor.py marks _ai: true
  -> OpenCode reads inbox, replies via telegram-send skill
  -> User receives reply in Telegram
```

## See Also

- [Restructuring Guide](RESTRUCTURING.md)
