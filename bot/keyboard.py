# bot/keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой /start
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Начать работу",
                    callback_data="start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Загрузить резюме",
                    callback_data="upload_resume"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help"
                )
            ]
        ]
    )
    return keyboard

def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Создает приветственную клавиатуру с кнопкой /start
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Запустить бота",
                    web_app=WebAppInfo(url="https://t.me/your_bot_username?start=welcome")
                )
            ]
        ]
    )
    return keyboard

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создает основное меню с кнопками
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Загрузить резюме",
                    callback_data="upload_resume"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Найти вакансии",
                    callback_data="search_jobs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help"
                )
            ]
        ]
    )
    return keyboard
