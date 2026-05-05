import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokeningizni kiriting
API_TOKEN = '8675658310:AAGeTvAgVKoxIKfxVAXmgOzv8yhPzhKmuAk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchilarning ish boshlash vaqtini saqlash uchun lug'at
user_sessions = {}

# Tugmalar
buttons = ReplyKeyboardMarkup(resize_keyboard=True)
buttons.add(KeyboardButton("🚀 Ishni boshlash"), KeyboardButton("🛑 Ishni tugatish"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Ish vaqtingizni hisoblashga tayyorman.", reply_markup=buttons)

@dp.message_handler(lambda message: message.text == "🚀 Ishni boshlash")
async def start_work(message: types.Message):
    user_id = message.from_user.id
    user_sessions[user_id] = datetime.now()
    
    start_time = user_sessions[user_id].strftime("%H:%M:%S")
    await message.answer(f"Ish boshlandi! 🕒 Soat: {start_time}\nCharchamang!")

@dp.message_handler(lambda message: message.text == "🛑 Ishni tugatish")
async def stop_work(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        start_time = user_sessions[user_id]
        end_time = datetime.now()
        
        # Vaqt farqini hisoblash
        duration = end_time - start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Sessiyani o'chirish
        del user_sessions[user_id]
        
        response = (f"Ish yakunlandi! ✅\n\n"
                    f"⏱ Sarflangan vaqt: {hours} soat, {minutes} daqiqa\n"
                    f"Yaxshi dam oling!")
        await message.answer(response)
    else:
        await message.answer("Siz hali ishni boshlamagansiz. Avval 'Ishni boshlash'ni bosing.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)