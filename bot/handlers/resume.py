# bot/handlers/resume.py

import uuid
import asyncio
import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message
from aiogram import Bot

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# Папка для временного хранения PDF
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)


@router.message(F.document.mime_type == "application/pdf")
async def resume_handler(message: Message, bot: Bot) -> None:
    """
    Принимает PDF-файл, сохраняет его во временную папку,
    парсит и извлекает ключевые навыки.
    """
    logger.info("=" * 50)
    logger.info("НАЧАЛО ОБРАБОТКИ РЕЗЮМЕ (PDF)")
    logger.info(f"От пользователя: {message.from_user.id if message.from_user else 'Unknown'}")
    logger.info(f"Имя файла: {message.document.file_name if message.document else 'None'}")
    
    await process_resume(message, bot)


@router.message(F.document)
async def any_document_handler(message: Message, bot: Bot) -> None:
    """
    Обработчик для всех документов - проверяет, является ли PDF
    """
    logger.info("=" * 50)
    logger.info("ОБРАБОТЧИК ВСЕХ ДОКУМЕНТОВ")
    logger.info(f"От пользователя: {message.from_user.id if message.from_user else 'Unknown'}")
    logger.info(f"Имя файла: {message.document.file_name if message.document else 'None'}")
    logger.info(f"MIME тип: {message.document.mime_type if message.document else 'None'}")
    
    if not message.document:
        await message.answer("❌ Не удалось получить документ.")
        return
    
    # Проверяем, является ли файл PDF
    if message.document.mime_type == "application/pdf":
        logger.info("✅ Это PDF файл, обрабатываю как резюме")
        await process_resume(message, bot)
    else:
        logger.info(f"❌ Не PDF файл: {message.document.mime_type}")
        await message.answer(
            "❌ Пожалуйста, отправьте файл в формате PDF.\n\n"
            f"Получен файл типа: {message.document.mime_type}"
        )


