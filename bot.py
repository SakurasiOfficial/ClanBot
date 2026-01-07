import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933 
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" 
MY_ACC_URL = "https://t.me/sakurasi_official" # Твоя ссылка уже тут

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- ПРИЕМ ЗАЯВОК С САЙТА ---
async def handle_submit(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)
    
    try:
        data = await request.json()
        nick = data.get('nick', 'Unknown')
        u_id = data.get('user_id', '0')
        
        text = (
            f"<b>🔔 Новая заявка!</b>\n\n"
            f"👤 Ник: <code>{nick}</code>\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинты: {data.get('points')}\n"
            f"🆔 ID: <code>{u_id}</code>"
        )

        # Короткие callback_data, чтобы не было ошибок
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Принять", callback_data=f"ok_{u_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"no_{u_id}")
        )

        await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb)
        return web.Response(text="OK", status=200, headers=headers)
    except Exception as e:
        logging.error(f"Error: {e}")
        return web.Response(text="Error", status=500, headers=headers)

# --- ОБРАБОТКА НАЖАТИЙ ---
@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    u_id = data.split('_')[1]
    
    # Вытаскиваем ник из текста сообщения для красоты
    nick_match = re.search(r"Ник: (.*)\n", callback_query.message.text)
    nick = nick_match.group(1).strip() if nick_match else "Игрок"

    if data.startswith('ok_'):
        res_text = "Принят ✅"
        user_msg = f"🎉 <b>{nick}</b>, твоя заявка одобрена!\n👤 Напиши лидеру: {MY_ACC_URL}"
    else:
        res_text = "Отклонен ❌"
        user_msg = f"Привет, <b>{nick}</b>. К сожалению, заявка отклонена."

    # Убираем часики на кнопке
    await bot.answer_callback_query(callback_query.id)

    # Отправляем ответ игроку
    if u_id and u_id not in ['0', 'null', 'None']:
        try:
            await bot.send_message(u_id, user_msg, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение игроку: {e}")

    # Обновляем сообщение у админа
    try:
        await bot.edit_message_text(
            chat_id=ADMIN_ID,
            message_id=callback_query.message.message_id,
            text=callback_query.message.text + f"\n\n<b>Статус: {res_text}</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка редактирования: {e}")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer("Бот запущен и готов принимать заявки!", reply_markup=kb)

async def main():
    app = web.Application()
    app.router.add_post('/submit', handle_submit)
    app.router.add_options('/submit', handle_submit)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()
    
    # Очистка очереди обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
