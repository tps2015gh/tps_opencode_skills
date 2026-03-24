---
name: pdf-to-telegram
description: List PDF files in folder and send selected to Telegram.
---

## PDF to Telegram Skill

List PDF files in a folder, select by number, and send to Telegram.

## Prerequisites

- telegram-send skill installed

## Usage

### List and send PDFs from current folder
```bash
python .opencode/skills/pdf-to-telegram/pdf_send.py
```

### List and send PDFs from specific folder
```bash
python .opencode/skills/pdf-to-telegram/pdf_send.py C:\Documents
```

### Specify chat ID
```bash
python .opencode/skills/pdf-to-telegram/pdf_send.py C:\Documents 7815216214
```

## How It Works

1. Scans folder for PDF files
2. Shows numbered list with file size
3. User selects by number
4. Sends selected PDF to Telegram via telegram-send skill

## Example

```
📄 PDF Files:
────────────────────────────────────
  1. report_2026.pdf (2.3 MB)
  2. invoice_march.pdf (156.2 KB)
  3. contract.pdf (1.1 MB)
────────────────────────────────────

🔢 Select PDF number (or 'q' to quit): 2

📤 Sending: invoice_march.pdf
✅ Sent: invoice_march.pdf
```

## Output

- Shows numbered PDF list
- Sends selected file to Telegram
- Confirmation message

## Files

| File | Description |
|------|-------------|
| pdf_send.py | Main script |
| SKILL.md | This file |
