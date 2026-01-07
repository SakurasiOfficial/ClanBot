import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКИ (ЗАПОЛНИ СВОИ) ---
TOKEN = "ВАШ_ТОКЕН"
ADMIN_ID = 123456789 # Твой ID
WEBAPP_URL = "https://твойник.github.io/ClanBot/" 
# -------------------------------

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Привет! Нажми на кнопку, чтобы заполнить анкету в клан.", reply_markup=markup)

@dp.message(lambda message: message.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        # Текст анкеты для тебя
        admin_text = (
            f"📩 **Новая заявка в клан!**\n\n"
            f"👤 Ник: `{data.get('nick')}`\n"
            f"🎂 Возраст: {data.get('age')}\n"
            f"⏳ Часов: {data.get('hours')}\n"
            f"🏆 Поинтов: {data.get('points')}\n\n"
            f"🔗 Ссылка: [{user_name}](tg://user?id={user_id})"
        )

        # Создаем кнопки действия
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"adm_accept_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_decline_{user_id}")
            ]
        ])

        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=markup)
        await message.answer("✅ Твоя заявка отправлена! Ожидай решения лидера.")

    except Exception as e:
        print(f"Ошибка в данных: {e}")

# Обработка нажатий на кнопки Принять/Отклонить
@dp.callback_query(F.data.startswith("adm_"))
async def process_decision(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    player_id = int(callback.data.split("_")[2])

    if action == "accept":
        await bot.send_message(player_id, "🎉 Поздравляем! Ты принят в клан. Лидер скоро свяжется с тобой!")
        await callback.message.edit_text(callback.message.text + "\n\nСтатус: ✅ **ПРИНЯТ**", parse_mode="Markdown")
    else:
        await bot.send_message(player_id, "😔 К сожалению, твоя заявка в клан отклонена.")
        await callback.message.edit_text(callback.message.text + "\n\nСтатус: ❌ **ОТКЛОНЕН**", parse_mode="Markdown")
    
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
