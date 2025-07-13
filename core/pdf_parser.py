from pdfminer.high_level import extract_text
import re

def pdf_to_text(path: str) -> str:
    """
    Извлекает весь текст из PDF файла и возвращает очищенный текст.
    
    Args:
        path (str): Путь к PDF файлу
        
    Returns:
        str: Очищенный текст из PDF
    """
    try:
        # Извлекаем сырой текст из PDF
        raw = extract_text(path)
        
        if not raw:
            return ""
        
        # Убираем лишние пробелы и переносы строк
        cleaned = re.sub(r'\s+', ' ', raw)
        
        # Убираем специальные символы, но оставляем буквы, цифры и основные знаки препинания
        cleaned = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', cleaned)
        
        # Убираем множественные пробелы
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        
        return cleaned.strip()
        
    except Exception as e:
        print(f"Ошибка при обработке PDF файла {path}: {e}")
        return ""

def extract_words_from_pdf(path: str) -> list:
    """
    Извлекает все слова из PDF файла.
    
    Args:
        path (str): Путь к PDF файлу
        
    Returns:
        list: Список всех слов из PDF
    """
    text = pdf_to_text(path)
    if not text:
        return []
    
    # Разбиваем текст на слова, убираем пустые строки
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Убираем слова длиной меньше 2 символов (обычно это артикли, предлоги и т.д.)
    words = [word for word in words if len(word) >= 2]
    
    return words

def get_word_statistics(path: str) -> dict:
    """
    Получает статистику по словам в PDF файле.
    
    Args:
        path (str): Путь к PDF файлу
        
    Returns:
        dict: Словарь со статистикой (общее количество слов, уникальные слова, частотность)
    """
    words = extract_words_from_pdf(path)
    
    if not words:
        return {
            'total_words': 0,
            'unique_words': 0,
            'word_frequency': {},
            'most_common_words': []
        }
    
    # Подсчитываем частотность слов
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Сортируем по частоте
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_words': len(words),
        'unique_words': len(word_freq),
        'word_frequency': word_freq,
        'most_common_words': sorted_words[:20]  # Топ-20 самых частых слов
    }