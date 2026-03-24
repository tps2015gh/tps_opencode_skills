#!/usr/bin/env python3
"""
Thai OCR - Extract Thai text from PDF files
Supports both regular PDFs and scanned documents
Sends status updates to Telegram
"""

import os
import sys
import json
import gc
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Check and install dependencies
def check_dependencies():
    required = ['pdfplumber', 'pymupdf', 'easyocr', 'pythainlp', 'PIL', 'numpy']
    missing = []
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    
    if missing:
        print(f"Installing missing dependencies: {missing}")
        os.system(f"pip install {' '.join(missing)}")

check_dependencies()

import pdfplumber
try:
    import pymupdf as fitz
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import easyocr
    import numpy as np
    from PIL import Image
    HAS_EASYOCR = True
    
    # Check GPU availability
    USE_GPU = False
    try:
        import torch
        USE_GPU = torch.cuda.is_available()
    except:
        pass
        
except ImportError:
    HAS_EASYOCR = False
    USE_GPU = False

from pythainlp.util import normalize


# ============= Config =============
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


# ============= Telegram Notification =============
def load_env():
    env_file = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '.env'))
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value


def send_telegram(chat_id, text):
    """Send message to Telegram"""
    load_env()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return
    
    import urllib.request
    import urllib.parse
    
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': str(chat_id), 'text': text}
    
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
        resp = urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass


def notify(chat_id, step, status, details=""):
    """Send formatted notification"""
    emoji = {
        'start': '🔄',
        'progress': '⏳',
        'success': '✅',
        'error': '❌',
        'complete': '🎉'
    }
    
    msg = f"{emoji.get(status, '📄')} {step}"
    if details:
        msg += f"\n{details}"
    
    print(msg)
    
    if chat_id:
        send_telegram(chat_id, msg)


# ============= OCR Functions =============

def normalize_thai(text):
    """Normalize Thai text"""
    if not text:
        return ""
    return normalize(text)


def extract_text_pdfplumber(pdf_path, chat_id=None):
    """Extract text using pdfplumber with progress"""
    print("[*] Extracting text with pdfplumber...")
    
    all_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"[*] Total pages: {total_pages}")
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += normalize_thai(text) + "\n"
            
            # Progress every page
            if (i + 1) % 5 == 0 or i == 0:
                pct = int((i + 1) / total_pages * 100)
                print(f"[*] Progress: {i+1}/{total_pages} pages ({pct}%)")
                if chat_id:
                    send_telegram(chat_id, f"⏳ Extracting: {i+1}/{total_pages} pages ({pct}%)")
            
            del page
            gc.collect()
    
    return all_text


def extract_text_ocr(pdf_path, chat_id=None):
    """Extract text using OCR for scanned PDFs"""
    global USE_GPU
    
    if not HAS_PYMUPDF or not HAS_EASYOCR:
        return ""
    
    gpu_status = "GPU" if USE_GPU else "CPU"
    print(f"[*] Initializing EasyOCR (Thai only) - Using {gpu_status}...")
    if chat_id:
        send_telegram(chat_id, f"⏳ Loading EasyOCR ({gpu_status})...")
    
    reader = easyocr.Reader(['th'], gpu=USE_GPU)
    
    all_text = ""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"[*] Total pages to OCR: {total_pages}")
    
    for i, page in enumerate(doc):
        print(f"[*] OCR page {i+1}/{total_pages}...")
        if chat_id and (i + 1) % 3 == 0:
            pct = int((i + 1) / total_pages * 100)
            send_telegram(chat_id, f"⏳ OCR: {i+1}/{total_pages} pages ({pct}%)")
        
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        result = reader.readtext(np.array(img), detail=0, batch_size=1)
        page_text = " ".join(result)
        all_text += f"\n--- Page {i+1} ---\n{normalize_thai(page_text)}\n"
        gc.collect()
    
    doc.close()
    return all_text


def extract_pdf(pdf_path, output_file=None, use_ocr=False, chat_id=None):
    """Main extraction function"""
    
    if not os.path.exists(pdf_path):
        notify(chat_id, "Error: PDF not found", "error", pdf_path)
        return None
    
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    
    # Output to specific folder
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.txt")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    notify(chat_id, f"📄 Starting: {filename}", "start")
    
    # Step 1: Text extraction
    print("[*] Step 1: Text extraction...")
    all_text = extract_text_pdfplumber(pdf_path, chat_id)
    text_len = len(all_text.strip())
    print(f"[*] Extracted {text_len} characters")
    
    # Step 2: OCR if needed
    if use_ocr or text_len < 100:
        if use_ocr:
            notify(chat_id, "Step 2: OCR mode (forced)", "progress")
        else:
            notify(chat_id, f"Step 2: Only {text_len} chars, trying OCR...", "progress")
        
        all_text = extract_text_ocr(pdf_path, chat_id)
    
    if not all_text.strip():
        notify(chat_id, "Error: No text extracted", "error")
        return None
    
    # Step 3: Save
    notify(chat_id, "Step 3: Saving file...", "progress")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    
    notify(chat_id, f"✅ Complete! {len(all_text)} chars", "success")
    print(f"[+] Saved: {output_file}")
    
    # Send to Telegram
    if chat_id:
        notify(chat_id, "Sending file to Telegram...", "progress")
        try:
            telegram_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'telegram-send', 'send.py')
            cmd = f'python "{telegram_py}" document {chat_id} "{output_file}" "📄 {filename} - OCR"'
            os.system(cmd)
            notify(chat_id, "✅ File sent to Telegram!", "complete")
        except Exception as e:
            notify(chat_id, f"⚠️ Telegram error: {e}", "error")
    
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Thai OCR - Extract Thai text from PDF")
        print(f"Output folder: {OUTPUT_DIR}")
        print("")
        print("Usage: python extract.py <pdf_file> [--ocr] [chat_id]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    use_ocr = False
    chat_id = None
    
    for arg in sys.argv[2:]:
        if arg == '--ocr':
            use_ocr = True
        elif arg.isdigit():
            chat_id = arg
    
    result = extract_pdf(pdf_file, None, use_ocr, chat_id)
    
    if result:
        print(f"\n[SUCCESS] {result}")
    else:
        print("\n[FAILED]")
        sys.exit(1)
