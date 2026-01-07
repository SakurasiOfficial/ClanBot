import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def handle_submit(request):
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"}
    if request.method == "OPTIONS": return web.Response(status=200, headers=headers)
    
    try:
        data = await request.json()
        u_id = data.get('user_id')
        u_name = data.get('username')
        nick = data.get('nick', 'Unknown')

        # Формируем ссылку на профиль
        if u_name:
            mention = f'<a href="https://t.me/{u_name}">{nick}</a>'
        elif u_id:
            mention = f'<a href="tg://user?id={u_id}">{nick}</a>'
        else:
            mention = f"<b>{nick}</b>"

        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник (нажми): {mention}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n\n"
            f"<i>Чтобы ответить, нажми на ник выше</i>"
        )

        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        logging.error(f"Error: {e}")
        return web.Response(text="Error", status=500, headers=headers)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот готов! Жми кнопку для анкеты:", reply_markup=kb)

async def main():
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()
    await dp.start_polling()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
