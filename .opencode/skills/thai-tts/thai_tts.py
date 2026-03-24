#!/usr/bin/env python3
"""
Thai Text-to-Speech - Standalone Script
Convert Thai text to speech using Microsoft Edge TTS
"""

import sys
import os
import re
import asyncio
import time

try:
    import edge_tts
except ImportError:
    print("Installing edge-tts...")
    os.system('pip install edge-tts')
    import edge_tts

THAI_VOICES = {
    "female": "th-TH-PremwadeeNeural",
    "male": "th-TH-NiwatNeural",
}

TEXT_CACHE = {}

def extract_thai_text(content):
    """Extract and clean Thai text from content"""
    lines = content.split('\n')
    thai_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('---', '```', '*Generated', '*Source:', '*Iterations')):
            continue
        cleaned = re.sub(r'^#+\s*', '', stripped)
        cleaned = cleaned.replace('*', '').replace('`', '').replace('|', ' ')
        cleaned = cleaned.replace('□', '').replace('>', '').replace('✅', '')
        cleaned = ' '.join(cleaned.split())
        
        if any('\u0E00' <= c <= '\u0E7F' for c in cleaned):
            thai_lines.append(cleaned)
    
    return '\n'.join(thai_lines)


async def text_to_speech(text, voice="female", rate="+0%", volume="+0%", output_file=None):
    """Convert text to speech and save as MP3"""
    voice_id = THAI_VOICES.get(voice, THAI_VOICES["female"])
    
    if not output_file:
        output_file = "output.mp3"
    
    print(f"[TTS] Voice: {voice} | Rate: {rate} | Volume: {volume}")
    print(f"[TTS] Characters: {len(text)}")
    
    try:
        communicate = edge_tts.Communicate(text, voice_id, rate=rate, volume=volume)
        await communicate.save(output_file)
        print(f"[TTS] Saved: {output_file}")
        return True
    except Exception as e:
        print(f"[TTS] Error: {e}")
        return False


async def process_input(input_text, voice="female", rate="+0%", volume="+0%", output_file=None):
    """Process text input (file or direct text)"""
    if os.path.exists(input_text):
        print(f"[TTS] Reading file: {input_text}")
        try:
            with open(input_text, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(input_text, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        
        thai_text = extract_thai_text(content)
        if not output_file:
            output_file = os.path.splitext(os.path.basename(input_text))[0] + ".mp3"
    else:
        print(f"[TTS] Using direct text input")
        thai_text = input_text
        if not output_file:
            output_file = "output.mp3"
    
    if not thai_text.strip():
        print("[TTS] No Thai text to process.")
        return False
    
    return await text_to_speech(thai_text, voice, rate, volume, output_file)


def main():
    print("=" * 50)
    print("  Thai Text-to-Speech (Edge TTS)")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage: python thai_tts.py <text|file> [voice] [rate] [volume]")
        print("\n  text/file: Direct Thai text OR path to text file")
        print("  voice    : female (default) or male")
        print("  rate     : +0% (default), +10%, -10%")
        print("  volume   : +0% (default), +20%, -20%")
        print("\nExample:")
        print("  python thai_tts.py \"ทดสอบ\"")
        print("  python thai_tts.py news.txt")
        print("  python thai_tts.py news.txt female +10% +0%")
        sys.exit(1)
    
    input_text = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 else "female"
    rate = sys.argv[3] if len(sys.argv) > 3 else "+0%"
    volume = sys.argv[4] if len(sys.argv) > 4 else "+0%"
    
    asyncio.run(process_input(input_text, voice, rate, volume))


if __name__ == "__main__":
    main()
