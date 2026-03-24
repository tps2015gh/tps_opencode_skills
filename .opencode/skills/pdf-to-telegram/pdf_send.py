#!/usr/bin/env python3
"""List PDFs in folder and send selected to Telegram"""

import os
import sys
import glob
import subprocess


def list_pdfs(folder='.'):
    """List all PDF files in folder"""
    pattern = os.path.join(folder, '*.pdf')
    pdfs = glob.glob(pattern)
    pdfs.sort(key=os.path.getmtime, reverse=True)
    return pdfs


def display_pdfs(pdfs):
    """Display numbered list of PDFs"""
    if not pdfs:
        print("No PDF files found.")
        return
    
    print("\n📄 PDF Files:")
    print("─" * 40)
    for i, pdf in enumerate(pdfs, 1):
        size = os.path.getsize(pdf)
        size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
        name = os.path.basename(pdf)
        print(f"  {i}. {name} ({size_str})")
    print("─" * 40)


def send_to_telegram(pdf_path, chat_id, reply_to=None):
    """Send PDF to Telegram using telegram-send skill"""
    send_script = os.path.join(os.path.dirname(__file__), '..', 'telegram-send', 'send.py')
    
    if not os.path.exists(send_script):
        print(f"Error: telegram-send skill not found at {send_script}")
        return False
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}")
        return False
    
    # Use telegram-send document mode to send PDF
    filename = os.path.basename(pdf_path)
    cmd = ['python', send_script, 'document', chat_id, pdf_path, filename]
    if reply_to:
        cmd.append(str(reply_to))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sent: {filename}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    # Default folder
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    chat_id = sys.argv[2] if len(sys.argv) > 2 else '7815216214'
    
    if not os.path.isdir(folder):
        print(f"Error: Folder not found: {folder}")
        sys.exit(1)
    
    # List PDFs
    pdfs = list_pdfs(folder)
    display_pdfs(pdfs)
    
    if not pdfs:
        sys.exit(0)
    
    # Get user selection
    while True:
        try:
            choice = input("\n🔢 Select PDF number (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Bye!")
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(pdfs):
                selected = pdfs[idx]
                print(f"\n📤 Sending: {os.path.basename(selected)}")
                send_to_telegram(selected, chat_id)
            else:
                print(f"❌ Invalid number. Enter 1-{len(pdfs)}")
                
        except ValueError:
            print("❌ Enter a number or 'q'")
        except KeyboardInterrupt:
            print("\nBye!")
            break


if __name__ == '__main__':
    main()
