import asyncio ,sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder



def add_log(user_id, start, end, duration):
    conn = sqlite3.connect('work_time.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO work_logs (user_id, start_time, end_time, duration) VALUES (?, ?, ?, ?)',
                   (user_id, start, end, duration))
    conn.commit()
    conn.close()


# Bazaga ulanish va jadval yaratish
def init_db():
    conn = sqlite3.connect('work_time.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_logs (
            user_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Bot tokeningizni kiriting
API_TOKEN = '8675658310:AAGeTvAgVKoxIKfxVAXmgOzv8yhPzhKmuAk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_sessions = {}

def main_menu(status="idle"):
    builder = ReplyKeyboardBuilder()
    
    # Holatga qarab o'zgaruvchi tugmalar
    if status == "working":
        builder.button(text="⏸ Tanaffus")
        builder.button(text="🛑 Ishni tugatish")
    elif status == "paused":
        builder.button(text="▶️ Davom ettirish")
        builder.button(text="🛑 Ishni tugatish")
    else:
        builder.button(text="🚀 Ishni boshlash")
    
    # Doimiy statistik tugmalar (bular har doim turadi)
    builder.button(text="📊 Bugun")
    builder.button(text="📅 Shu hafta")
    
    # Tugmalarni chiroyli tartibga solish
    builder.adjust(2) 
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
        start_dt = user_sessions[user_id]
        end_dt = datetime.now()
        duration_seconds = int((end_dt - start_dt).total_seconds())
        
        # Vaqtlarni matn ko'rinishiga keltiramiz
        start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Bazaga saqlash
        add_log(user_id, start_str, end_str, duration_seconds)
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        del user_sessions[user_id]
        await message.answer(f"Ish yakunlandi va bazaga saqlandi! ✅\n⏱ Vaqt: {hours}s, {minutes}d.")
    else:
        await message.answer("Siz hali ishni boshlamagansiz.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())