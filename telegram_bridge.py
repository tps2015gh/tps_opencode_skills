#!/usr/bin/env python3
"""
Telegram OpenCode Bridge v2
Telegram messages → File → OpenCode Agent processes → Reply
"""

VERSION = "2.0"

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
    
    await update.message.reply_text(
        f"Status:\n\n"
        f"Inbox (pending): {inbox_count}\n"
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
        await update.message.reply_text("Cleared!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n\n"
        "/ai <message> - Forward to OpenCode Agent\n"
        "/aia <message> - Forward with audio reply\n"
        "/readx - Read last reply as TTS audio\n"
        "/status - Check bridge status\n"
        "/pending - View pending messages\n"
        "/clear - Clear all data\n\n"
        "Auto-commands (instant):\n"
        "hello, hi, ok, thanks\n"
        "time, date\n"
        "git status, git log, git branch\n"
        "cmd <command>\n\n"
        "Simple chat works instantly!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages - auto-respond or process immediately"""
    user = update.effective_user
    text = update.message.text.strip()
    
    # Check for auto-response first
    auto_reply = get_auto_response(text)
    if auto_reply:
        # Send auto-response immediately
        await update.message.reply_text(auto_reply)
        return
    
    # Check if it's a command (starts with /)
    if text.startswith('/'):
        add_to_inbox(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            text=f"[/ai] {text}"
        )
        await update.message.reply_text(
            f"Command received!\n\n"
            f"Use /ai to forward to OpenCode Agent.\n"
            f"For instant response, just chat normally."
        )
    else:
        # Regular message - add to inbox and auto-process
        add_to_inbox(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            text=text
        )
        await update.message.reply_text(
            f"Message received!\n\n"
            f"For quick responses, try: hello, time, date, git status"
        )

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command - add to inbox for OpenCode"""
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
    
    await update.message.reply_text(
        f"Message forwarded to OpenCode Agent!\n\n"
        f"Run /telegram in OpenCode to process.\n"
        f"Or just chat - I auto-respond to simple messages."
    )

async def aia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /aia command - add to inbox for OpenCode with audio"""
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
    
    await update.message.reply_text(
        f"Message forwarded (audio mode)!\n\n"
        f"OpenCode Agent will reply with text + audio."
    )

async def telegram_loop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /telegram command - process inbox with auto-restart loop"""
    chat_id = update.message.chat_id
    
    await update.message.reply_text(
        "Starting Telegram inbox processor...\n"
        "Auto-restart enabled if crashed.\n"
        "Sends 'stop' to halt."
    )
    
    messages_processed = 0
    last_message_count = -1
    stop_requested = False
    restart_count = 0
    
    import time
    start_time = time.time()
    max_runtime = 300  # 5 minutes max
    
    while time.time() - start_time < max_runtime and not stop_requested:
        try:
            if os.path.exists(INBOX_FILE):
                try:
                    with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            inbox = json.loads(content)
                        else:
                            inbox = []
                except json.JSONDecodeError:
                    inbox = []
                
                pending = [m for m in inbox if not m.get('processed', False)]
                
                if len(pending) == 0:
                    if messages_processed > 0:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"Done! Processed {messages_processed} messages."
                        )
                    return
                
                if len(pending) != last_message_count:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"Processing... {len(pending)} messages remaining"
                    )
                    last_message_count = len(pending)
                
                msg = pending[0]
                msg['processed'] = True
                
                with open(INBOX_FILE, 'w', encoding='utf-8') as f:
                    json.dump(inbox, f, ensure_ascii=False, indent=2)
                
                messages_processed += 1
                print(f"[LOOP] Marked: {msg.get('text', '')[:50]}...")
        
        except asyncio.CancelledError:
            print("[LOOP] Cancelled")
            break
        except Exception as e:
            print(f"[LOOP] Error: {e}")
            restart_count += 1
            if restart_count > 10:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Too many errors ({restart_count}). Stopping."
                )
                break
            await asyncio.sleep(2)  # Wait before retry
        
        await asyncio.sleep(1)
    
    if time.time() - start_time >= max_runtime:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Timeout (5min). Processed {messages_processed} messages."
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
        
        # Generate TTS - use await instead of asyncio.run
        try:
            import edge_tts
            communicate = edge_tts.Communicate(content[:2000], "th-TH-PremwadeeNeural")
            await communicate.save(tts_output)
            
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
        BotCommand("readx", "Read as audio"),
        BotCommand("status", "Check status"),
        BotCommand("pending", "View pending"),
        BotCommand("help", "All commands"),
        BotCommand("clear", "Clear data"),
    ])

# ─── Command Executor ───────────────────────────────────────────────────────
import subprocess

def save_last_response(text: str):
    """Save last response to file for /readx"""
    try:
        with open(os.path.join(BRIDGE_DIR, 'last_response.txt'), 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        pass

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
    """No longer needed - queue_processor handles everything"""
    pass

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    
    print("=" * 60)
    print(f"  Telegram OpenCode Bridge v{VERSION}")
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
    
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("aia", aia_command))
    application.add_handler(CommandHandler("readx", readx_command))
    application.add_handler(CommandHandler("telegram", telegram_loop_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    import asyncio
    
    async def run_with_interrupt():
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        print("Bot running. Press Ctrl+C to stop...")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Stopping...")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            print("[SHUTDOWN] Bot stopped.")
    
    asyncio.run(run_with_interrupt())

if __name__ == "__main__":
    main()
