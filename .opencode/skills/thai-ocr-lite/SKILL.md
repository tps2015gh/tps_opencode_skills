---
name: thai-ocr-lite
description: Extract Thai text from PDF files using Tesseract OCR (32-bit compatible)
---

## Thai OCR Lite Skill

A lightweight Thai OCR skill designed to work on 32-bit Python environments. Uses Tesseract OCR.

## Prerequisites

1. **Install Tesseract-OCR (32-bit)**: 
   - Download: [Tesseract-OCR 32-bit Installer](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-5.3.1.20230401.exe)
   - **Crucial:** Select "Thai" language data during installation.
   - Add `C:\Program Files (x86)\Tesseract-OCR` to your System PATH.

2. **Python Dependencies**:
   ```bash
   pip install pytesseract pymupdf pillow
   ```

## Usage

### Extract text from PDF
```bash
python .opencode/skills/thai-ocr-lite/extract_lite.py <pdf_file> [output_file]
```

### Examples
```bash
# Extract from PDF
python .opencode/skills/thai-ocr-lite/extract_lite.py document.pdf

# Extract and save to specific folder
python .opencode/skills/thai-ocr-lite/extract_lite.py document.pdf output/result.txt
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| pdf_file | Yes | - | Path to PDF file |
| output_file | No | auto | Output text file (default: same name .txt) |

## How It Works

1. **Image Conversion**: Converts PDF pages to high-resolution images using `PyMuPDF` (fitz).
2. **OCR**: Uses `Tesseract` to perform Thai OCR on each image.
3. **Save**: Appends extracted text from all pages into a single `.txt` file.

## Notes

- Requires Tesseract-OCR binary installed on Windows.
- Best for scanned documents in 32-bit environments where EasyOCR is not supported.