async def process_resume(message: Message, bot: Bot) -> None:
    """
    Основная логика обработки резюме
    """
    if not message.document:
        logger.error("Документ не найден в сообщении")
        await message.answer("❌ Не удалось получить документ.")
        return
    
    logger.info(f"Получен PDF документ: {message.document.file_name}")
    
    # Отправляем сообщение о начале обработки
    try:
        processing_msg = await message.answer(
            "📄 Резюме получено! Начинаю обработку..."
        )
        logger.info("✅ Отправлено сообщение о начале обработки")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке первого сообщения: {e}")
        return
        
    # Генерируем уникальное имя, чтобы не было коллизий
    tmp_path = TMP_DIR / f"{uuid.uuid4()}.pdf"
    logger.info(f"Временный путь: {tmp_path}")
    
    try:
        # Сохраняем PDF в tmp/
        logger.info("Начинаю загрузку PDF файла...")
        await bot.download(message.document, destination=tmp_path)
        logger.info("✅ PDF файл успешно загружен")
        
        # Проверяем, что файл существует и не пустой
        if not tmp_path.exists():
            raise FileNotFoundError("Файл не был сохранен")
        
        file_size = tmp_path.stat().st_size
        logger.info(f"Размер файла: {file_size} байт")
        
        if file_size == 0:
            raise ValueError("Файл пустой")
        
        # Обновляем сообщение
        try:
            await processing_msg.edit_text(
                "📄 Резюме сохранено! Извлекаю ключевые навыки..."
            )
            logger.info("✅ Обновлено сообщение о сохранении")
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении сообщения: {e}")
        
        logger.info("Начинаю извлечение навыков...")
        
        # Пробуем импортировать и использовать skills_extractor
        try:
            logger.info("Импортирую skills_extractor...")
            from core.skills_extractor import skills_extractor
            logger.info("✅ Модуль skills_extractor успешно импортирован")
            
            # Извлекаем навыки из PDF
            logger.info("Вызываю extract_skills_from_pdf...")
            skills = skills_extractor.extract_skills_from_pdf(str(tmp_path))
            logger.info(f"✅ Навыки извлечены: {len(skills) if skills else 0} категорий")
            
            # Формируем ответ
            if skills:
                logger.info("Формирую ответ с найденными навыками...")
                # Получаем все навыки
                all_skills = skills_extractor.get_top_skills(skills, 1000)  # Получаем все навыки
                
                # Формируем детальный список всех навыков по категориям
                skills_details = []
                category_names = {
                    'programming_languages': '💻 Языки программирования',
                    'frameworks_libraries': '🔧 Фреймворки и библиотеки',
                    'databases': '🗄️ Базы данных',
                    'cloud_platforms': '☁️ Облачные платформы',
                    'tools_technologies': '🛠️ Инструменты и технологии',
                    'methodologies': '📋 Методологии',
                    'soft_skills': '🤝 Soft skills'
                }
                
                for category, skill_list in skills.items():
                    if skill_list:
                        category_name = category_names.get(category, category)
                        skills_details.append(f"\n{category_name}:")
                        for skill in skill_list:
                            skills_details.append(f"  • {skill}")
                
                response_text = (
                    "✅ Резюме успешно обработано!\n\n"
                    "🔍 **Все найденные ключевые навыки:**\n"
                    f"{''.join(skills_details)}\n\n"
                    f"📊 **Статистика:**\n"
                    f"• Всего навыков: {len(all_skills)}\n"
                    f"• Категорий: {len(skills)}\n\n"
                    "💡 Теперь я могу подобрать для вас подходящие вакансии на основе этих навыков!"
                )
                
                logger.info(f"Сформирован ответ длиной {len(response_text)} символов")
                
            else:
                logger.warning("Навыки не найдены, формирую ответ об ошибке...")
                response_text = (
                    "✅ Резюме успешно обработано!\n\n"
                    "⚠️ К сожалению, не удалось извлечь ключевые навыки из резюме.\n"
                    "Возможно, резюме содержит изображения или нестандартный формат.\n\n"
                    "💡 Попробуйте загрузить резюме в текстовом формате или убедитесь, "
                    "что текст в PDF доступен для копирования."
                )
            
        except ImportError as e:
            logger.error(f"❌ Ошибка импорта skills_extractor: {e}")
            response_text = (
                "✅ Резюме успешно получено и сохранено!\n\n"
                "⚠️ Модуль анализа навыков временно недоступен.\n"
                "Файл сохранен для дальнейшей обработки.\n\n"
                "💡 Попробуйте позже или обратитесь к администратору."
            )
        
        # Отправляем результат
        logger.info("Отправляю результат пользователю...")
        try:
            await processing_msg.edit_text(response_text)
            logger.info("✅ Результат успешно отправлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке результата: {e}")
            # Пробуем отправить новое сообщение
            try:
                await message.answer(response_text)
                logger.info("✅ Результат отправлен новым сообщением")
            except Exception as e2:
                logger.error(f"❌ Ошибка при отправке нового сообщения: {e2}")
        
    except Exception as e:
        logger.error(f"❌ Общая ошибка при обработке резюме: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_text = (
            "❌ Произошла ошибка при обработке резюме.\n\n"
            f"Ошибка: {str(e)}\n\n"
            "💡 Убедитесь, что файл является корректным PDF документом."
        )
        
        try:
            await processing_msg.edit_text(error_text)
        except Exception as edit_error:
            logger.error(f"❌ Ошибка при отправке сообщения об ошибке: {edit_error}")
            try:
                await message.answer(error_text)
            except Exception as send_error:
                logger.error(f"❌ Критическая ошибка отправки: {send_error}")
        
    finally:
        # Удаляем временный файл
        try:
            if tmp_path.exists():
                tmp_path.unlink()
                logger.info("✅ Временный файл удален")
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении временного файла: {e}")
    
    logger.info("КОНЕЦ ОБРАБОТКИ РЕЗЮМЕ")
    logger.info("=" * 50)
            