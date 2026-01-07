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

# 1. Главное меню (с кнопкой WebApp)
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Привет! Нажми на кнопку ниже, чтобы заполнить анкету.", reply_markup=markup)

# 2. Функция, которая принимает данные от сайта
async def handle_submit(request):
    try:
        data = await request.json()
        
        # Формируем текст сообщения для тебя
        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник: {data.get('nick')}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )
        
        # Кнопки управления для админа
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data="accept"),
            InlineKeyboardButton("❌ Отклонить", callback_data="reject")
        )
        
        # Отправляем анкету тебе в личку
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")
        return web.Response(text="Error", status=500)

# 3. Настройка веб-сервера (чтобы Render видел порт)
async def on_startup(dp):
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render автоматически дает порт 10000
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    print("Сервер порта 10000 запущен!")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
