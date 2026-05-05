import asyncio
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN = '8675658310:AAGeTvAgVKoxIKfxVAXmgOzv8yhPzhKmuAk' 
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('work_time.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS work_logs 
                      (user_id INTEGER, start_time TEXT, end_time TEXT, duration INTEGER)''')
    conn.commit()
    conn.close()

init_db()
user_data = {}

# --- DINAMIK MENYU (MUHIM QISM) ---
def get_menu(status="idle"):
    builder = ReplyKeyboardBuilder()
    
    # Ish holatiga qarab o'zgaradigan tugmalar
    if status == "working":
        builder.button(text="⏸ Tanaffus")
        builder.button(text="🛑 Ishni tugatish")
    elif status == "paused":
        builder.button(text="▶️ Davom ettirish")
        builder.button(text="🛑 Ishni tugatish")
    else:
        builder.button(text="🚀 Ishni boshlash")
    
    # Har doim turadigan statistika tugmalari
    builder.button(text="📊 Bugun")
    builder.button(text="📅 Shu hafta")
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Vaqt hisobchi botga xush kelibsiz!", reply_markup=get_menu("idle"))

@dp.message(lambda message: message.text == "🚀 Ishni boshlash")
async def start_work(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        'status': 'working',
        'start_time': datetime.now(),
        'total_seconds': 0,
        'session_start': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # BU YERDA get_menu("working") deb yozish shart!
    await message.answer("Ish boshlandi!", reply_markup=get_menu("working"))

@dp.message(lambda message: message.text == "⏸ Tanaffus")
async def pause_work(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['status'] == 'working':
        diff = datetime.now() - user_data[user_id]['start_time']
        user_data[user_id]['total_seconds'] += int(diff.total_seconds())
        user_data[user_id]['status'] = 'paused'
        await message.answer("Tanaffus...", reply_markup=get_menu("paused"))

@dp.message(lambda message: message.text == "▶️ Davom ettirish")
async def resume_work(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['status'] == 'paused':
        user_data[user_id]['status'] = 'working'
        user_data[user_id]['start_time'] = datetime.now()
        await message.answer("Ish davom etmoqda...", reply_markup=get_menu("working"))

@dp.message(lambda message: message.text == "🛑 Ishni tugatish")
async def stop_work(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        data = user_data[user_id]
        total = data['total_seconds']
        if data['status'] == 'working':
            total += int((datetime.now() - data['start_time']).total_seconds())
        
        conn = sqlite3.connect('work_time.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO work_logs VALUES (?, ?, ?, ?)', 
                       (user_id, data['session_start'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total))
        conn.commit()
        conn.close()
        
        h, r = divmod(total, 3600)
        m, _ = divmod(r, 60)
        del user_data[user_id]
        await message.answer(f"Ish tugadi! ✅\nSof vaqt: {h}s, {m}d.", reply_markup=get_menu("idle"))

@dp.message(lambda message: message.text == "📊 Bugun")
async def stats_today(message: types.Message):
    user_id = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('work_time.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(duration) FROM work_logs WHERE user_id=? AND start_time LIKE ?', (user_id, f"{today}%"))
    res = cursor.fetchone()[0] or 0
    conn.close()
    h, r = divmod(res, 3600)
    m, _ = divmod(r, 60)
    await message.answer(f"📊 Bugun jami: {h} soat, {m} daqiqa.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())