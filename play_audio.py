#!/usr/bin/env python3
"""
Play Audio File
Play MP3, WAV, and other audio formats
"""

import sys
import os
import subprocess

try:
    import pygame
except ImportError:
    print("Installing pygame...")
    os.system('pip install pygame')
    import pygame

def play_audio(filepath):
    if not os.path.exists(filepath):
        print(f"[Play] File not found: {filepath}")
        return False
    
    print(f"[Play] {filepath}")
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        print("[Play] Press Ctrl+C to stop")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"[Play] Error: {e}")
        return False

def play_windows(filepath):
    """Use Windows default player"""
    print(f"[Play] Opening with default player: {filepath}")
    os.system(f'start "" "{filepath}"')

def main():
    if len(sys.argv) < 2:
        print("Usage: python play_audio.py <audio_file>")
        print("Example: python play_audio.py output.mp3")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"[Play] File not found: {filepath}")
        sys.exit(1)
    
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.mp3':
        play_audio(filepath)
    else:
        play_windows(filepath)

if __name__ == "__main__":
    main()
