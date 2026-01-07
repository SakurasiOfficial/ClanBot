import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 
# -----------------

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Обработка заявок с сайта
async def handle_submit(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    
    # Отвечаем на проверку браузера (CORS)
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
    
    try:
        data = await request.json()
        text = (
            f"<b>🔔 Новая заявка!</b>\n\n"
            f"👤 Ник: {data.get('nick')}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        print(f"Ошибка: {e}")
        return web.Response(text="Error", status=500, headers=headers)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот запущен! Нажми кнопку ниже для анкеты.", reply_markup=markup)

async def main():
    # Настраиваем веб-сервер
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    
    # Запускаем сервер и бота параллельно
    print("Запуск сервера на порту 10000...")
    await site.start()
    
    print("Запуск polling...")
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
