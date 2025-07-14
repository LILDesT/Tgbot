from pdfminer.high_level import extract_text
import re

def pdf_to_text(path: str) -> str:
    try:
        raw = extract_text(path)
        if not raw:
            return ""
        cleaned = re.sub(r'\s+', ' ', raw)
        cleaned = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', cleaned)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()
    except Exception as e:
        print(f"Ошибка при обработке PDF файла {path}: {e}")
        return ""

def extract_words_from_pdf(path: str) -> list:
    text = pdf_to_text(path)
    if not text:
        return []
    words = re.findall(r'\b\w+\b', text.lower())
    words = [word for word in words if len(word) >= 2]
    return words

def get_word_statistics(path: str) -> dict:
    words = extract_words_from_pdf(path)
    if not words:
        return {
            'total_words': 0,
            'unique_words': 0,
            'word_frequency': {},
            'most_common_words': []
        }
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return {
        'total_words': len(words),
        'unique_words': len(word_freq),
        'word_frequency': word_freq,
        'most_common_words': sorted_words[:20]
    }