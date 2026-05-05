import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Bot tokeningizni kiriting
API_TOKEN = '8675658310:AAGeTvAgVKoxIKfxVAXmgOzv8yhPzhKmuAk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_sessions = {}

# Tugmalar
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚀 Ishni boshlash")
    builder.button(text="🛑 Ishni tugatish")
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Salom! Ish vaqtingizni hisoblashga tayyorman.", reply_markup=main_menu())

@dp.message(lambda message: message.text == "🚀 Ishni boshlash")
async def start_work(message: types.Message):
    user_id = message.from_user.id
    user_sessions[user_id] = datetime.now()
    start_time = user_sessions[user_id].strftime("%H:%M:%S")
    await message.answer(f"Ish boshlandi! 🕒 Soat: {start_time}\nBaraka bersin!")

@dp.message(lambda message: message.text == "🛑 Ishni tugatish")
async def stop_work(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        start_time = user_sessions[user_id]
        duration = datetime.now() - start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        del user_sessions[user_id]
        await message.answer(f"Ish yakunlandi! ✅\n⏱ Sarflangan vaqt: {hours} soat, {minutes} daqiqa.")
    else:
        await message.answer("Siz hali ishni boshlamagansiz.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())