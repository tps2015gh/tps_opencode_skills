import sys
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_thai_ocr(pdf_path, output_path=None):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    # Auto-generate output path if not provided
    if not output_path:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"pdf_ocr_002/{base_name}.txt"

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Starting OCR on: {pdf_path}")
    
    try:
        # Check if tesseract is available
        # Manually point to the 64-bit installation path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract-OCR not found on System PATH.")
        print("Please download and install from: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-5.3.1.20230401.exe")
        print("Make sure to add it to your PATH and include Thai language data.")
        return

    # Open the PDF
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    full_text = []

    print(f"Total pages: {total_pages}")

    for i in range(total_pages):
        page = doc.load_page(i)
        
        # High resolution for better OCR (zoom=2.0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # Perform Thai OCR
        print(f"[*] Processing page {i+1}/{total_pages}...", end="\r")
        text = pytesseract.image_to_string(img, lang='tha')
        full_text.append(f"--- Page {i+1} ---\n{text}\n")

    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))

    print(f"\n[SUCCESS] Extracted text saved to: {output_path}")
    doc.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_lite.py <pdf_file> [output_file]")
    else:
        pdf_input = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        extract_thai_ocr(pdf_input, output_file)
