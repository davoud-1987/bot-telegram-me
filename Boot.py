from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "7136725278:AAEW4DZ6tanqCjj5KCOiPHIZ6jjcB6YEVos"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("سلام! ربات روشنه ✅")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
