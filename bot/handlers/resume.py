# bot/handlers/resume.py

import uuid
import logging
from pathlib import Path
import datetime

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
import httpx
from aiogram.exceptions import TelegramBadRequest

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# Папка для временного хранения PDF
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

# Состояния для редактирования навыков
class ResumeStates(StatesGroup):
    editing_skills = State()
    waiting_new_skill = State()


@router.message(F.document.mime_type == "application/pdf")
async def resume_handler(message: Message, bot: Bot, state: FSMContext) -> None:
    """
    Принимает PDF-файл, сохраняет его во временную папку,
    парсит и извлекает ключевые навыки.
    """
    logger.info("=" * 50)
    logger.info("НАЧАЛО ОБРАБОТКИ РЕЗЮМЕ (PDF)")
    logger.info(f"От пользователя: {message.from_user.id if message.from_user else 'Unknown'}")
    logger.info(f"Имя файла: {message.document.file_name if message.document else 'None'}")
    
    await process_resume(message, bot, state)


@router.message(F.document)
async def any_document_handler(message: Message, bot: Bot, state: FSMContext) -> None:
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
        await process_resume(message, bot, state)
    else:
        logger.info(f"❌ Не PDF файл: {message.document.mime_type}")
        await message.answer(
            "❌ Пожалуйста, отправьте файл в формате PDF.\n\n"
            f"Получен файл типа: {message.document.mime_type}"
        )


async def process_resume(message: Message, bot: Bot, state: FSMContext) -> None:
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
            skills_result = skills_extractor.extract_skills_from_pdf(str(tmp_path))
            logger.info(f"✅ Навыки извлечены: {len(skills_result) if skills_result else 0} источников")

            # Логируем результат анализа
            logger.info(f"Результат skills_extractor: {skills_result}")

            skills_set = set()
            # Если есть ключи skillner/keybert/dict — старый формат
            if any(k in skills_result for k in ("skillner", "keybert", "dict")):
                for key in ("skillner", "keybert"):
                    logger.info(f"Навыки из {key}: {skills_result.get(key, [])}")
                    skills_set.update(skills_result.get(key, []))
                dict_skills = skills_result.get("dict", {})
                logger.info(f"Навыки из dict: {dict_skills}")
                if isinstance(dict_skills, dict):
                    for cat_skills in dict_skills.values():
                        skills_set.update(cat_skills)
            else:
                # Новый формат: сразу категории
                for cat, cat_skills in skills_result.items():
                    logger.info(f"Навыки из {cat}: {cat_skills}")
                    if isinstance(cat_skills, list):
                        skills_set.update(cat_skills)
            skills_list = sorted(skills_set)
            logger.info(f"Общий итоговый список навыков: {skills_list}")

            # Fallback: если ничего не найдено, показываем отдельное сообщение
            if not skills_list:
                await processing_msg.edit_text(
                    "❗️ Не удалось автоматически извлечь навыки из резюме.\n"
                    "Проверьте, что файл содержит текст, а не только изображения, и попробуйте снова.\n"
                    "\nВы можете вручную добавить навыки, просто отправив их в ответ.",
                    parse_mode="HTML"
                )
                await state.update_data(user_skills=[])
                await state.set_state(ResumeStates.editing_skills)
                return

            # Сохраняем навыки в FSM
            await state.update_data(user_skills=skills_list)

            # Формируем сообщение для редактирования
            skills_text = "\n".join(f"• {s}" for s in skills_list) if skills_list else "(ничего не найдено)"
            edit_text = (
                "🔍 <b>Найденные навыки:</b>\n"
                f"{skills_text}\n\n"
                "<b>Используйте кнопки ниже для управления навыками:</b>\n"
                "➕ <b>Добавить навык</b> — добавить новый навык\n"
                "➖ <b>Удалить навык</b> — удалить из списка\n"
                "✅ <b>Готово</b> — подтвердить список\n"
                "🔍 <b>Найти вакансии</b> — подобрать вакансии по навыкам"
            )
            await processing_msg.edit_text(edit_text, parse_mode="HTML", reply_markup=get_skills_keyboard(skills_list))
            await state.set_state(ResumeStates.editing_skills)
            return  # Переходим к ручному редактированию, не отправляем старый ответ
            
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

VACANCIES_PER_PAGE = 5
VACANCIES_FETCH_LIMIT = 50

