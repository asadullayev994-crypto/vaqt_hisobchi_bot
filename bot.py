import asyncio
import logging
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import FSInputFile

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

# --- UNIVERSAL MENYU ---
def get_menu(status="idle"):
    builder = ReplyKeyboardBuilder()
    
    if status == "working":
        builder.button(text="⏸ Tanaffus")
        builder.button(text="🛑 Ishni tugatish")
    elif status == "paused":
        builder.button(text="▶️ Davom ettirish")
        builder.button(text="🛑 Ishni tugatish")
    else:
        builder.button(text="🚀 Ishni boshlash")
    
    builder.button(text="📊 Bugun")
    builder.button(text="📅 Shu hafta")
    builder.button(text="🗓 Shu oy")
    builder.button(text="📁 Excel hisobot")
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- STATISTIKA FUNKSIYASI ---
def get_stats(user_id, days):
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect('work_time.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(duration) FROM work_logs WHERE user_id=? AND start_time >= ?', (user_id, since_date))
    res = cursor.fetchone()[0] or 0
    conn.close()
    h, r = divmod(res, 3600)
    m, _ = divmod(r, 60)
    return h, m

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Salom {message.from_user.full_name}! Vaqtni birga hisoblaymiz.", reply_markup=get_menu())

@dp.message(lambda m: m.text == "🚀 Ishni boshlash")
async def start_work(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {'status': 'working', 'start_time': datetime.now(), 'total_seconds': 0, 'session_start': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    await message.answer("Ish boshlandi! Baraka bersin.", reply_markup=get_menu("working"))

@dp.message(lambda m: m.text == "🛑 Ishni tugatish")
async def stop_work(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        data = user_data[user_id]
        total = data['total_seconds']
        if data['status'] == 'working':
            total += int((datetime.now() - data['start_time']).total_seconds())
        
        conn = sqlite3.connect('work_time.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO work_logs VALUES (?, ?, ?, ?)', (user_id, data['session_start'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total))
        conn.commit()
        conn.close()
        
        h, m = divmod(total, 3600)[0], divmod(total, 3600)[1] // 60
        del user_data[user_id]
        await message.answer(f"Ish yakunlandi! ✅\nVaxt: {h}s, {m}d.", reply_markup=get_menu("idle"))

# Statistikalar uchun handlerlar
@dp.message(lambda m: m.text in ["📊 Bugun", "📅 Shu hafta", "🗓 Shu oy"])
async def show_stats(message: types.Message):
    days = 0 if "Bugun" in message.text else (7 if "hafta" in message.text else 30)
    h, m = get_stats(message.from_user.id, days)
    await message.answer(f"{message.text} jami: {h} soat, {m} daqiqa.")

@dp.message(lambda m: m.text == "📁 Excel hisobot")
async def send_excel(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('work_time.db')
    df = pd.read_sql_query("SELECT start_time, end_time, duration FROM work_logs WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    
    if df.empty:
        await message.answer("Hozircha ma'lumot yo'q.")
        return

    # Soniyalarni soat/daqiqa ko'rinishiga o'tkazish
    df['duration'] = df['duration'].apply(lambda x: f"{x//3600}s {(x%3600)//60}d")
    file_path = f"report_{user_id}.xlsx"
    df.to_excel(file_path, index=False)
    
    excel_file = FSInputFile(file_path)
    await message.answer_document(excel_file, caption="Sizning barcha ish tarixingiz 📁")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())