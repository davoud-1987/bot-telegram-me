import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import google.generativeai as genai

# -------------------- Logging --------------------
logging.basicConfig(level=logging.INFO)

# -------------------- Environment Variables --------------------
TELEGRAM_BOT_TOKEN =("7136725278:AAEW4DZ6tanqCjj5KCOiPHIZ6jjcB6YEVos")
GEMINI_API_KEY = ("AIzaSyCnaVM7seITQAV-khVh9eQxFcF87RmimoM")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN تعریف نشده!")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY تعریف نشده!")

# -------------------- Telegram Bot --------------------
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# -------------------- Gemini Init --------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# -------------------- Handlers --------------------
@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("سلام 👋 من ربات هوش مصنوعی هستم. هر سوالی داری بپرس!")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text
    try:
        response = model.generate_content(user_text)
        ai_reply = response.text
    except Exception as e:
        ai_reply = f"⚠️ خطا در ارتباط با Gemini: {e}"

    await message.reply(ai_reply)

# -------------------- Start Bot --------------------
if __name__ == "__main__":
    logging.info("🚀 Bot started...")
    executor.start_polling(dp, skip_updates=True)
