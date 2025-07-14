try:
    from .pdf_parser import pdf_to_text, extract_words_from_pdf, get_word_statistics
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("⚠️ pdf_parser недоступен - установите pdfminer.six")

try:
    from .skills_extractor import skills_extractor, SkillsExtractor
    SKILLS_EXTRACTOR_AVAILABLE = True
except ImportError:
    SKILLS_EXTRACTOR_AVAILABLE = False
    print("⚠️ skills_extractor недоступен")

__all__ = []
if PDF_PARSER_AVAILABLE:
    __all__.extend(['pdf_to_text', 'extract_words_from_pdf', 'get_word_statistics'])
if SKILLS_EXTRACTOR_AVAILABLE:
    __all__.extend(['skills_extractor', 'SkillsExtractor'])
