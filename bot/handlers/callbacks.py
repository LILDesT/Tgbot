# bot/handlers/callbacks.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboard import get_main_menu_keyboard

router = Router()

@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery) -> None:
    await callback.answer("🚀 Добро пожаловать!")
    await callback.message.edit_text(
        "👋 Привет! Я бот для поиска вакансий.\n\n"
        "📄 Пришли мне своё резюме в PDF — "
        "и я подберу для тебя подходящие вакансии.",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "upload_resume")
async def upload_resume_callback(callback: CallbackQuery) -> None:
    await callback.answer("📄 Готов к загрузке резюме!")
    await callback.message.edit_text(
        "📄 Пожалуйста, отправьте ваше резюме в формате PDF.\n\n"
        "Я проанализирую его и найду подходящие вакансии для вас.",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "statistics")
async def statistics_callback(callback: CallbackQuery) -> None:
    await callback.answer("📊 Статистика")
    await callback.message.edit_text(
        "📊 Статистика использования бота:\n\n"
        "• Обработано резюме: 0\n"
        "• Найдено вакансий: 0\n"
        "• Успешных трудоустройств: 0\n\n"
        "Функция находится в разработке!",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.answer("ℹ️ Помощь")
    await callback.message.edit_text(
        "ℹ️ Справка по использованию бота:\n\n"
        "📄 **Загрузить резюме** - отправьте PDF файл с вашим резюме\n"
        "🔍 **Найти вакансии** - поиск подходящих вакансий\n"
        "📊 **Статистика** - статистика использования\n\n"
        "Для начала работы загрузите ваше резюме!",
        reply_markup=get_main_menu_keyboard()
    ) 