#!/usr/bin/env python3
"""Piano - Generate and play piano notes"""

import os
import sys
import math
import struct
import wave
import tempfile

SAMPLE_RATE = 44100
NOTE_FREQ = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'C6': 1046.50,
    'C#4': 277.18, 'D#4': 311.13, 'F#4': 369.99, 'G#4': 415.30, 'A#4': 466.16,
    'C#5': 554.37, 'D#5': 622.25, 'F#5': 739.99, 'G#5': 830.61, 'A#5': 932.33,
    'Db4': 277.18, 'Eb4': 311.13, 'Gb4': 369.99, 'Ab4': 415.30, 'Bb4': 466.16,
    'Db5': 554.37, 'Eb5': 622.25, 'Gb5': 739.99, 'Ab5': 830.61, 'Bb5': 932.33,
    'R': 0, 'REST': 0, '-': 0,
}


def note_to_freq(note):
    note = note.strip().upper()
    if note in NOTE_FREQ:
        return NOTE_FREQ[note]
    # Try with original case for sharps/flats
    for key in NOTE_FREQ:
        if key.upper() == note:
            return NOTE_FREQ[key]
    return 0


def generate_tone(freq, duration=0.3, volume=0.5):
    """Generate a single tone as bytes"""
    samples = int(SAMPLE_RATE * duration)
    data = b''
    for i in range(samples):
        t = i / SAMPLE_RATE
        # Envelope: fade in/out to avoid clicks
        env = min(1.0, t * 20) * max(0, 1.0 - (t - duration + 0.05) * 20) if t < duration else 0
        if freq > 0:
            # Sine wave with slight harmonics for piano-like sound
            val = math.sin(2 * math.pi * freq * t)
            val += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            val += 0.1 * math.sin(2 * math.pi * freq * 3 * t)
            val *= volume * env / 1.4
        else:
            val = 0
        val = max(-1, min(1, val))
        data += struct.pack('<h', int(val * 32767))
    return data


def play_notes(notes_str, tempo=0.3, output_file=None):
    """Play a sequence of notes. Notes separated by spaces."""
    notes = notes_str.replace(',', ' ').split()
    all_data = b''
    for note in notes:
        freq = note_to_freq(note)
        all_data += generate_tone(freq, tempo)

    if output_file is None:
        output_file = os.path.join(tempfile.gettempdir(), 'piano_output.wav')

    with wave.open(output_file, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(all_data)

    return output_file


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python piano.py <notes> [tempo] [output.wav]')
        print('')
        print('Examples:')
        print('  python piano.py "C4 D4 E4 C4"')
        print('  python piano.py "C4 E4 G4 C5" 0.4 song.wav')
        print('')
        print('Notes: C3-B6, C#4, Db4, - (rest)')
        print('Tempo: seconds per note (default 0.3)')
        sys.exit(1)

    notes = sys.argv[1]
    tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
    output = sys.argv[3] if len(sys.argv) > 3 else None

    outfile = play_notes(notes, tempo, output)
    print(f'Generated: {outfile}')
