import json
import os
from typing import Dict, List, Optional


class QuestionLoader:
    """Service for loading and managing questions from JSON files.

    Supports both the new per-exam subdirectory layout:
        questions/<exam_id>/<category>.json

    And falls back to the legacy flat layout:
        questions/<category>.json
    """

    def __init__(self, questions_dir: str):
        self.questions_dir = questions_dir
        self._questions_cache = {}

    def _resolve_category_path(self, exam_id: str, category: str) -> str:
        """Resolve the file path for a category, trying exam subdir first, then flat."""
        # Try per-exam subdirectory first
        exam_path = os.path.join(self.questions_dir, exam_id, f'{category}.json')
        if os.path.exists(exam_path):
            return exam_path

        # Fallback to flat layout (backwards compat)
        flat_path = os.path.join(self.questions_dir, f'{category}.json')
        if os.path.exists(flat_path):
            return flat_path

        return exam_path  # Return the expected path even if missing, for error messages

    def load_all_questions(self, exam_id: str = None, categories: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Load all questions for an exam.

        Args:
            exam_id: Exam identifier (subfolder name). If None, uses legacy flat layout.
            categories: List of category IDs to load. If None, auto-discovers from exam dir.

        Returns:
            Dictionary mapping category -> list of questions
        """
        cache_key = exam_id or '__legacy__'
        if cache_key in self._questions_cache:
            return self._questions_cache[cache_key]

        if categories is None:
            categories = self._discover_categories(exam_id)

        questions = {}
        for category in categories:
            loaded = self.load_category(category, exam_id=exam_id)
            if loaded:
                questions[category] = loaded

        self._questions_cache[cache_key] = questions
        return questions

    def _discover_categories(self, exam_id: str = None) -> List[str]:
        """Auto-discover categories by scanning JSON files in the exam directory."""
        if exam_id:
            scan_dir = os.path.join(self.questions_dir, exam_id)
        else:
            scan_dir = self.questions_dir

        if not os.path.isdir(scan_dir):
            return []

        categories = []
        for filename in sorted(os.listdir(scan_dir)):
            if filename.endswith('.json'):
                categories.append(filename[:-5])  # Strip .json
        return categories

    def load_category(self, category: str, exam_id: str = None) -> List[Dict]:
        """
        Load questions for a specific category.

        Args:
            category: Category name (e.g., 'number_theory')
            exam_id: Exam identifier for per-exam subdirectory lookup

        Returns:
            List of question dictionaries
        """
        if exam_id:
            file_path = self._resolve_category_path(exam_id, category)
        else:
            file_path = os.path.join(self.questions_dir, f'{category}.json')

        if not os.path.exists(file_path):
            print(f"Warning: Question file not found: {file_path}")
            return []

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('questions', [])
        except json.JSONDecodeError as e:
            print(f"Error parsing {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def get_question_by_id(self, question_id: str, exam_id: str = None, categories: List[str] = None) -> Optional[Dict]:
        """
        Get a specific question by ID.

        Args:
            question_id: Question identifier
            exam_id: Exam to search within
            categories: Categories to search (if None, searches all)

        Returns:
            Question dictionary or None if not found
        """
        all_questions = self.load_all_questions(exam_id=exam_id, categories=categories)

        for category, questions in all_questions.items():
            for question in questions:
                if question.get('id') == question_id:
                    return question

        return None

    def get_questions_by_category(self, category: str, exam_id: str = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get questions for a specific category.

        Args:
            category: Category name
            exam_id: Exam identifier
            limit: Optional limit on number of questions

        Returns:
            List of questions
        """
        questions = self.load_category(category, exam_id=exam_id)

        if limit:
            return questions[:limit]

        return questions

    def get_random_questions(self, category: str, count: int, exam_id: str = None) -> List[Dict]:
        """
        Get random questions from a category.

        Args:
            category: Category name
            count: Number of questions to return
            exam_id: Exam identifier

        Returns:
            List of random questions
        """
        import random
        questions = self.load_category(category, exam_id=exam_id)
        unique_questions = list({q.get('id'): q for q in questions}.values())

        if len(unique_questions) <= count:
            return unique_questions

        return random.sample(unique_questions, count)

    def reload_questions(self, exam_id: str = None):
        """Force reload of questions from files"""
        if exam_id:
            self._questions_cache.pop(exam_id, None)
        else:
            self._questions_cache = {}
