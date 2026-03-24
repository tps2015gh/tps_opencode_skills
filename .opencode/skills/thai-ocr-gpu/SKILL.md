---
name: thai-ocr-gpu
description: Extract Thai text from PDF using GPU acceleration (Fast)
---

## Thai OCR GPU Skill

Extract Thai text from PDF using GPU acceleration. Requires NVIDIA GPU.

## Prerequisites

```bash
pip install pdfplumber pymupdf easyocr pythainlp pillow numpy torch
```

## Usage

```bash
python .opencode/skills/thai-ocr-gpu/extract.py <pdf_file> [chat_id]
```

## Examples

```bash
# Basic extraction
python .opencode/skills/thai-ocr-gpu/extract.py document.pdf

# With Telegram notification
python .googleocr/thai-ocr-gpu/extract.py document.pdf 123456789
```

## Check GPU

```bash
python .opencode/skills/check-gpu/gpu_check.py
```

## Notes

- Uses GPU if available (NVIDIA with CUDA)
- Falls back to CPU if no GPU
- Faster than regular Thai-OCR for large PDFs
