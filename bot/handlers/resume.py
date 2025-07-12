# bot/handlers/resume.py

import uuid
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message
from aiogram import Bot

router = Router()

# Папка для временного хранения PDF
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)


@router.message(F.document.mime_type == "application/pdf")
async def resume_handler(message: Message, bot: Bot) -> None:
    """
    Принимает PDF-файл и сохраняет его во временную папку,
    после чего подтверждает приём резюме.
    """
    if not message.document:
        await message.answer("❌ Не удалось получить документ.")
        return
        
    # Генерируем уникальное имя, чтобы не было коллизий
    tmp_path = TMP_DIR / f"{uuid.uuid4()}.pdf"
    # Сохраняем PDF в tmp/
    await bot.download(message.document, destination=tmp_path)
    # Подтверждаем получение
    await message.answer(
        "📄 Резюме получено и сохранено! "
        "В ближайшее время начну его обработку."
    )
