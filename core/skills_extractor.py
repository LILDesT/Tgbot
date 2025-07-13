import re
from typing import List, Dict, Set

# Пробуем импортировать pdf_parser, но не падаем если его нет
try:
    from .pdf_parser import extract_words_from_pdf
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("⚠️ pdf_parser недоступен - PDF анализ будет ограничен")

class SkillsExtractor:
    """
    Класс для извлечения ключевых навыков из резюме
    """
    
    def __init__(self):
        # Словарь навыков по категориям
        self.skills_dict = {
            'programming_languages': {
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell'
            },
            'frameworks_libraries': {
                'django', 'flask', 'fastapi', 'spring', 'react', 'vue', 'angular', 'node.js', 'express',
                'laravel', 'rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'material-ui',
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn'
            },
            'databases': {
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle',
                'sql server', 'dynamodb', 'cassandra', 'neo4j', 'influxdb'
            },
            'cloud_platforms': {
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr', 'kubernetes',
                'docker', 'terraform', 'ansible', 'jenkins', 'gitlab', 'github actions'
            },
            'tools_technologies': {
                'git', 'svn', 'jira', 'confluence', 'slack', 'teams', 'zoom', 'figma', 'sketch',
                'photoshop', 'illustrator', 'excel', 'powerpoint', 'word', 'notion', 'trello'
            },
            'methodologies': {
                'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'lean',
                'six sigma', 'prince2', 'pmp'
            },
            'soft_skills': {
                'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                'time management', 'project management', 'mentoring', 'presentation', 'negotiation',
                'analytical skills', 'creativity', 'adaptability', 'stress management'
            }
        }
        
        # Дополнительные паттерны для поиска навыков
        self.skill_patterns = [
            r'\b(?:знаю|владею|опыт работы с|работал с|использую|применяю)\s+([^,\n]+)',
            r'\b(?:skills|навыки|технологии|инструменты|умею|умею использовать|key skills)\s*[:]\s*([^,\n]+)',
            r'\b(?:programming|development|технологии)\s*[:]\s*([^,\n]+)',
            r'\b(?:framework|library|библиотека)\s*[:]\s*([^,\n]+)',
            r'\b(?:database|база данных)\s*[:]\s*([^,\n]+)',
            r'\b(?:cloud|облачные технологии)\s*[:]\s*([^,\n]+)',
            r'\b(?:tool|инструмент)\s*[:]\s*([^,\n]+)',
        ]
    
    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Извлекает навыки из текста резюме
        
        Args:
            text (str): Текст резюме
            
        Returns:
            Dict[str, List[str]]: Словарь с навыками по категориям
        """
        text_lower = text.lower()
        found_skills = {category: [] for category in self.skills_dict.keys()}
        
        # Ищем навыки по словарю
        for category, skills in self.skills_dict.items():
            for skill in skills:
                # Ищем точное совпадение слова
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        # Ищем навыки по паттернам
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Очищаем найденный текст
                cleaned_skill = re.sub(r'[^\w\s\-\.]', '', match).strip()
                # Убираем лишние пробелы и дефисы в начале/конце
                cleaned_skill = re.sub(r'^[\-\s]+|[\-\s]+$', '', cleaned_skill)
                if cleaned_skill and len(cleaned_skill) > 2:
                    # Определяем категорию для найденного навыка
                    category = self._categorize_skill(cleaned_skill)
                    if category and cleaned_skill not in found_skills[category]:
                        found_skills[category].append(cleaned_skill)
        
        # Убираем пустые категории
        return {k: v for k, v in found_skills.items() if v}
    
    def _categorize_skill(self, skill: str) -> str:
        """
        Определяет категорию для навыка
        
        Args:
            skill (str): Навык
            
        Returns:
            str: Категория навыка
        """
        skill_lower = skill.lower()
        
        # Проверяем по ключевым словам
        if any(word in skill_lower for word in ['python', 'java', 'javascript', 'c++', 'php', 'ruby']):
            return 'programming_languages'
        elif any(word in skill_lower for word in ['django', 'flask', 'react', 'vue', 'angular', 'spring']):
            return 'frameworks_libraries'
        elif any(word in skill_lower for word in ['mysql', 'postgresql', 'mongodb', 'redis', 'database']):
            return 'databases'
        elif any(word in skill_lower for word in ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes']):
            return 'cloud_platforms'
        elif any(word in skill_lower for word in ['git', 'jira', 'jenkins', 'figma', 'excel']):
            return 'tools_technologies'
        elif any(word in skill_lower for word in ['agile', 'scrum', 'devops', 'ci/cd', 'project']):
            return 'methodologies'
        elif any(word in skill_lower for word in ['leadership', 'communication', 'teamwork', 'management']):
            return 'soft_skills'
        
        return 'tools_technologies'  # По умолчанию
    
    def extract_skills_from_pdf(self, pdf_path: str) -> Dict[str, List[str]]:
        """
        Извлекает навыки из PDF файла
        
        Args:
            pdf_path (str): Путь к PDF файлу
            
        Returns:
            Dict[str, List[str]]: Словарь с навыками по категориям
        """
        if not PDF_PARSER_AVAILABLE:
            print("❌ PDF парсер недоступен. Установите pdfminer.six: pip install pdfminer.six")
            return {}
        
        try:
            from .pdf_parser import pdf_to_text
            
            text = pdf_to_text(pdf_path)
            if not text:
                return {}
            
            return self.extract_skills_from_text(text)
            
        except Exception as e:
            print(f"❌ Ошибка при извлечении текста из PDF: {e}")
            return {}
    
    def get_skills_summary(self, skills: Dict[str, List[str]]) -> str:
        """
        Формирует краткое описание найденных навыков
        
        Args:
            skills (Dict[str, List[str]]): Словарь с навыками
            
        Returns:
            str: Краткое описание навыков
        """
        if not skills:
            return "Навыки не найдены в резюме."
        
        summary_parts = []
        
        category_names = {
            'programming_languages': 'Языки программирования',
            'frameworks_libraries': 'Фреймворки и библиотеки',
            'databases': 'Базы данных',
            'cloud_platforms': 'Облачные платформы',
            'tools_technologies': 'Инструменты и технологии',
            'methodologies': 'Методологии',
            'soft_skills': 'Soft skills'
        }
        
        for category, skill_list in skills.items():
            if skill_list:
                category_name = category_names.get(category, category)
                skills_str = ', '.join(skill_list[:5])  # Показываем первые 5 навыков
                if len(skill_list) > 5:
                    skills_str += f" и еще {len(skill_list) - 5}"
                summary_parts.append(f"• {category_name}: {skills_str}")
        
        return "\n".join(summary_parts)
    
    def get_top_skills(self, skills: Dict[str, List[str]], top_n: int = 10) -> List[str]:
        """
        Возвращает топ навыков
        
        Args:
            skills (Dict[str, List[str]]): Словарь с навыками
            top_n (int): Количество топ навыков
            
        Returns:
            List[str]: Список топ навыков
        """
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        
        # Убираем дубликаты и возвращаем топ
        unique_skills = list(set(all_skills))
        return unique_skills[:top_n]

# Создаем глобальный экземпляр
skills_extractor = SkillsExtractor() 