async def search_hh_vacancies(skills, area=113, per_page=VACANCIES_FETCH_LIMIT, page=0):
    # skills может быть либо списком, либо словарём по категориям
    # Попробуем получить категории, если это словарь
    if isinstance(skills, dict):
        # Приоритет: языки программирования > инструменты > фреймворки
        for cat in ["programming_languages", "tools_technologies", "frameworks_libraries"]:
            if cat in skills and skills[cat]:
                query_skills = skills[cat][:2]
                break
        else:
            # Если ничего из приоритетного нет — берём любые навыки
            all_skills = []
            for v in skills.values():
                all_skills.extend(v)
            query_skills = all_skills[:2]
    else:
        # Если skills — просто список
        query_skills = skills[:2] if skills else []
    query = " ".join(query_skills)
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "area": area,
        "per_page": per_page,
        "page": 0,  # всегда только первую страницу
        "order_by": "relevance"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("items", []), data.get("pages", 1)

async def send_hh_vacancies(message_or_callback, state: FSMContext, page=0):
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    logger.info(f"Навыки для поиска: {skills}")
    user_skills = [s.lower() for s in skills] if isinstance(skills, list) else [s.lower() for v in skills.values() for s in v]
    # Получаем вакансии только при первом запросе, потом используем из FSM
    if page == 0 or not data.get("sorted_vacancies"):
        try:
            vacancies, _ = await search_hh_vacancies(skills, per_page=VACANCIES_FETCH_LIMIT)
            logger.info(f"Вакансии с hh.ru: {vacancies}")
        except Exception as e:
            logger.error(f"Ошибка при запросе к hh.ru: {e}")
            await message_or_callback.answer("Ошибка при поиске вакансий. Попробуйте позже.")
            return
        if not vacancies:
            await message_or_callback.answer("Вакансии по вашим навыкам не найдены на hh.ru. Попробуйте изменить или добавить навыки.")
            return
        def count_and_list_matches(vac):
            text = (vac.get("name", "") + " " +
                    (vac.get("snippet", {}).get("requirement", "") or "") + " " +
                    (vac.get("snippet", {}).get("responsibility", "") or "")
            ).lower()
            matched = [skill for skill in user_skills if skill in text]
            return len(matched), matched
        # Сортируем и сохраняем совпавшие навыки
        vac_with_matches = []
        for v in vacancies:
            count, matched = count_and_list_matches(v)
            v["_match_count"] = count
            v["_matched_skills"] = matched
            vac_with_matches.append(v)
        vac_with_matches.sort(key=lambda v: v["_match_count"], reverse=True)
        await state.update_data(sorted_vacancies=vac_with_matches, hh_page=page)
    else:
        vac_with_matches = data["sorted_vacancies"]
    # Пагинация по 5 вакансий
    start = page * VACANCIES_PER_PAGE
    end = start + VACANCIES_PER_PAGE
    page_vacancies = vac_with_matches[start:end]
    if not page_vacancies:
        await message_or_callback.answer("Больше вакансий не найдено.")
        return
    total_pages = (len(vac_with_matches) + VACANCIES_PER_PAGE - 1) // VACANCIES_PER_PAGE
    msg = f"<b>Топ вакансий на hh.ru по вашим навыкам (стр. {page+1}/{total_pages}):</b>\n\n"
    for v in page_vacancies:
        name = v.get("name", "(без названия)")
        employer = v.get("employer", {}).get("name", "")
        url = v.get("alternate_url", "")
        salary = v.get("salary")
        snippet = v.get("snippet", {})
        snippet_text = snippet.get("responsibility") or snippet.get("requirement") or ""
        published_at = v.get("published_at")
        published_str = ""
        if published_at:
            try:
                dt = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                published_str = dt.strftime("%d.%m.%Y")
            except Exception:
                published_str = published_at[:10]
        if snippet_text:
            snippet_text = snippet_text.replace('<highlighttext>', '<b>').replace('</highlighttext>', '</b>')
        if salary:
            if salary.get("from") and salary.get("to"):
                salary_str = f"{salary['from']}–{salary['to']} {salary.get('currency', '')}"
            elif salary.get("from"):
                salary_str = f"от {salary['from']} {salary.get('currency', '')}"
            elif salary.get("to"):
                salary_str = f"до {salary['to']} {salary.get('currency', '')}"
            else:
                salary_str = "не указана"
        else:
            salary_str = "не указана"
        match_count = v.get("_match_count", 0)
        matched_skills = v.get("_matched_skills", [])
        msg += f"<b>{name}</b>\n"
        if employer:
            msg += f"Компания: {employer}\n"
        if published_str:
            msg += f"🗓️ Дата публикации: {published_str}\n"
        msg += f"Зарплата: {salary_str}\n"
        msg += f"Совпадений по навыкам: <b>{match_count}</b>\n"
        if matched_skills:
            msg += f"<i>Совпавшие навыки: {', '.join(matched_skills)}</i>\n"
        if snippet_text:
            msg += f"<i>{snippet_text}</i>\n"
        msg += f"<a href='{url}'>Открыть вакансию</a>\n\n"
    # Кнопка 'Показать ещё', если есть следующая страница
    keyboard = None
    if end < len(vac_with_matches):
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="Показать ещё", callback_data=f"more_jobs:{page+1}")]]
        )
    try:
        await message_or_callback.answer(msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при отправке вакансий: {e}")
        await message_or_callback.answer("Ошибка при отправке вакансий. Попробуйте позже.")
    await state.update_data(hh_page=page)

@router.callback_query(lambda c: c.data == "search_jobs", ResumeStates.editing_skills)
async def search_jobs_handler(callback: types.CallbackQuery, state: FSMContext):
    logger.info("НАЖАТА КНОПКА ПОИСКА ВАКАНСИЙ")
    await callback.answer("Ищу вакансии на hh.ru по вашим навыкам...", show_alert=False)
    await send_hh_vacancies(callback.message, state, page=0)

@router.callback_query(lambda c: c.data and c.data.startswith("more_jobs:"), ResumeStates.editing_skills)
async def more_jobs_handler(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split(":", 1)[1])
    await callback.answer()
    await send_hh_vacancies(callback.message, state, page=page)

def get_skills_keyboard(skills):
    keyboard = []
    if skills:
        keyboard.append([
            InlineKeyboardButton(text="➖ Удалить навык", callback_data="choose_del_skill"),
        ])
    keyboard.append([
        InlineKeyboardButton(text="➕ Добавить навык", callback_data="add_skill"),
        InlineKeyboardButton(text="✅ Готово", callback_data="done_skills"),
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔍 Найти вакансии", callback_data="search_jobs"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора навыка для удаления

def get_del_skill_keyboard(skills):
    keyboard = []
    for skill in skills:
        keyboard.append([
            InlineKeyboardButton(text=f"❌ {skill}", callback_data=f"del_skill:{skill}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_skills")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_skills_list(skills):
    if not skills:
        return "<i>Навыков нет</i>"
    return (
        "📝 <b>Ваши навыки:</b>\n"
        "───────────────\n" +
        "\n".join(f"• {s}" for s in skills) +
        "\n───────────────"
    )

@router.message(ResumeStates.editing_skills, F.text.regexp(r"^/del "))
async def delete_skill_handler(message: Message, state: FSMContext):
    skill_to_del = (message.text[5:].strip() if message.text else "")
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    if skill_to_del in skills:
        skills.remove(skill_to_del)
        await state.update_data(user_skills=skills)
        await message.answer(f"❌ Навык <b>{skill_to_del}</b> удалён.", parse_mode="HTML")
    else:
        await message.answer(f"Навык <b>{skill_to_del}</b> не найден в списке.", parse_mode="HTML")
    # Показываем обновлённый список с кнопками
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    await message.answer(format_skills_list(skills), parse_mode="HTML", reply_markup=get_skills_keyboard(skills))

@router.message(ResumeStates.editing_skills, F.text.regexp(r"^/done$"))
async def done_skills_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    skills = data.get("user_skills", [])
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    await message.answer(f"✅ Итоговый список навыков сохранён:\n{skills_text}", parse_mode="HTML")
    # Не очищаем FSM и не выходим из режима редактирования
    # Пользователь остаётся в ResumeStates.editing_skills
    # Можно добавить подсказку:
    await message.answer(
        "Вы можете продолжить редактировать навыки, добавить новые, удалить лишние или сразу искать вакансии по кнопке ниже.",
        reply_markup=get_skills_keyboard(skills),
        parse_mode="HTML"
    )

@router.message(ResumeStates.editing_skills, F.text)
async def add_skill_handler(message: Message, state: FSMContext):
    new_skill = (message.text.strip() if message.text else "")
    if not new_skill or new_skill.startswith("/"):
        await message.answer("Пожалуйста, введите навык или используйте /done для завершения.")
        return
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    if new_skill in skills:
        await message.answer(f"Навык <b>{new_skill}</b> уже есть в списке.", parse_mode="HTML")
    else:
        skills.append(new_skill)
        await state.update_data(user_skills=skills)
        await message.answer(f"➕ Навык <b>{new_skill}</b> добавлен.", parse_mode="HTML")
    # Показываем обновлённый список с кнопками
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    await message.answer(format_skills_list(skills), parse_mode="HTML", reply_markup=get_skills_keyboard(skills))

# Инлайн-обработчик для удаления навыка по кнопке
@router.callback_query(lambda c: c.data and c.data.startswith("del_skill:"), ResumeStates.editing_skills)
async def inline_delete_skill_handler(callback: types.CallbackQuery, state: FSMContext):
    if not callback.data:
        await callback.answer("Ошибка: пустой callback.data", show_alert=True)
        return
    skill_to_del = callback.data.split(":", 1)[1]
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    if skill_to_del in skills:
        skills.remove(skill_to_del)
        await state.update_data(user_skills=skills)
        await callback.answer(f"Навык {skill_to_del} удалён", show_alert=False)
    else:
        await callback.answer(f"Навык {skill_to_del} не найден", show_alert=True)
    # Показываем обновлённый список с кнопками
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    if callback.message:
        try:
            await callback.message.edit_text(format_skills_list(skills), parse_mode="HTML", reply_markup=get_skills_keyboard(skills))
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise

# Инлайн-обработчик для добавления навыка по кнопке
@router.callback_query(lambda c: c.data == "add_skill", ResumeStates.editing_skills)
async def inline_add_skill_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await callback.message.answer("Введите новый навык для добавления:")
    await state.set_state(ResumeStates.waiting_new_skill)

@router.message(ResumeStates.waiting_new_skill, F.text)
async def add_skill_from_button_handler(message: Message, state: FSMContext):
    new_skill = (message.text.strip() if message.text else "")
    if not new_skill or new_skill.startswith("/"):
        await message.answer("Пожалуйста, введите навык или используйте /done для завершения.")
        return
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    if new_skill in skills:
        await message.answer(f"Навык <b>{new_skill}</b> уже есть в списке.", parse_mode="HTML")
    else:
        skills.append(new_skill)
        await state.update_data(user_skills=skills)
        await message.answer(f"➕ Навык <b>{new_skill}</b> добавлен.", parse_mode="HTML")
    # Показываем обновлённый список с кнопками
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    await message.answer(format_skills_list(skills), parse_mode="HTML", reply_markup=get_skills_keyboard(skills))
    await state.set_state(ResumeStates.editing_skills)
            
@router.callback_query(lambda c: c.data == "choose_del_skill", ResumeStates.editing_skills)
async def choose_del_skill_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    if not skills:
        await callback.answer("Нет навыков для удаления.", show_alert=True)
        return
    await callback.message.edit_text(
        "Выберите навык для удаления:",
        reply_markup=get_del_skill_keyboard(skills)
    )

@router.callback_query(lambda c: c.data == "back_to_skills", ResumeStates.editing_skills)
async def back_to_skills_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    skills = data.get("user_skills", []) or []
    await callback.message.edit_text(
        format_skills_list(skills),
        parse_mode="HTML",
        reply_markup=get_skills_keyboard(skills)
    )

@router.callback_query(lambda c: c.data == "done_skills", ResumeStates.editing_skills)
async def done_skills_button_handler(callback: types.CallbackQuery, state: FSMContext):
    # Просто вызываем done_skills_handler как если бы пользователь отправил /done
    data = await state.get_data()
    skills = data.get("user_skills", [])
    skills_text = "\n".join(f"• {s}" for s in skills) if skills else "(ничего не осталось)"
    await callback.message.answer(f"✅ Итоговый список навыков сохранён:\n{skills_text}", parse_mode="HTML")
    await callback.message.answer(
        "Вы можете продолжить редактировать навыки, добавить новые, удалить лишние или сразу искать вакансии по кнопке ниже.",
        reply_markup=get_skills_keyboard(skills),
        parse_mode="HTML"
    )
    await callback.answer("Навыки подтверждены!")
    # Остаёмся в режиме редактирования
            