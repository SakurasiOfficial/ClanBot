import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКИ ---
TOKEN = "8256898976:AAEBnI-SQf4zK_6-eUjY4IlFY0C1UPhB0CY"
ADMIN_ID = 5831918933  # Твой ID, куда будут падать заявки
WEBAPP_URL = "https://sakurasiofficial.github.io/ClanBot/" # Ссылка на твой HTML
# -----------------

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Приветствие при команде /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Можешь дописать здесь свой текст
    welcome_text = (
        "Привет! Добро пожаловать в систему подачи заявок клана.\n"
        "Чтобы вступить к нам, нажми на кнопку ниже или используй /application."
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    
    await message.answer(welcome_text, reply_markup=markup)

# Команда /application (дублирует открытие приложения)
@dp.message(Command("application"))
async def open_app(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть анкету", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Нажми кнопку, чтобы заполнить данные:", reply_markup=markup)

# Обработка данных, пришедших из Mini App
@dp.message(lambda message: message.web_app_data)
async def handle_webapp_data(message: types.Message):
    # Распаковываем JSON данные из веб-приложения
    try:
        data = json.loads(message.web_app_data.data)
        
        # Формируем текст для админа (для тебя)
        admin_text = (
            f"📩 **Новая заявка в клан!**\n\n"
            f"👤 **Ник:** `{data.get('nick')}`\n"
            f"🎂 **Возраст:** {data.get('age')}\n"
            f"⏳ **Часов:** {data.get('hours')}\n"
            f"🏆 **Поинтов:** {data.get('points')}\n\n"
            f"🔗 **Профиль в TG:** @{message.from_user.username if message.from_user.username else 'скрыт'}\n"
            f"🆔 **ID пользователя:** `{message.from_user.id}`"
        )
        
        # Отправляем заявку тебе
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        
        # Отвечаем пользователю
        await message.answer("✅ Твоя заявка успешно отправлена! Лидер клана рассмотрит её в ближайшее время.")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке данных: {e}")
        await message.answer("Произошла ошибка при отправке заявки. Попробуй еще раз.")

# Запуск бота
async def main():
    print("Бот запущен и готов принимать заявки!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")