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
        "/ai <message> - Talk directly to AI\n"
        "/start - Start\n"
        "/status - Check status\n"
        "/pending - View pending messages\n"
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
        "How to use:\n\n"
        "/ai <message> - Talk directly to OpenCode AI Agent\n\n"
        "Or send any message and run /telegram in OpenCode"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages, save to inbox"""
    user = update.effective_user
    text = update.message.text
    
    add_to_inbox(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        user_id=user.id,
        username=user.username or user.first_name,
        text=text
    )
    
    await update.message.reply_text(
        f"Got your message!\n\n"
        f"From: @{user.username or user.first_name}\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
        f"Waiting for OpenCode Agent to reply..."
    )

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command - save to inbox for OpenCode Agent to process immediately"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /ai <your message>\n\n"
            "Example: /ai Hello, how are you?"
        )
        return
    
    text = " ".join(context.args)
    
    add_to_inbox(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        user_id=user.id,
        username=user.username or user.first_name,
        text=f"[/ai] {text}"
    )
    
    await update.message.reply_text(
        f"Forwarded to OpenCode Agent...\n\n"
        f"Message: {text[:100]}{'...' if len(text) > 100 else ''}"
    )

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start"),
        BotCommand("ai", "Talk to AI"),
        BotCommand("status", "Check status"),
        BotCommand("pending", "View pending"),
        BotCommand("help", "Help"),
        BotCommand("clear", "Clear data"),
    ])

# ─── Periodic Check for Outbox ──────────────────────────────────────────────
async def outbox_checker(app):
    """Periodically check outbox and send pending replies"""
    while True:
        try:
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
                            print(f"[OUTBOX] Sent reply to {msg['chat_id']}")
                        except Exception as e:
                            print(f"[OUTBOX] Error: {e}")
                
                if changed:
                    with open(OUTBOX_FILE, 'w', encoding='utf-8') as f:
                        json.dump(outbox, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[OUTBOX] Check error: {e}")
        
        await asyncio.sleep(2)

async def post_init_and_start(app):
    """Post init and start outbox checker"""
    asyncio.create_task(outbox_checker(app))
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
    print("Flow:")
    print("   1. Message in Telegram -> inbox.json")
    print("   2. Run /telegram in OpenCode")
    print("   3. Reply written to outbox.json")
    print("   4. This bot auto-sends reply to Telegram")
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
