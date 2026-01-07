import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web
import asyncio

# --- ТВОИ НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 
# ----------------------

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Привет! Нажми на кнопку ниже, чтобы заполнить анкету.", reply_markup=markup)

async def handle_submit(request):
    # --- ЭТО ВАЖНО: Разрешаем сайту присылать данные (CORS) ---
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    
    if request.method == "OPTIONS":
        return web.Response(headers=headers)
    
    try:
        data = await request.json()
        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник: {data.get('nick')}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data="accept"),
            InlineKeyboardButton("❌ Отклонить", callback_data="reject")
        )
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        print(f"Ошибка: {e}")
        return web.Response(text="Error", status=500, headers=headers)

async def on_startup(dp):
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit) # Для предварительной проверки браузером
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
