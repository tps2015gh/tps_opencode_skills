---
name: piano
description: Play piano notes. Accept note sequences like "C4 D4 E4" or search songs from internet.
---

## Piano Skill

Generate and play piano notes as WAV audio.

## Prerequisites

No extra dependencies - uses built-in Python modules.

## Usage

### Generate notes and play
```bash
# Generate WAV
python .opencode/skills/piano/piano.py "C4 D4 E4 F4 G4"

# Play it
python .opencode/skills/play-audio/play_audio.py piano_output.wav

# Send to Telegram
python .opencode/skills/telegram-send/send.py audio <chat_id> piano_output.wav
```

### Custom tempo
```bash
python .opencode/skills/piano/piano.py "C4 E4 G4 C5" 0.4
```

### Save to specific file
```bash
python .opencode/skills/piano/piano.py "C4 D4 E4 C4" 0.3 song.wav
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| notes | Yes | - | Space-separated notes |
| tempo | No | 0.3 | Seconds per note |
| output | No | piano_output.wav | Output file path |

## Notes

| Range | Notes |
|-------|-------|
| Low | C3, D3, E3, F3, G3, A3, B3 |
| Mid | C4, D4, E4, F4, G4, A4, B4 |
| High | C5, D5, E5, F5, G5, A5, B5 |
| Very High | C6 |
| Sharps | C#4, D#4, F#4, G#4, A#4 |
| Flats | Db4, Eb4, Gb4, Ab4, Bb4 |
| Rest | R or - |

## Search Song Notes

Ask OpenCode: "Find notes for [song name]"
Then play the notes returned.

## Example Songs

### Twinkle Twinkle Little Star
```
C4 C4 G4 G4 A4 A4 G4 - F4 F4 E4 E4 D4 D4 C4
```

### Happy Birthday
```
C4 C4 D4 C4 F4 E4 - C4 C4 D4 C4 G4 F4
```

### Mary Had a Little Lamb
```
E4 D4 C4 D4 E4 E4 E4 - D4 D4 D4 - E4 G4 G4
```

### Jingle Bells
```
E4 E4 E4 - E4 E4 E4 - E4 G4 C4 D4 E4 - - - F4 F4 F4 F4 F4 E4 E4 E4 E4 D4 D4 E4 D4 - G4
```

## Full Workflow

```bash
# 1. Generate
python .opencode/skills/piano/piano.py "C4 D4 E4 C4"

# 2. Play locally
python .opencode/skills/play-audio/play_audio.py piano_output.wav

# 3. Send to Telegram
python .opencode/skills/telegram-send/send.py audio 7815216214 piano_output.wav "My song"
```
