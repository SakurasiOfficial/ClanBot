import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- ОБРАБОТКА ДАННЫХ С САЙТА ---
async def handle_submit(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
    
    try:
        data = await request.json()
        nick = data.get('nick', 'Unknown')
        
        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник: {nick}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )

        # Создаем кнопки (максимально просто)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data=f"acc_{nick}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"rej_{nick}")
        )

        # Отправляем админу
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        logging.error(f"Ошибка в handle_submit: {e}")
        return web.Response(text="Error", status=500, headers=headers)

# --- ОБРАБОТКА НАЖАТИЙ (Исправленная логика для обеих кнопок) ---
@dp.callback_query_handler(lambda c: True) # Ловим все нажатия
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    
    if data.startswith('acc_'):
        action_text = "Принят ✅"
        nick = data.replace('acc_', '')
    elif data.startswith('rej_'):
        action_text = "Отклонен ❌"
        nick = data.replace('rej_', '')
    else:
        return

    # 1. Мгновенно убираем часики
    await bot.answer_callback_query(callback_query.id, text=f"{nick}: {action_text}")

    # 2. Обновляем сообщение
    new_text = callback_query.message.text + f"\n\n<b>Статус: {action_text}</b>"
    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=new_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка при редактировании: {e}")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот готов! Жми кнопку:", reply_markup=markup)

# --- ЗАПУСК ---
async def main():
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    
    await site.start()
    logging.info("Сервер Render запущен!")
    
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
