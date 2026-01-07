import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 
MY_ACC_URL = "https://t.me/sakurasi_official" # <-- ВСТАВЬ СВОЮ ССЫЛКУ СЮДА

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- ПРИЕМ ЗАЯВОК ---
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
        u_id = data.get('user_id') # ID игрока для ответа
        
        text = (
            f"<b>🔔 Новая заявка в клан!</b>\n\n"
            f"👤 Ник: {nick}\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
        )

        # Кодируем данные в кнопку (действие_ID_Ник)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data=f"acc_{u_id}_{nick}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"rej_{u_id}_{nick}")
        )

        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        logging.error(f"Ошибка в handle_submit: {e}")
        return web.Response(text="Error", status=500, headers=headers)

# --- ОБРАБОТКА РЕШЕНИЯ АДМИНА ---
@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    parts = callback_query.data.split('_')
    action = parts[0]
    player_id = parts[1]
    nick = parts[2]

    if action == 'acc':
        res_text = "Принят ✅"
        user_msg = f"🎉 Поздравляем, <b>{nick}</b>! Твоя заявка в клан одобрена.\n\n👤 Напиши лидеру для вступления: {MY_ACC_URL}"
    else:
        res_text = "Отклонен ❌"
        user_msg = f"Привет, <b>{nick}</b>. К сожалению, твоя заявка в клан была отклонена. Попробуй позже!"

    # Убираем загрузку на кнопке
    await bot.answer_callback_query(callback_query.id, text=f"Решение отправлено!")

    # Отправляем уведомление игроку
    if player_id and player_id != "None":
        try:
            await bot.send_message(player_id, user_msg, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение игроку {player_id}: {e}")

    # Обновляем сообщение у админа
    new_text = callback_query.message.text + f"\n\n<b>Статус: {res_text}</b>"
    await bot.edit_message_text(
        chat_id=ADMIN_ID, 
        message_id=callback_query.message.message_id, 
        text=new_text, 
        parse_mode="HTML"
    )

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот запущен. Чтобы подать заявку, нажми на кнопку ниже:", reply_markup=markup)

# --- ЗАПУСК СЕРВЕРА И БОТА ---
async def main():
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    
    await site.start()
    logging.info("Сервер запущен на порту 10000")
    
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
