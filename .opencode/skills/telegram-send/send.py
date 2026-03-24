#!/usr/bin/env python3
"""Telegram Send - Send messages and audio to Telegram via Bot API"""

import os
import sys
import io
import json
import uuid
import urllib.request
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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


def send_message(chat_id: str, text: str, reply_to: str = None) -> dict:
    load_env()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return {'ok': False, 'error': 'TELEGRAM_BOT_TOKEN not set'}

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': str(chat_id), 'text': text}
    if reply_to:
        data['reply_to_message_id'] = str(reply_to)

    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def send_audio(chat_id: str, file_path: str, caption: str = '', reply_to: str = None) -> dict:
    load_env()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return {'ok': False, 'error': 'TELEGRAM_BOT_TOKEN not set'}

    if not os.path.exists(file_path):
        return {'ok': False, 'error': f'File not found: {file_path}'}

    url = f'https://api.telegram.org/bot{token}/sendAudio'
    boundary = uuid.uuid4().hex

    body = b''
    # chat_id
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
    body += f'{chat_id}\r\n'.encode()

    # caption
    if caption:
        body += f'--{boundary}\r\n'.encode()
        body += b'Content-Disposition: form-data; name="caption"\r\n\r\n'
        body += f'{caption}\r\n'.encode()

    # reply_to_message_id
    if reply_to:
        body += f'--{boundary}\r\n'.encode()
        body += b'Content-Disposition: form-data; name="reply_to_message_id"\r\n\r\n'
        body += f'{reply_to}\r\n'.encode()

    # audio file
    filename = os.path.basename(file_path)
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="audio"; filename="{filename}"\r\n'.encode()
    body += b'Content-Type: audio/mpeg\r\n\r\n'
    with open(file_path, 'rb') as f:
        body += f.read()
    body += b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    try:
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {'ok': False, 'error': str(e)}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  Text:  python send.py text <chat_id> <text> [reply_to_message_id]')
        print('  Audio: python send.py audio <chat_id> <file.mp3> [caption] [reply_to_message_id]')
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'text':
        if len(sys.argv) < 4:
            print('Usage: python send.py text <chat_id> <text> [reply_to_message_id]')
            sys.exit(1)
        chat_id = sys.argv[2]
        text = sys.argv[3]
        reply_to = sys.argv[4] if len(sys.argv) > 4 else None
        result = send_message(chat_id, text, reply_to)

    elif mode == 'audio':
        if len(sys.argv) < 4:
            print('Usage: python send.py audio <chat_id> <file.mp3> [caption] [reply_to_message_id]')
            sys.exit(1)
        chat_id = sys.argv[2]
        file_path = sys.argv[3]
        caption = sys.argv[4] if len(sys.argv) > 4 else ''
        reply_to = sys.argv[5] if len(sys.argv) > 5 else None
        result = send_audio(chat_id, file_path, caption, reply_to)

    else:
        print(f'Unknown mode: {mode}')
        print('Use "text" or "audio"')
        sys.exit(1)

    try:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except UnicodeEncodeError:
        print(json.dumps(result, ensure_ascii=True, indent=2))
