#!/usr/bin/env python3
"""
Telegram OpenCode Bridge
Telegram messages → File → OpenCode Agent processes → Reply
No external AI needed, use OpenCode directly
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# ─── Configuration from Environment Variables ───────────────────────────────────
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BRIDGE_DIR = os.getenv('TELEGRAM_BRIDGE_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge_data'))
INBOX_FILE = os.path.join(BRIDGE_DIR, 'inbox.json')
OUTBOX_FILE = os.path.join(BRIDGE_DIR, 'outbox.json')

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Create Bridge Directory ───────────────────────────────────────────────────
os.makedirs(BRIDGE_DIR, exist_ok=True)

# ─── Check Configuration ───────────────────────────────────────────────────────
def check_config():
    if not TELEGRAM_TOKEN:
        print("=" * 60)
        print("TELEGRAM_BOT_TOKEN is not set!")
        print("=" * 60)
        print("\nSet environment variable:")
        print("  PowerShell: $env:TELEGRAM_BOT_TOKEN=\"your_token\"")
        print("  CMD: set TELEGRAM_BOT_TOKEN=your_token")
        print("  Linux/Mac: export TELEGRAM_BOT_TOKEN=\"your_token\"")
        print("\nGet token from @BotFather")
        print("=" * 60)
        return False
    return True

# ─── Message Queue Functions ──────────────────────────────────────────────────
def add_to_inbox(chat_id: int, message_id: int, user_id: int, username: str, text: str):
    """Add message to inbox"""
    inbox = []
    if os.path.exists(INBOX_FILE):
        try:
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                inbox = json.load(f)
        except:
            inbox = []
    
    inbox.append({
        'timestamp': datetime.now().isoformat(),
        'chat_id': chat_id,
        'message_id': message_id,
        'user_id': user_id,
        'username': username,
        'text': text,
        'processed': False
    })
    
    with open(INBOX_FILE, 'w', encoding='utf-8') as f:
        json.dump(inbox, f, ensure_ascii=False, indent=2)
    
    print(f"[INBOX] New message from @{username}: {text[:50]}...")

def add_to_outbox(chat_id: int, reply_to_message_id: int, text: str):
    """Add reply to outbox"""
    outbox = []
    if os.path.exists(OUTBOX_FILE):
        try:
            with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                outbox = json.load(f)
        except:
            outbox = []
    
    outbox.append({
        'timestamp': datetime.now().isoformat(),
        'chat_id': chat_id,
        'reply_to_message_id': reply_to_message_id,
        'text': text,
        'sent': False
    })
    
    with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
        json.dump(outbox, f, ensure_ascii=False, indent=2)
    
    print(f"[OUTBOX] Reply queued for chat {chat_id}")

# ─── Commands ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi!\n\n"
        "I am Telegram Bridge for OpenCode Agent\n\n"
        "Commands:\n"
        "/ai <message> - Talk to AI\n"
        "/aia <message> - Talk + audio reply\n"
        "/readx - Read last reply as audio\n"
        "/start - Start\n"
        "/status - Check status\n"
        "/clear - Clear data"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inbox_count = 0
    outbox_count = 0
    
    if os.path.exists(INBOX_FILE):
        try:
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                inbox = json.load(f)
                inbox_count = len([m for m in inbox if not m.get('processed', False)])
        except:
            pass
    
    if os.path.exists(OUTBOX_FILE):
        try:
            with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                outbox = json.load(f)
                outbox_count = len([m for m in outbox if not m.get('sent', False)])
        except:
            pass
    
    await update.message.reply_text(
        f"Status:\n\n"
        f"Inbox (pending): {inbox_count}\n"
        f"Outbox (pending): {outbox_count}\n"
        f"Bridge Dir: `{BRIDGE_DIR}`",
        parse_mode="Markdown"
    )

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = []
    
    if os.path.exists(INBOX_FILE):
        try:
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                inbox = json.load(f)
                pending = [m for m in inbox if not m.get('processed', False)]
                for m in pending[:5]:
                    ts = m['timestamp'][:19]
                    text = m['text'][:100]
                    messages.append(f"- [{ts}] @{m['username']}: {text}...")
        except:
            pass
    
    if messages:
        text = "Pending messages:\n\n" + "\n".join(messages)
    else:
        text = "No pending messages"
    
    await update.message.reply_text(text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.exists(INBOX_FILE):
            os.remove(INBOX_FILE)
        if os.path.exists(OUTBOX_FILE):
            os.remove(OUTBOX_FILE)
        await update.message.reply_text("Cleared!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n\n"
        "/ai <message> - Forward to OpenCode Agent\n"
        "/aia <message> - Forward with audio\n"
        "/readx - Read last reply as audio\n\n"
        "Auto-commands (instant):\n"
        "git status - Show git status\n"
        "git log - Show recent commits\n"
        "git branch - Show branches\n"
        "cmd <command> - Run any command\n\n"
        "Simple chat:\n"
        "hello, ok, thanks, time, date"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages"""
    user = update.effective_user
    text = update.message.text.strip()
    
    # Check if it's a command (starts with /)
    if text.startswith('/'):
        # Treat as /ai command
        add_to_inbox(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            text=f"[/ai] {text}"
        )
    else:
        # Regular message - add to inbox
        add_to_inbox(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            text=text
        )
    
    await update.message.reply_text(
        f"Message received!\n\n"
        f"From: @{user.username or user.first_name}\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
        f"OpenCode Agent will reply..."
    )
    
    await update.message.reply_text(
        f"Got your message!\n\n"
        f"From: @{user.username or user.first_name}\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
        f"Waiting for OpenCode Agent to reply..."
    )

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command - reply immediately"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /ai <your message>\n\n"
            "Example: /ai Hello, how are you?"
        )
        return
    
    text = " ".join(context.args)
    
    # Save to inbox for OpenCode
    add_to_inbox(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        user_id=user.id,
        username=user.username or user.first_name,
        text=f"[/ai] {text}"
    )
    
    # REPLY IMMEDIATELY
    await update.message.reply_text(
        f"Message received!\n\n"
        f"From: @{user.username or user.first_name}\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
        f"OpenCode Agent will reply soon..."
    )

