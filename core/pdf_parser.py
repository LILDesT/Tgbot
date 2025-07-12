from pdfminer.high_level import extract_text
import re

def pdf_to_text(path: str) -> str:
    raw = extract_text(path)
    # убираем переносы страниц/два пробела …
    cleaned = re.sub(r'\s{2,}', ' ', raw)
    return cleaned.strip()