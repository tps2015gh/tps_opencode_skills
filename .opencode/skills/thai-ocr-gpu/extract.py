#!/usr/bin/env python3
"""
Thai OCR GPU - Extract Thai text from PDF (1 page at a time or all)
GPU: True
"""

import os
import sys
import gc
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Install dependencies
def check_deps():
    for mod in ['pdfplumber', 'pymupdf', 'easyocr', 'pythainlp', 'PIL', 'numpy']:
        try:
            __import__(mod)
        except:
            os.system(f'pip install {mod}')

check_deps()

import pymupdf as fitz
import easyocr
import numpy as np
from PIL import Image
from pythainlp.util import normalize

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize EasyOCR ONCE with GPU=True
print("Initializing EasyOCR with GPU=True...")
reader = easyocr.Reader(['th'], gpu=True)
print("EasyOCR ready!")

def normalize_thai(t):
    return normalize(t) if t else ""

def ocr_page(pdf_path, page_num):
    """OCR single page"""
    doc = fitz.open(pdf_path)
    
    if page_num < 1 or page_num > len(doc):
        print(f"Page {page_num} not found")
        return None
    
    page = doc[page_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    result = reader.readtext(np.array(img), detail=0, batch_size=1)
    page_text = normalize_thai(" ".join(result))
    
    doc.close()
    del page, pix, img
    gc.collect()
    
    return page_text

def extract_all(pdf_path, chat_id=None):
    """Extract all pages"""
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        return None
    
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    
    # Get page count
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    print(f"\nFile: {filename}")
    print(f"Pages: {total_pages}")
    print("=" * 40)
    
    all_text = ""
    
    for page_num in range(1, total_pages + 1):
        print(f"OCR page {page_num}/{total_pages} ...", end=" ", flush=True)
        
        page_text = ocr_page(pdf_path, page_num)
        
        if page_text:
            all_text += f"\n--- Page {page_num} ---\n{page_text}\n"
            print(f"OK ({len(page_text)} chars)")
        else:
            print("Empty")
        
        gc.collect()
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    
    print("=" * 40)
    print(f"DONE! {len(all_text)} chars")
    print(f"Saved: {output_file}")
    
    return output_file

def show_pages(pdf_path):
    """Show page count"""
    doc = fitz.open(pdf_path)
    total = len(doc)
    doc.close()
    return total

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Thai OCR GPU (gpu=True)")
        print("Usage:")
        print("  python extract.py <pdf_file>              # OCR all pages")
        print("  python extract.py <pdf_file> <page_num>  # OCR single page")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        # Single page
        page_num = int(sys.argv[2])
        print(f"\nOCR page {page_num} of {pdf_file}")
        text = ocr_page(pdf_file, page_num)
        if text:
            print(f"\n--- Page {page_num} ---\n{text}")
    else:
        # All pages
        extract_all(pdf_file)
