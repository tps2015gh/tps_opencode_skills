#!/usr/bin/env python3
"""
Telegram AI Chat Bot
接收 Telegram 消息 → 发送给 AI → 返回 AI 回复
使用环境变量存储敏感信息
"""

import os
import sys
import logging
import asyncio
import aiohttp
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# ─── Configuration from Environment Variables ───────────────────────────────────
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
AI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
ALLOWED_USERS = os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if os.getenv('TELEGRAM_ALLOWED_USERS') else []
SYSTEM_PROMPT = os.getenv('AI_SYSTEM_PROMPT', 'คุณคือ AI assistant ที่ตอบเป็นภาษาไทย ใช้สไตล์เป็นกันเอง กระชับ')

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Check Configuration ───────────────────────────────────────────────────────
def check_config():
    """检查必要的环境变量"""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append('TELEGRAM_BOT_TOKEN')
    if not AI_API_KEY:
        missing.append('OPENAI_API_KEY')
    
    if missing:
        print("=" * 60)
        print("❌ 缺少必要的环境变量!")
        print("=" * 60)
        for var in missing:
            print(f"\n  {var}: 未设置")
        print("\n请设置以下环境变量:")
        print("  Windows: setx VARIABLE_NAME \"value\"")
        print("  Linux/Mac: export VARIABLE_NAME=\"value\"")
        print("\n环境变量列表:")
        print("  TELEGRAM_BOT_TOKEN - Telegram Bot Token (从 @BotFather 获取)")
        print("  OPENAI_API_KEY - AI API Key")
        print("  OPENAI_API_BASE - API 地址 (可选, 默认: https://api.openai.com/v1)")
        print("  AI_MODEL - AI 模型 (可选, 默认: gpt-4o-mini)")
        print("  TELEGRAM_ALLOWED_USERS - 允许的用户ID,逗号分隔 (可选)")
        print("=" * 60)
        return False
    return True

# ─── User Validation ──────────────────────────────────────────────────────────
def is_allowed_user(update: Update) -> bool:
    """检查用户是否有权限"""
    if not ALLOWED_USERS or '' in ALLOWED_USERS:
        return True
    return str(update.effective_user.id) in ALLOWED_USERS

# ─── AI Chat Function ──────────────────────────────────────────────────────────
async def chat_with_ai(user_message: str) -> str:
    """发送消息给 AI 并获取回复"""
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AI_API_BASE}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    error_text = await response.text()
                    logger.error(f"AI API Error: {response.status} - {error_text}")
                    return f"❌ AI API 错误: {response.status}"
    except asyncio.TimeoutError:
        return "❌ AI 响应超时，请稍后重试"
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return f"❌ AI 错误: {str(e)}"

# ─── Commands ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ 你没有权限使用此机器人")
        return
    
    await update.message.reply_text(
        "👋 สวัสดีครับ!\n\n"
        "ฉันคือ AI Chat Bot\n"
        "ส่งข้อความมาคุยได้เลย!\n\n"
        "คำสั่ง:\n"
        "/start - เริ่มต้น\n"
        "/clear - ล้างการสนทนา\n"
        "/model - เช็คโมเดลที่ใช้"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清除对话历史（此版本不支持，提示用户）"""
    await update.message.reply_text(
        "🧹 พร้อมแล้ว!\n\n"
        "เริ่มสนทนาใหม่ได้เลย"
    )

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示当前使用的 AI 模型"""
    await update.message.reply_text(
        f"🤖 โมเดลปัจจุบัน: `{AI_MODEL}`",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ 你没有权限使用此机器人")
        return
    
    await update.message.reply_text(
        "📖 วิธีใช้งาน:\n\n"
        "1. ส่งข้อความมาคุยกับ AI ได้เลย\n"
        "2. AI จะตอบกลับเป็นภาษาไทย\n\n"
        "คำสั่งพิเศษ:\n"
        "/clear - เริ่มสนทนาใหม่\n"
        "/model - เช็คโมเดล\n"
        "/help - ดูคำสั่ง"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理所有消息，发送给 AI"""
    if not is_allowed_user(update):
        await update.message.reply_text("❌ 你没有权限使用此机器人")
        return
    
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    # 发送 "正在思考" 消息
    thinking_msg = await update.message.reply_text("🤔 AI กำลังคิด...")
    
    try:
        # 调用 AI
        ai_response = await chat_with_ai(user_message)
        
        # 删除 "正在思考" 消息
        await thinking_msg.delete()
        
        # 发送 AI 回复
        if len(ai_response) > 4000:
            # 分割长消息
            for i in range(0, len(ai_response), 4000):
                await update.message.reply_text(ai_response[i:i+4000])
        else:
            await update.message.reply_text(ai_response)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await thinking_msg.edit_text(f"❌ เกิดข้อผิดพลาด: {str(e)}")

async def post_init(application: Application):
    """设置机器人命令菜单"""
    await application.bot.set_my_commands([
        BotCommand("start", "เริ่มต้น"),
        BotCommand("help", "ดูความช่วยเหลือ"),
        BotCommand("clear", "เริ่มสนทนาใหม่"),
        BotCommand("model", "เช็คโมเดล"),
    ])

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Telegram AI Chat Bot")
    print("=" * 60)
    
    if not check_config():
        sys.exit(1)
    
    masked_token = TELEGRAM_TOKEN[:10] + "..." if len(TELEGRAM_TOKEN) > 10 else "***"
    print(f"\n📋 Configuration:")
    print(f"   Telegram Token: {masked_token}")
    print(f"   AI API: {AI_API_BASE}")
    print(f"   AI Model: {AI_MODEL}")
    print(f"   Allowed Users: {len([u for u in ALLOWED_USERS if u]) or 'All'}")
    print()
    print("🚀 Bot 正在启动...")
    print("📱 发送消息到你的 Telegram Bot!")
    print("=" * 60)
    
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
