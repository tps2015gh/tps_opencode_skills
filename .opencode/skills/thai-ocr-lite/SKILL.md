---
name: thai-ocr-lite
description: Extract Thai text from PDF files using Tesseract OCR (32-bit compatible)
---

## Thai OCR Lite Skill

A lightweight Thai OCR skill designed to work on 32-bit Python environments. Uses Tesseract OCR for local, token-free text extraction.

## Prerequisites

1.  <strong>Tesseract-OCR Installation (32-bit):</strong>
    <ul>
        <li>Download: <a href="https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-5.3.1.20230401.exe">Tesseract-OCR 32-bit Installer</a></li>
        <li>During installation, ensure "Thai" language data is selected.</li>
        <li>Add Tesseract's installation directory (e.g., <code>C:\Program Files (x86)\Tesseract-OCR</code>) to your System PATH environment variable.</li>
    </ul>

2.  <strong>Python Dependencies:</strong>
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
# Extract text from a PDF file
python .opencode/skills/thai-ocr-lite/extract_lite.py document.pdf

# Extract text and save to a specific folder
python .opencode/skills/thai-ocr-lite/extract_lite.py input.pdf output/result.txt
```

## Parameters

| Parameter     | Required | Default | Description                                      |
|---------------|----------|---------|--------------------------------------------------|
| `pdf_file`    | Yes      | -       | Path to the PDF file to process.                 |
| `output_file` | No       | auto    | Path for the output text file (defaults to .txt). |

## How It Works

1.  <strong>Image Conversion:</strong> Uses `PyMuPDF` (fitz) to convert each page of the PDF into a high- Aresolution image.
2.  <strong>OCR Processing:</strong> Employs `pytesseract` to interface with the Tesseract OCR engine. It specifically uses the 'tha' (Thai) language model for text recognition.
3.  <strong>Output:</strong> Concatenates the extracted text from all pages into a single `.txt` file.

## Tesseract OCR Engine

Tesseract is one of the most popular open-source OCR engines. Modern versions (like 4.x and 5.x, which this skill assumes) primarily use an LSTM (Long Short-Term Memory) neural network for character recognition. This architecture allows Tesseract to learn patterns and context, leading to improved accuracy, especially with multiple languages like Thai, provided the language data (`.traineddata` files) is correctly installed. The engine works by analyzing image segments, identifying characters, and assembling them into words and sentences based on language models.

## Performance Considerations

Tesseract OCR's speed is generally dependent on the CPU, the complexity of the document (number of pages, image resolution, text density), and the quality of the scan. While it is highly efficient for local, token-free processing, it may not always be as instantaneous as native PDF text extraction (which is only possible for non-scanned PDFs). Compared to cloud-based AI Vision solutions, Tesseract offers significant cost savings (zero tokens) but might require more processing time for very large or complex documents. It is well-suited for batch processing and scenarios where token costs are a primary concern.

## Project Integration
The skill is located at `.opencode/skills/thai-ocr-lite/`.
