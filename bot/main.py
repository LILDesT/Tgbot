# bot/main.py
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from bot.handlers.resume import ResumeStates
from bot.handlers.resume import router as resume_router
from bot.handlers.callbacks import router as callbacks_router
from bot.keyboard import get_start_keyboard
from bot.env import TG_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

dp.include_router(callbacks_router)
logger.info("✅ Роутер callbacks подключен")
dp.include_router(resume_router)
logger.info("✅ Роутер резюме подключен")

@dp.message(CommandStart())
async def start_handler(message):
    logger.info(f"Команда /start от пользователя {message.from_user.id if message.from_user else 'Unknown'}")
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if args and args[0] == "welcome":
        await message.answer(
            "🎉 Добро пожаловать! Я бот для поиска вакансий.\n\n"
            "📄 Пришли мне своё резюме в PDF — "
            "и я подберу для тебя подходящие вакансии.",
            reply_markup=get_start_keyboard()
        )
    else:
        await message.answer(
            "👋 Привет! Пришли мне своё резюме в PDF — "
            "и я подберу для тебя подходящие вакансии.",
            reply_markup=get_start_keyboard()
        )

@dp.message(F.text, ~StateFilter(ResumeStates.editing_skills), ~StateFilter(ResumeStates.waiting_new_skill))
async def any_message_handler(message):
    logger.info(f"Получено текстовое сообщение от {message.from_user.id if message.from_user else 'Unknown'}")
    if message.text.startswith('/'):
        logger.info("Игнорирую команду")
        return
    await message.answer(
        "👋 Добро пожаловать! Выберите действие:",
        reply_markup=get_start_keyboard()
    )
