#!/usr/bin/env python3
"""
Telegram Bot - Environment Variables Version
Tokens are read from OS environment variables only (no hardcoded values)
"""

import os
import sys
import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# ─── Configuration from Environment Variables ───────────────────────────────────
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if os.getenv('TELEGRAM_ALLOWED_USERS') else []

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Check Configuration ───────────────────────────────────────────────────────
def check_config():
    """Check if required environment variables are set"""
    if not TELEGRAM_TOKEN:
        print("=" * 60)
        print("❌ TELEGRAM_BOT_TOKEN is not set!")
        print("=" * 60)
        print("\nPlease set your Telegram bot token:")
        print("  Windows: setx TELEGRAM_BOT_TOKEN \"your_token_here\"")
        print("  Linux/Mac: export TELEGRAM_BOT_TOKEN=\"your_token_here\"")
        print("\nTo get a token:")
        print("  1. Open Telegram and search for @BotFather")
        print("  2. Send /newbot")
        print("  3. Follow instructions and copy the token")
        print("=" * 60)
        return False
    return True

# ─── User Validation ──────────────────────────────────────────────────────────
def is_allowed_user(update: Update) -> bool:
    """Check if user is allowed to use this bot"""
    if not ALLOWED_USERS or '' in ALLOWED_USERS:
        return True  # No restriction
    
    user_id = str(update.effective_user.id)
    return user_id in ALLOWED_USERS

# ─── Commands ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "👋 สวัสดีครับ!\n\n"
        "ฉันคือ Telegram Bot\n\n"
        "คำสั่งที่ใช้ได้:\n"
        "/start - เริ่มต้น\n"
        "/help - ดูคำสั่งทั้งหมด\n"
        "/echo <ข้อความ> - ทวนข้อความ\n"
        "/tts <ข้อความ> - แปลงเป็นเสียง\n"
        "/info - ข้อมูลบอท"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "📖 คำสั่งทั้งหมด:\n\n"
        "/start - เริ่มต้นใช้งาน\n"
        "/help - แสดงคำสั่งทั้งหมด\n"
        "/echo <ข้อความ> - ทวนข้อความกลับ\n"
        "/tts <ข้อความ> - แปลงข้อความเป็นเสียง\n"
        "/info - ข้อมูลระบบ\n"
        "/id - ดู Chat ID ของคุณ"
    )

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"📢 {text}")
    else:
        await update.message.reply_text("ใช้: /echo <ข้อความ>")

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text-to-Speech command"""
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 วิธีใช้: /tts <ข้อความ>\n\n"
            "ตัวอย่าง:\n"
            "/tts สวัสดีครับ"
        )
        return
    
    text = ' '.join(context.args)
    await update.message.reply_text(f"⏳ กำลังแปลง: \"{text}\"")
    
    # Import TTS function
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from thai_tts import text_to_speech
        asyncio.run(text_to_speech(text, voice="female", rate="+0%", volume="+0%", output_file="tts_output.mp3"))
        
        if os.path.exists("tts_output.mp3"):
            with open("tts_output.mp3", "rb") as audio:
                await update.message.reply_voice(audio, caption=f"🔊 {text}")
            os.remove("tts_output.mp3")
        else:
            await update.message.reply_text("❌ ไม่สามารถสร้างไฟล์เสียงได้")
    except Exception as e:
        await update.message.reply_text(f"❌ เกิดข้อผิดพลาด: {e}")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    user = update.effective_user
    await update.message.reply_text(
        "ℹ️ ข้อมูลบอท:\n\n"
        f"👤 ชื่อ: {user.full_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"📅 วันที่: {update.message.date.strftime('%d/%m/%Y %H:%M')}\n"
        f"🤖 Bot Token: {'✅ Set' if TELEGRAM_TOKEN else '❌ Not Set'}"
    )

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's chat ID"""
    await update.message.reply_text(
        f"🆔 Your Chat ID: `{update.effective_chat.id}`\n\n"
        f"User ID: `{update.effective_user.id}`",
        parse_mode="Markdown"
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ ไม่รู้จักคำสั่งนี้\n"
        "พิมพ์ /help เพื่อดูคำสั่งทั้งหมด"
    )

async def post_init(application: Application):
    """Set bot commands after startup"""
    await application.bot.set_my_commands([
        BotCommand("start", "เริ่มต้น"),
        BotCommand("help", "ดูคำสั่งทั้งหมด"),
        BotCommand("echo", "ทวนข้อความ"),
        BotCommand("tts", "แปลงเป็นเสียง"),
        BotCommand("info", "ข้อมูลบอท"),
        BotCommand("id", "ดู Chat ID"),
    ])

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Telegram Bot - Environment Variables Version")
    print("=" * 60)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Show configuration status
    print(f"\n📋 Configuration:")
    print(f"   Bot Token: {'✅ Set' if TELEGRAM_TOKEN else '❌ Not Set'}")
    if TELEGRAM_TOKEN:
        masked = TELEGRAM_TOKEN[:10] + "..." + TELEGRAM_TOKEN[-5:] if len(TELEGRAM_TOKEN) > 15 else "***"
        print(f"   Token Preview: {masked}")
    print(f"   Allowed Users: {len(ALLOWED_USERS) if ALLOWED_USERS else 'All (no restriction)'}")
    print()
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("tts", tts_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_command))
    
    print("🚀 Bot is starting...")
    print("📱 Send a message to your bot on Telegram!")
    print("=" * 60)
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
