---
name: thai-ocr
description: Extract Thai text from PDF files using OCR (EasyOCR) or text extraction (pdfplumber)
---

## Thai OCR Skill

Extract Thai text from PDF files. Supports both regular PDFs and scanned documents.

## Prerequisites

```bash
pip install pdfplumber pymupdf easyocr pythainlp pillow numpy
```

## Usage

### Extract text from PDF
```bash
python .opencode/skills/thai-ocr/extract.py <pdf_file> [output_file]
```

### Examples
```bash
# Extract from PDF
python .opencode/skills/thai-ocr/extract.py document.pdf

# Extract and save to text file
python .opencode/skills/thai-ocr/extract.py document.pdf output.txt

# Extract with OCR for scanned PDFs
python .opencode/skills/thai-ocr/extract.py scanned.pdf -o output.txt --ocr
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| pdf_file | Yes | - | Path to PDF file |
| output_file | No | auto | Output text file (default: same name .txt) |
| --ocr | No | false | Force OCR for scanned PDFs |

## How It Works

1. **Text Extraction**: First tries pdfplumber to extract text normally
2. **OCR Fallback**: If no text found, uses EasyOCR with Thai language model
3. **Normalization**: Uses pythainlp to normalize Thai text

## Notes

- OCR requires EasyOCR model download (~500MB)
- First OCR run will download Thai language model
- Use --ocr flag for scanned documents
