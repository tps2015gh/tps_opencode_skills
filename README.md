### New Skill: Thai OCR Lite (Tesseract-based)

This skill provides a robust Thai OCR solution for environments where standard libraries like EasyOCR cannot be used (e.g., 32-bit Python on Windows). It leverages the Tesseract OCR engine for local, token-free processing.

#### Purpose
To enable OCR processing of Thai text from scanned PDF documents, especially in constrained 32-bit environments.

#### Prerequisites
1.  <strong>Tesseract-OCR Installation:</strong>
    <ul>
        <li>Download from the official UB Mannheim GitHub Wiki: <a href="https://github.com/UB-Mannheim/tesseract/wiki">Tesseract at UB Mannheim (GitHub Wiki)</a></li>
        <li>During installation, ensure "Thai" language data is selected.</li>
        <li>Add Tesseract's installation directory (e.g., <code>C:\Program Files (x86)\Tesseract-OCR</code> for 32-bit, or <code>C:\Program Files\Tesseract-OCR</code> for 64-bit) to your System PATH environment variable.</li>
    </ul>

#### Dependencies
- `pytesseract`
- `pymupdf`
- `pillow`

#### Usage
```bash
python .opencode/skills/thai-ocr-lite/extract_lite.py <pdf_file> [output_file]
```

#### Performance (Speed Considerations)
Tesseract OCR's speed is generally dependent on the CPU, the complexity of the document (number of pages, image resolution, text density), and the quality of the scan. While it is highly efficient for local, token-free processing, it may not always be as instantaneous as native PDF text extraction (which is only possible for non-scanned PDFs). Compared to cloud-based AI Vision solutions, Tesseract offers significant cost savings (zero tokens) but might require more processing time for very large or complex documents. It is well-suited for batch processing and scenarios where token costs are a primary concern.

#### Project Integration
The skill is located at `.opencode/skills/thai-ocr-lite/`.

---

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
| mysql-query | `mysql_query.py` | Execute MySQL queries and display as table |
| **thai-ocr-lite** | `extract_lite.py` | **Thai OCR using Tesseract (for 32-bit systems)** |

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
- [Thai OCR Lite Skill Documentation](.opencode/skills/thai-ocr-lite/SKILL.md)
