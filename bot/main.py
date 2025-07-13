# bot/main.py
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from bot.env import TG_TOKEN

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем роутеры
from bot.handlers.resume import router as resume_router
from bot.handlers.callbacks import router as callbacks_router
from bot.keyboard import get_start_keyboard

# Создаём экземпляры бота и диспетчера
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Подключаем маршруты
logger.info("Подключаю роутеры...")
dp.include_router(callbacks_router)
logger.info("✅ Роутер callbacks подключен")
dp.include_router(resume_router)
logger.info("✅ Роутер резюме подключен")

@dp.message(CommandStart())
async def start_handler(message):
    logger.info(f"Команда /start от пользователя {message.from_user.id if message.from_user else 'Unknown'}")
    
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

@dp.message(F.text)
async def any_message_handler(message):
    """
    Обработчик для текстовых сообщений - показывает стартовое меню
    """
    logger.info(f"Получено текстовое сообщение от {message.from_user.id if message.from_user else 'Unknown'}")
    
    # Игнорируем команды
    if message.text.startswith('/'):
        logger.info("Игнорирую команду")
        return
    
    # Для любого другого текста показываем стартовое меню
    logger.info("Показываю стартовое меню")
    await message.answer(
        "👋 Добро пожаловать! Выберите действие:",
        reply_markup=get_start_keyboard()
    )

if __name__ == "__main__":
    logger.info("Запускаю бота...")
    dp.run_polling(bot)
