# bot/main.py
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from bot.env import TG_TOKEN

# Импортируем роутеры
from bot.handlers.resume import router as resume_router
from bot.handlers.callbacks import router as callbacks_router
from bot.keyboard import get_start_keyboard

# Создаём экземпляры бота и диспетчера
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Подключаем маршруты
dp.include_router(resume_router)
dp.include_router(callbacks_router)

@dp.message(CommandStart())
async def start_handler(message):
    # Получаем параметры команды /start
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args and args[0] == "welcome":
        # Если перешли по ссылке с параметром welcome
        await message.answer(
            "🎉 Добро пожаловать! Я бот для поиска вакансий.\n\n"
            "📄 Пришли мне своё резюме в PDF — "
            "и я подберу для тебя подходящие вакансии.",
            reply_markup=get_start_keyboard()
        )
    else:
        # Обычная команда /start
        await message.answer(
            "👋 Привет! Пришли мне своё резюме в PDF — "
            "и я подберу для тебя подходящие вакансии.",
            reply_markup=get_start_keyboard()
        )

@dp.message()
async def any_message_handler(message):
    """
    Обработчик для любого сообщения - показывает стартовое меню
    """
    # Игнорируем команды и документы
    if message.text and message.text.startswith('/'):
        return
    
    if message.document:
        return
    
    # Для любого другого текста показываем стартовое меню
    await message.answer(
        "👋 Добро пожаловать! Выберите действие:",
        reply_markup=get_start_keyboard()
    )

if __name__ == "__main__":
    dp.run_polling(bot)
