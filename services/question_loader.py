import json
import logging
import os
import random
import re

logger = logging.getLogger(__name__)

# Allow only conservative identifiers (letters, digits, underscore, dash)
# for exam ids and category names. This is the first line of defence against
# path-traversal — values that fail this check never even touch os.path.join.
_SAFE_ID = re.compile(r'^[a-zA-Z0-9_\-]+$')


class QuestionLoader:
    """Service for loading and managing questions from JSON files.

    Supports both the new per-exam subdirectory layout:
        questions/<exam_id>/<category>.json

    And falls back to the legacy flat layout:
        questions/<category>.json
    """

    def __init__(self, questions_dir: str):
        self.questions_dir = os.path.realpath(questions_dir)
        self._questions_cache: dict[str, dict[str, list[dict]]] = {}

    @staticmethod
    def _is_safe_id(value: str | None) -> bool:
        return bool(value) and bool(_SAFE_ID.match(value))

    def _resolve_category_path(self, exam_id: str | None, category: str) -> str | None:
        """Resolve the file path for a category, validating both ids first.

        Returns ``None`` when the requested ids are unsafe or resolve outside
        the configured questions directory.
        """
        if not self._is_safe_id(category):
            logger.warning('Rejecting unsafe category id: %r', category)
            return None
        if exam_id is not None and not self._is_safe_id(exam_id):
            logger.warning('Rejecting unsafe exam id: %r', exam_id)
            return None

        candidates = []
        if exam_id:
            candidates.append(os.path.join(self.questions_dir, exam_id, f'{category}.json'))
        # Fallback to flat legacy layout
        candidates.append(os.path.join(self.questions_dir, f'{category}.json'))

        for candidate in candidates:
            real = os.path.realpath(candidate)
            # Containment check: refuse paths outside the questions root
            if not real.startswith(self.questions_dir + os.sep) and real != self.questions_dir:
                logger.warning('Rejecting path outside questions dir: %s', real)
                continue
            if os.path.exists(real):
                return real

        # Nothing found, but the request was syntactically safe — return the
        # primary expected path so callers can produce useful error messages.
        primary = candidates[0]
        primary_real = os.path.realpath(primary)
        if primary_real.startswith(self.questions_dir + os.sep):
            return primary_real
        return None

    def load_all_questions(
        self,
        exam_id: str | None = None,
        categories: list[str] | None = None,
    ) -> dict[str, list[dict]]:
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

        questions: dict[str, list[dict]] = {}
        for category in categories:
            loaded = self.load_category(category, exam_id=exam_id)
            if loaded:
                questions[category] = loaded

        self._questions_cache[cache_key] = questions
        return questions

    def _discover_categories(self, exam_id: str | None = None) -> list[str]:
        """Auto-discover categories by scanning JSON files in the exam directory."""
        if exam_id is not None and not self._is_safe_id(exam_id):
            logger.warning('Rejecting unsafe exam id during discovery: %r', exam_id)
            return []

        if exam_id:
            scan_dir = os.path.join(self.questions_dir, exam_id)
        else:
            scan_dir = self.questions_dir

        scan_real = os.path.realpath(scan_dir)
        if not scan_real.startswith(self.questions_dir):
            return []

        if not os.path.isdir(scan_real):
            return []

        categories = []
        for filename in sorted(os.listdir(scan_real)):
            if filename.endswith('.json'):
                categories.append(filename[:-5])  # Strip .json
        return categories

    def load_category(self, category: str, exam_id: str | None = None) -> list[dict]:
        """Load questions for a specific category."""
        file_path = self._resolve_category_path(exam_id, category)
        if not file_path:
            return []

        if not os.path.exists(file_path):
            logger.warning('Question file not found: %s', file_path)
            return []

        try:
            with open(file_path) as f:
                data = json.load(f)
                return data.get('questions', [])
        except json.JSONDecodeError as e:
            logger.error('Error parsing %s: %s', file_path, e)
            return []
        except OSError as e:
            logger.error('Error loading %s: %s', file_path, e)
            return []

    def get_question_by_id(
        self,
        question_id: str,
        exam_id: str | None = None,
        categories: list[str] | None = None,
    ) -> dict | None:
        """Get a specific question by ID."""
        all_questions = self.load_all_questions(exam_id=exam_id, categories=categories)

        for _category, questions in all_questions.items():
            for question in questions:
                if question.get('id') == question_id:
                    return question

        return None

    def get_questions_by_category(
        self,
        category: str,
        exam_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Get questions for a specific category."""
        questions = self.load_category(category, exam_id=exam_id)

        if limit:
            return questions[:limit]

        return questions

    def get_random_questions(
        self,
        category: str,
        count: int,
        exam_id: str | None = None,
    ) -> list[dict]:
        """Get random questions from a category."""
        questions = self.load_category(category, exam_id=exam_id)
        unique_questions = list({q.get('id'): q for q in questions}.values())

        if len(unique_questions) <= count:
            return unique_questions

        return random.sample(unique_questions, count)

    def reload_questions(self, exam_id: str | None = None) -> None:
        """Force reload of questions from files."""
        if exam_id:
            self._questions_cache.pop(exam_id, None)
        else:
            self._questions_cache = {}
