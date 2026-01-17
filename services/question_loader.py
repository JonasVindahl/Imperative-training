import json
import os
from typing import Dict, List, Optional


class QuestionLoader:
    """Service for loading and managing questions from JSON files"""

    def __init__(self, questions_dir: str):
        self.questions_dir = questions_dir
        self._questions_cache = {}

    def load_all_questions(self) -> Dict[str, List[Dict]]:
        """
        Load all questions from JSON files

        Returns:
            Dictionary mapping category -> list of questions
        """
        if self._questions_cache:
            return self._questions_cache

        categories = [
            'memory_management',
            'integer_division',
            'strings',
            'structs',
            'pointers',
            'recursion',
            'control_flow',
            'file_io',
            'fill_blanks',
            'drag_drop',
            'recursive_trace',
            'programming_tasks'
        ]

        questions = {}
        for category in categories:
            questions[category] = self.load_category(category)

        self._questions_cache = questions
        return questions

    def load_category(self, category: str) -> List[Dict]:
        """
        Load questions for a specific category

        Args:
            category: Category name (e.g., 'memory_management')

        Returns:
            List of question dictionaries
        """
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

    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """
        Get a specific question by ID

        Args:
            question_id: Question identifier

        Returns:
            Question dictionary or None if not found
        """
        all_questions = self.load_all_questions()

        for category, questions in all_questions.items():
            for question in questions:
                if question.get('id') == question_id:
                    return question

        return None

    def get_questions_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get questions for a specific category

        Args:
            category: Category name
            limit: Optional limit on number of questions

        Returns:
            List of questions
        """
        questions = self.load_category(category)

        if limit:
            return questions[:limit]

        return questions

    def get_random_questions(self, category: str, count: int) -> List[Dict]:
        """
        Get random questions from a category

        Args:
            category: Category name
            count: Number of questions to return

        Returns:
            List of random questions
        """
        import random
        questions = self.load_category(category)
        unique_questions = list({q.get('id'): q for q in questions}.values())

        if len(unique_questions) <= count:
            return unique_questions

        return random.sample(unique_questions, count)

    def reload_questions(self):
        """Force reload of all questions from files"""
        self._questions_cache = {}
        return self.load_all_questions()
