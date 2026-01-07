import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- НАСТРОЙКИ (Твои данные уже вписаны) ---
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
    
    # Ответ на предварительную проверку браузера
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
    
    try:
        data = await request.json()
        nick = data.get('nick', 'Неизвестно')
        
        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник: {nick}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )

        # Кнопки для админа
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{nick}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{nick}")
        )

        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        logging.error(f"Ошибка при получении заявки: {e}")
        return web.Response(text="Error", status=500, headers=headers)

# --- ОБРАБОТКА НАЖАТИЙ НА КНОПКИ (Убираем зависание) ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(('accept_', 'reject_')))
async def process_callback(callback_query: types.CallbackQuery):
    # Определяем действие
    action_text = "Принят ✅" if "accept" in callback_query.data else "Отклонен ❌"
    nick = callback_query.data.split('_')[1]

    # 1. СРАЗУ отвечаем Телеграму, чтобы убрать "часики"
    await bot.answer_callback_query(callback_query.id, text=f"Игрок {nick}: {action_text}")

    # 2. Обновляем сообщение у админа (убираем кнопки)
    new_text = callback_query.message.text + f"\n\n<b>Статус: {action_text}</b>"
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=new_text,
        parse_mode="HTML"
    )

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот запущен! Нажми кнопку ниже, чтобы открыть анкету.", reply_markup=markup)

# --- ЗАПУСК ВСЕГО ВМЕСТЕ ---
async def main():
    # Настройка веб-сервера для сайта
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    
    logging.info("Запуск сервера на порту 10000 и Polling...")
    
    # Запускаем сервер и бота одновременно
    await asyncio.gather(
        site.start(),
        dp.start_polling()
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