async def aia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /aia command - reply immediately with audio note"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /aia <your message>\n\n"
            "Example: /aia Hello, how are you?\n\n"
            "This will reply with both text and audio."
        )
        return
    
    text = " ".join(context.args)
    
    # Save to inbox for OpenCode
    add_to_inbox(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        user_id=user.id,
        username=user.username or user.first_name,
        text=f"[/aia] {text}"
    )
    
    # REPLY IMMEDIATELY
    await update.message.reply_text(
        f"Message received (audio mode)!\n\n"
        f"From: @{user.username or user.first_name}\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
        f"OpenCode Agent will reply with text + audio..."
    )

async def readx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /readx command - read last AI response as TTS"""
    user = update.effective_user
    
    last_response_file = os.path.join(BRIDGE_DIR, 'last_response.txt')
    
    if not os.path.exists(last_response_file):
        await update.message.reply_text(
            "No last response to read.\n\n"
            "Use /ai <message> first, then /readx to hear the reply."
        )
        return
    
    try:
        with open(last_response_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            await update.message.reply_text("Last response is empty.")
            return
        
        # Save to TTS folder
        tts_input = os.path.join(BRIDGE_DIR, 'tts_input.txt')
        tts_output = os.path.join(BRIDGE_DIR, 'tts_output.mp3')
        
        with open(tts_input, 'w', encoding='utf-8') as f:
            f.write(content[:2000])  # Limit for TTS
        
        await update.message.reply_text("Generating audio...")
        
        # Generate TTS
        try:
            import edge_tts
            asyncio.run(edge_tts.Communicate(content[:2000], "th-TH-PremwadeeNeural").save(tts_output))
            
            with open(tts_output, 'rb') as audio:
                await update.message.reply_voice(audio, caption="Read: " + content[:100] + "...")
            
            # Clean up
            os.remove(tts_input)
            os.remove(tts_output)
        except ImportError:
            await update.message.reply_text("TTS not available. Install: pip install edge-tts")
        except Exception as e:
            await update.message.reply_text(f"TTS error: {e}")
            
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start"),
        BotCommand("ai", "Talk to AI"),
        BotCommand("aia", "Talk + Audio"),
        BotCommand("readx", "Read last reply"),
        BotCommand("status", "Check status"),
        BotCommand("pending", "View pending"),
        BotCommand("help", "Help"),
        BotCommand("clear", "Clear data"),
    ])

# ─── Command Executor ───────────────────────────────────────────────────────
import subprocess

def run_command(cmd: str) -> str:
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, timeout=30,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return result.stdout.strip() or result.stderr.strip() or "Done!"
    except Exception as e:
        return f"Error: {e}"

def get_auto_response(text: str) -> str:
    """Auto-responses including command execution"""
    text_lower = text.lower().strip()
    
    # Simple greetings
    if text_lower in ['ok', 'okay', 'ครับ', 'ขอบคุณ', 'thanks', 'thank you']:
        return "OK!"
    
    # Time
    if 'time' in text_lower or 'เวลา' in text_lower or 'กี่โมง' in text_lower:
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%H:%M')} ICT"
    
    # Date
    if 'date' in text_lower or 'วันที่' in text_lower or 'today' in text_lower:
        from datetime import datetime
        return f"Today: {datetime.now().strftime('%d/%m/%Y')}"
    
    # Status
    if 'status' in text_lower or 'สถานะ' in text_lower:
        return "System is running normally."
    
    # Hello
    if 'hello' in text_lower or 'hi' in text_lower or 'สวัสดี' in text_lower:
        return "Hello! I'm here. What can I help you with?"
    
    # Help
    if 'help' in text_lower or 'ช่วย' in text_lower:
        return "Commands:\n/ai <message> - Forward to AI\n/git <cmd> - Run git command\n/cmd <command> - Run any command"
    
    # Git commands
    if text_lower.startswith('git '):
        cmd = text_lower[4:]
        if 'status' in cmd:
            return f"```\n{run_command('git status')}\n```"
        if 'log' in cmd:
            return f"```\n{run_command('git log --oneline -5')}\n```"
        if 'branch' in cmd:
            return f"```\n{run_command('git branch -a')}\n```"
        if 'diff' in cmd:
            return f"```\n{run_command('git diff')}\n```"
        return f"Running: git {cmd}\n```\n{run_command('git ' + cmd)}\n```"
    
    # System commands
    if text_lower.startswith('cmd '):
        cmd = text_lower[4:]
        return f"```\n{run_command(cmd)}\n```"
    
    return None

# ─── Auto-Inbox Processor ───────────────────────────────────────────────────
async def inbox_processor(app):
    """Periodically check inbox and auto-respond"""
    print("[AUTO] Starting auto-inbox processor...")
    while True:
        try:
            if os.path.exists(INBOX_FILE):
                try:
                    with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            inbox = []
                        else:
                            inbox = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    inbox = []
                
                changed = False
                for msg in inbox:
                    if not msg.get('processed', False):
                        text = msg.get('text', '')
                        
                        # Get auto-response
                        auto_reply = get_auto_response(text)
                        if auto_reply:
                            try:
                                await app.bot.send_message(
                                    chat_id=msg['chat_id'],
                                    text=auto_reply,
                                    reply_to_message_id=msg.get('message_id')
                                )
                                msg['processed'] = True
                                changed = True
                                print(f"[AUTO] Replied to @{msg.get('username')}: {text[:50]}...")
                            except Exception as e:
                                print(f"[AUTO] Send error: {e}")
                
                if changed:
                    with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                        json.dump(inbox, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AUTO] Process error: {e}")
        
        await asyncio.sleep(1)

# ─── Periodic Check for Outbox ──────────────────────────────────────────────
async def outbox_checker(app):
    """Periodically check outbox and send pending replies"""
    last_check = 0
    while True:
        try:
            current_time = asyncio.get_event_loop().time()
            interval = 0.5 if current_time - last_check < 5 else 2
            
            if os.path.exists(OUTBOX_FILE):
                try:
                    with open(OUTBOX_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            outbox = []
                        else:
                            outbox = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    outbox = []
                
                changed = False
                for msg in outbox:
                    if not msg.get('sent', False):
                        try:
                            await app.bot.send_message(
                                chat_id=msg['chat_id'],
                                text=msg['text'],
                                reply_to_message_id=msg.get('reply_to_message_id')
                            )
                            msg['sent'] = True
                            changed = True
                            last_check = current_time
                            print(f"[OUTBOX] Sent reply to {msg['chat_id']}")
                        except Exception as e:
                            print(f"[OUTBOX] Error: {e}")
                
                if changed:
                    with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
                        json.dump(outbox, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[OUTBOX] Check error: {e}")
        
        await asyncio.sleep(interval)

async def post_init_and_start(app):
    """Post init and start all background tasks"""
    asyncio.create_task(outbox_checker(app))
    asyncio.create_task(inbox_processor(app))
    await post_init(app)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Telegram OpenCode Bridge")
    print("=" * 60)
    
    if not check_config():
        sys.exit(1)
    
    masked_token = TELEGRAM_TOKEN[:10] + "..." if len(TELEGRAM_TOKEN) > 10 else "***"
    print(f"\nConfiguration:")
    print(f"   Telegram Token: {masked_token}")
    print(f"   Bridge Dir: {BRIDGE_DIR}")
    print()
    print("Auto-Commands (no OpenCode needed):")
    print("   - git status, git log, git branch, git diff")
    print("   - cmd <command>")
    print("   - hello, ok, thanks, time, date")
    print()
    print("Bot is starting...")
    print()
    print("To run in background (PowerShell):")
    print("   Start-Process python -ArgumentList 'telegram_bridge.py' -WindowStyle Hidden")
    print()
    print("Bot is starting...")
    print("=" * 60)
    
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init_and_start).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("aia", aia_command))
    application.add_handler(CommandHandler("readx", readx_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
