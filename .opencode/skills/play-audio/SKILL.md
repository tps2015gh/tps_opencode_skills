---
name: play-audio
description: Play audio files (MP3, WAV, etc.) on Windows using pygame or command-line player.
---

## Play Audio Skill

Play audio files directly from the command line.

## Prerequisites

```bash
pip install pygame
```

## Usage

### Command Format
```
/play <audio_file>
```

### Examples
```
/play output.mp3
/play sound.wav
```

## Direct Python Usage

```bash
python play_audio.py <audio_file>
```

## Supported Formats

- MP3
- WAV
- OGG
- And other formats supported by pygame

## Notes

- Uses pygame for cross-platform audio playback
- On Windows, can also use `start` command to open with default player
