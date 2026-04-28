import json

from flask import session


class ExamService:
    """Service for managing exams/courses and the active exam selection"""

    def __init__(self, exams_file: str):
        self.exams_file = exams_file
        self._exams_cache = None

    def _load_exams(self) -> dict:
        if self._exams_cache:
            return self._exams_cache

        with open(self.exams_file) as f:
            data = json.load(f)

        self._exams_cache = data
        return data

    def get_all_exams(self) -> list[dict]:
        """Return list of all exam definitions"""
        data = self._load_exams()
        return data.get('exams', [])

    def get_exam(self, exam_id: str) -> dict | None:
        """Get a specific exam by ID"""
        for exam in self.get_all_exams():
            if exam['id'] == exam_id:
                return exam
        return None

    def get_default_exam_id(self) -> str:
        """Get the default exam ID from config"""
        data = self._load_exams()
        return data.get('default_exam', 'c_programming')

    def get_active_exam_id(self) -> str:
        """Get the currently active exam from session, or fall back to default"""
        return session.get('active_exam_id', self.get_default_exam_id())

    def set_active_exam(self, exam_id: str) -> bool:
        """Set the active exam in session. Returns False if exam_id is invalid."""
        exam = self.get_exam(exam_id)
        if not exam:
            return False
        session['active_exam_id'] = exam_id
        return True

    def get_active_exam(self) -> dict:
        """Get the full exam definition for the active exam"""
        exam_id = self.get_active_exam_id()
        exam = self.get_exam(exam_id)
        if not exam:
            # Fallback to default
            exam = self.get_exam(self.get_default_exam_id())
        return exam

    def get_categories_for_exam(self, exam_id: str) -> list[dict]:
        """Get category definitions for a specific exam"""
        exam = self.get_exam(exam_id)
        if not exam:
            return []
        return exam.get('categories', [])

    def get_category_ids_for_exam(self, exam_id: str) -> list[str]:
        """Get just the category ID strings for a specific exam"""
        return [cat['id'] for cat in self.get_categories_for_exam(exam_id)]

    def get_category_name(self, exam_id: str, category_id: str) -> str:
        """Get display name for a category"""
        for cat in self.get_categories_for_exam(exam_id):
            if cat['id'] == category_id:
                return cat['name']
        return category_id.replace('_', ' ').title()

    def reload(self):
        """Force reload exam config from file"""
        self._exams_cache = None
        self._load_exams()
