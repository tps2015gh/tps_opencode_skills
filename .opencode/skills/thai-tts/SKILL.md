---
name: thai-tts
description: Convert Thai text to speech (TTS) using Microsoft Edge TTS. Supports voice selection (female/male), speed control, and volume adjustment.
---

## Thai Text-to-Speech Skill

Convert Thai text files to audio using Microsoft Edge TTS with natural Thai voices.

## Prerequisites

```bash
pip install edge-tts pygame
```

## Usage

### Command Format
```
/tts <file> [voice] [rate] [volume]
```

### Parameters
- **file**: Path to text file (required)
- **voice**: `female` (default) or `male`
- **rate**: Speech speed (default: `+0%`)
  - `+10%` = faster, `-10%` = slower
- **volume**: Volume level (default: `+0%`)
  - `+20%` = louder, `-20%` = softer

### Examples
```
/tts news.txt
/tts news.txt female +10% +0%
/tts news.txt male -5% +10%
```

## Direct Python Usage

```bash
python thai-tts-v2/thai_edge_tts.py <file> [voice] [rate] [volume]
```

### Example
```bash
python thai-tts-v2/thai_edge_tts.py ai_news.txt female +0% +0%
```

## Thai Voices

| Voice | ID | Description |
|-------|-----|-------------|
| Female | `th-TH-PremwadeeNeural` | Recommended - Natural Thai female voice |
| Male | `th-TH-NiwatNeural` | Thai male voice |

## Features

- **Text extraction**: Automatically extracts Thai text from markdown files
- **Caching**: Optimized for faster response on repeated use
- **Speed control**: Adjust speech rate for faster/slower delivery
- **Volume control**: Adjust output volume
- **MP3 output**: Generates MP3 file with same name as input

## Batch Script Usage

```bash
tts_read_v2.bat <filename>
```

## Troubleshooting

- **Encoding errors**: Ensure text files are saved in UTF-8 format
- **No Thai text found**: File must contain Thai characters (ภาษาไทย)
- **Slow response**: Try reducing text file size or use v2 version
