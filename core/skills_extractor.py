import re
from typing import List, Dict

try:
    from .pdf_parser import extract_words_from_pdf
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("⚠️ pdf_parser недоступен - PDF анализ будет ограничен")

class SkillsExtractor:
    def __init__(self):
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
                'photoshop', 'illustrator', 'excel', 'powerpoint', 'word', 'notion', 'trello', 
                'microsoft office', 'microsoft excel', 'microsoft powerpoint', 'microsoft word', 
                'microsoft teams', 'microsoft outlook', 'microsoft onedrive', 'microsoft onenote', 
                'MS Word/Excel', 'MS', 'Word', 'Excel', 'PowerPoint', 'Outlook', 'OneDrive', 'OneNote',
            },
            'methodologies': {
                'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'lean',
                'six sigma', 'prince2', 'pmp'
            },
            'soft_skills': {
                'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                'time management', 'project management', 'mentoring', 'presentation', 'negotiation',
                'analytical skills', 'creativity', 'adaptability', 'stress management', 'stress resistance','logical thinking'
            }
        }
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
        text_lower = text.lower()
        found_skills = {category: [] for category in self.skills_dict.keys()}
        for category, skills in self.skills_dict.items():
            for skill in skills:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                cleaned_skill = re.sub(r'[^\w\s\-\.]', '', match).strip()
                cleaned_skill = re.sub(r'^[\-\s]+|[\-\s]+$', '', cleaned_skill)
                if cleaned_skill and len(cleaned_skill) > 2:
                    category = self._categorize_skill(cleaned_skill)
                    if category and cleaned_skill not in found_skills[category]:
                        found_skills[category].append(cleaned_skill)
        return {k: v for k, v in found_skills.items() if v}

    def _categorize_skill(self, skill: str) -> str:
        skill_lower = skill.lower()
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
        return 'tools_technologies'

    def extract_skills_from_pdf(self, pdf_path: str) -> Dict[str, List[str]]:
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

    def get_top_skills(self, skills: Dict[str, List[str]], top_n: int = 10) -> List[str]:
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        unique_skills = list(set(all_skills))
        return unique_skills[:top_n]

skills_extractor = SkillsExtractor() 