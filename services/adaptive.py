from typing import List, Dict
import random
from models import Progress, db


class AdaptiveLearningService:
    """Service for generating adaptive practice sessions based on user performance"""

    CATEGORIES = [
        'memory_management',
        'integer_division',
        'strings',
        'structs',
        'pointers',
        'recursion',
        'control_flow'
    ]

    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_recommended_categories(self) -> List[str]:
        """
        Get the 3 weakest categories for the user

        Returns:
            List of category names sorted by weakest first
        """
        progress_records = Progress.query.filter_by(user_id=self.user_id).all()

        # Calculate accuracy for each category
        category_scores = {}
        for record in progress_records:
            category_scores[record.category] = record.accuracy

        # Add categories with no attempts (0% accuracy)
        for category in self.CATEGORIES:
            if category not in category_scores:
                category_scores[category] = 0

        # Sort by accuracy (ascending)
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])

        # Return top 3 weakest
        return [cat for cat, score in sorted_categories[:3]]

    def generate_practice_session(self, questions_pool: Dict, session_size: int = 10) -> List[Dict]:
        """
        Generate an adaptive practice session

        Args:
            questions_pool: Dictionary mapping category -> list of questions
            session_size: Number of questions in the session

        Returns:
            List of question dictionaries
        """
        weak_categories = self.get_recommended_categories()

        # 70% weak areas, 30% review from other areas
        weak_count = int(session_size * 0.7)
        review_count = session_size - weak_count

        session_questions = []
        used_ids = set()
        remaining = {cat: list(questions) for cat, questions in questions_pool.items()}

        def pick_unique(categories: List[str], count: int) -> List[Dict]:
            picks = []
            available = [cat for cat in categories if remaining.get(cat)]
            while len(picks) < count and available:
                category = random.choice(available)
                candidates = [q for q in remaining[category] if q.get('id') not in used_ids]
                if not candidates:
                    available.remove(category)
                    continue
                question = random.choice(candidates)
                picks.append(question)
                used_ids.add(question.get('id'))
                remaining[category].remove(question)
                if not remaining[category]:
                    available.remove(category)
            return picks

        # Select questions from weak categories
        session_questions.extend(pick_unique(weak_categories, weak_count))

        # Select review questions from other categories
        review_categories = [cat for cat in self.CATEGORIES if cat not in weak_categories]
        session_questions.extend(pick_unique(review_categories, review_count))

        # Fill any remaining slots from all categories without repeats
        if len(session_questions) < session_size:
            session_questions.extend(
                pick_unique(self.CATEGORIES, session_size - len(session_questions))
            )

        # Shuffle to mix weak and review questions
        random.shuffle(session_questions)

        return session_questions[:session_size]

    def get_progress_summary(self) -> Dict:
        """
        Get overall progress summary for the user

        Returns:
            Dictionary with progress statistics
        """
        progress_records = Progress.query.filter_by(user_id=self.user_id).all()

        total_attempted = sum(p.total_attempted for p in progress_records)
        total_correct = sum(p.total_correct for p in progress_records)

        overall_accuracy = 0
        if total_attempted > 0:
            overall_accuracy = int((total_correct / total_attempted) * 100)

        category_progress = {}
        for record in progress_records:
            category_progress[record.category] = {
                'attempted': record.total_attempted,
                'correct': record.total_correct,
                'accuracy': record.accuracy,
                'last_practiced': record.last_practiced.isoformat() if record.last_practiced else None
            }

        # Add categories with no attempts
        for category in self.CATEGORIES:
            if category not in category_progress:
                category_progress[category] = {
                    'attempted': 0,
                    'correct': 0,
                    'accuracy': 0,
                    'last_practiced': None
                }

        weak_areas = self.get_recommended_categories()

        return {
            'overall_accuracy': overall_accuracy,
            'total_attempted': total_attempted,
            'total_correct': total_correct,
            'category_progress': category_progress,
            'weak_areas': weak_areas,
            'recommendations': self._generate_recommendations(weak_areas, category_progress)
        }

    def _generate_recommendations(self, weak_areas: List[str], category_progress: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []

        for category in weak_areas[:2]:  # Top 2 weakest
            accuracy = category_progress[category]['accuracy']
            category_name = category.replace('_', ' ').title()

            if accuracy == 0:
                recommendations.append(f"Start practicing {category_name} (not yet attempted)")
            elif accuracy < 50:
                recommendations.append(f"Focus on {category_name} (current: {accuracy}%)")
            else:
                recommendations.append(f"Improve {category_name} (current: {accuracy}%)")

        return recommendations

    def update_progress(self, category: str, correct: bool) -> None:
        """
        Update progress after a question attempt

        Args:
            category: Question category
            correct: Whether the answer was correct
        """
        progress = Progress.query.filter_by(
            user_id=self.user_id,
            category=category
        ).first()

        if not progress:
            progress = Progress(
                user_id=self.user_id,
                category=category,
                total_attempted=0,
                total_correct=0
            )
            db.session.add(progress)

        progress.total_attempted = (progress.total_attempted or 0) + 1
        if correct:
            progress.total_correct = (progress.total_correct or 0) + 1

        from datetime import datetime
        progress.last_practiced = datetime.utcnow()

        db.session.commit()
