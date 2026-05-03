import random
from datetime import datetime, timedelta

from sqlalchemy import func

from models import Attempt, Progress, db


class AdaptiveLearningService:
    """Service for generating adaptive practice sessions based on user performance"""

    # Legacy fallback categories (used when no exam-specific categories are provided)
    DEFAULT_CATEGORIES = [
        'pointers_and_memory',
        'arrays_and_strings',
        'structs_and_data_structures',
        'control_flow',
        'functions_and_recursion',
        'file_io',
        'fundamentals',
        'programming_challenges'
    ]

    def __init__(self, user_id: int, categories: list[str] = None, exam_id: str = None):
        self.user_id = user_id
        self.categories = categories or self.DEFAULT_CATEGORIES
        self.exam_id = exam_id

    def get_recommended_categories(self, categories: list[str] = None) -> list[str]:
        """
        Get the 3 weakest categories for the user

        Returns:
            List of category names sorted by weakest first
        """
        categories = categories or self.categories

        if self.exam_id:
            progress_records = Progress.query.filter_by(
                user_id=self.user_id, exam_id=self.exam_id
            ).all()
        else:
            progress_records = Progress.query.filter_by(user_id=self.user_id).all()

        # Calculate accuracy for each category
        category_scores = {}
        for record in progress_records:
            if record.category in categories:
                category_scores[record.category] = record.accuracy

        # Add categories with no attempts (0% accuracy)
        for category in categories:
            if category not in category_scores:
                category_scores[category] = 0

        # Sort by accuracy (ascending)
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])

        # Return top 3 weakest
        return [cat for cat, score in sorted_categories[:3]]

    def generate_practice_session(self, questions_pool: dict, session_size: int = 10) -> list[dict]:
        """
        Generate an adaptive practice session

        Args:
            questions_pool: Dictionary mapping category -> list of questions
            session_size: Number of questions in the session

        Returns:
            List of question dictionaries
        """
        all_categories = list(questions_pool.keys()) or self.categories
        weak_categories = self.get_recommended_categories(all_categories)

        # 70% weak areas, 30% review from other areas
        weak_count = int(session_size * 0.7)
        review_count = session_size - weak_count

        session_questions = []
        used_ids = set()
        remaining = {cat: list(questions) for cat, questions in questions_pool.items()}

        def pick_unique(categories: list[str], count: int) -> list[dict]:
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
        review_categories = [cat for cat in all_categories if cat not in weak_categories]
        session_questions.extend(pick_unique(review_categories, review_count))

        # Fill any remaining slots from all categories without repeats
        if len(session_questions) < session_size:
            session_questions.extend(
                pick_unique(all_categories, session_size - len(session_questions))
            )

        # Shuffle to mix weak and review questions
        random.shuffle(session_questions)

        return session_questions[:session_size]

    def get_mistake_question_ids(self, lookback_days: int = 30) -> list[str]:
        """Return question ids the user got wrong in the last ``lookback_days``,
        deduped to one entry per question (the most recent attempt). Sorted
        by recency: most recent mistake first.

        A question is considered "still wrong" only if the user's most recent
        attempt was incorrect — re-answering it correctly retires it from the
        drill pool. This matches how a student would think about it ("I keep
        getting these wrong").
        """
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)

        # One row per (user, exam_id?, question_id): the most recent attempt.
        latest_q = (
            db.session.query(
                Attempt.question_id.label('question_id'),
                func.max(Attempt.id).label('latest_id'),
            )
            .filter(Attempt.user_id == self.user_id)
            .filter(Attempt.timestamp >= cutoff)
        )
        if self.exam_id:
            latest_q = latest_q.filter(Attempt.exam_id == self.exam_id)
        latest_q = latest_q.group_by(Attempt.question_id).subquery()

        rows = (
            db.session.query(Attempt.question_id, Attempt.timestamp)
            .join(latest_q, Attempt.id == latest_q.c.latest_id)
            .filter(Attempt.correct.is_(False))
            .order_by(Attempt.timestamp.desc())
            .all()
        )
        return [qid for qid, _ts in rows]

    def get_mistake_count(self, lookback_days: int = 30) -> int:
        """Cheap counter for surfacing in the UI ("12 mistakes from last 30 days")."""
        return len(self.get_mistake_question_ids(lookback_days=lookback_days))

    def generate_mistakes_session(
        self,
        questions_pool: dict,
        session_size: int = 10,
        lookback_days: int = 30,
    ) -> list[dict]:
        """Build a session entirely from questions the user has gotten wrong
        in the last ``lookback_days`` and that are still in the active exam's
        question pool. Most recent mistakes first; topped up from older ones
        if needed. Returns at most ``session_size`` questions, possibly fewer
        if the user simply doesn't have that many outstanding mistakes."""
        # Flatten the pool to one lookup table; only keep ids from categories
        # the active exam currently exposes (so a category that was retired
        # from exams.json doesn't pollute the drill).
        by_id: dict[str, dict] = {}
        for cat_questions in questions_pool.values():
            for q in cat_questions:
                qid = q.get('id')
                if isinstance(qid, str) and qid:
                    by_id[qid] = q

        mistake_ids = self.get_mistake_question_ids(lookback_days=lookback_days)
        picked: list[dict] = []
        seen: set[str] = set()
        for qid in mistake_ids:
            if qid in seen:
                continue
            q = by_id.get(qid)
            if q is None:
                # Question existed historically but isn't in the current pool —
                # skip silently.
                continue
            picked.append(q)
            seen.add(qid)
            if len(picked) >= session_size:
                break
        return picked

    # ------------------------------------------------------------------
    # Recommended-next: turns the dashboard into an active study coach.
    #
    # The dashboard surfaces 1-3 actionable recommendations. Each carries a
    # *reason code* the template uses to render Danish microcopy, and a
    # priority score so the top-ranked card is what truly needs attention.
    #
    # Heuristic (tunable):
    #   - Untouched categories rank highest (you can't improve what you
    #     haven't tried).
    #   - Among practiced categories, low-accuracy outranks rusty.
    #   - Rusty = last_practiced > 7 days ago AND accuracy 60..89%.
    #   - Mastered (≥90%, recent) is filtered out — no recommendation.
    # ------------------------------------------------------------------

    REASON_NEVER_PRACTICED = 'never_practiced'
    REASON_LOW_ACCURACY = 'low_accuracy'
    REASON_GETTING_RUSTY = 'getting_rusty'
    REASON_KEEP_GOING = 'keep_going'

    def _recommendation_for_category(self, category: str, record: 'Progress | None') -> dict | None:
        """Score a single category and produce a recommendation object, or
        None if the category is mastered + recent (don't waste a slot)."""
        if record is None or record.total_attempted == 0:
            return {
                'category': category,
                'reason': self.REASON_NEVER_PRACTICED,
                'accuracy': 0,
                'attempted': 0,
                'last_practiced': None,
                'days_since': None,
                'priority': 90,
            }

        accuracy = record.accuracy
        last = record.last_practiced
        days_since = None
        if last is not None:
            delta = datetime.utcnow() - last
            days_since = max(int(delta.total_seconds() // 86400), 0)

        # Mastered: high accuracy, practiced recently → don't recommend.
        if accuracy >= 90 and (days_since is None or days_since <= 7):
            return None

        # Low accuracy is the loudest signal we can pick on.
        if accuracy < 60 and record.total_attempted >= 3:
            # Lower accuracy → higher priority. 0% → 100, 59% → 41.
            priority = 100 - accuracy
            return {
                'category': category,
                'reason': self.REASON_LOW_ACCURACY,
                'accuracy': accuracy,
                'attempted': record.total_attempted,
                'last_practiced': last,
                'days_since': days_since,
                'priority': priority,
            }

        # Rusty: not practiced in a week, accuracy not great.
        if days_since is not None and days_since >= 7 and accuracy < 90:
            # Older = higher priority, capped at 80.
            priority = min(40 + days_since, 80)
            return {
                'category': category,
                'reason': self.REASON_GETTING_RUSTY,
                'accuracy': accuracy,
                'attempted': record.total_attempted,
                'last_practiced': last,
                'days_since': days_since,
                'priority': priority,
            }

        # Practiced recently, mid-pack accuracy: gentle keep-going nudge.
        if accuracy < 90:
            return {
                'category': category,
                'reason': self.REASON_KEEP_GOING,
                'accuracy': accuracy,
                'attempted': record.total_attempted,
                'last_practiced': last,
                'days_since': days_since,
                'priority': 30,
            }

        return None

    def get_recommended_next(self, limit: int = 3) -> list[dict]:
        """Return the top ``limit`` actionable recommendations, sorted by
        priority (most-needs-attention first), then by recency (older = more
        urgent), then by category id (stable for tests).

        Each entry is a dict with keys ``category``, ``reason``, ``accuracy``,
        ``attempted``, ``last_practiced`` (datetime|None), ``days_since``
        (int|None), ``priority`` (int)."""
        if self.exam_id:
            records = Progress.query.filter_by(
                user_id=self.user_id, exam_id=self.exam_id
            ).all()
        else:
            records = Progress.query.filter_by(user_id=self.user_id).all()

        record_by_cat = {r.category: r for r in records if r.category in self.categories}

        candidates: list[dict] = []
        for category in self.categories:
            rec = self._recommendation_for_category(category, record_by_cat.get(category))
            if rec is not None:
                candidates.append(rec)

        candidates.sort(
            key=lambda r: (
                -r['priority'],
                -(r['days_since'] or 0),
                r['category'],
            )
        )
        return candidates[:limit]

    def get_progress_summary(self, categories: list[str] = None) -> dict:
        """
        Get overall progress summary for the user

        Returns:
            Dictionary with progress statistics
        """
        if self.exam_id:
            progress_records = Progress.query.filter_by(
                user_id=self.user_id, exam_id=self.exam_id
            ).all()
        else:
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
        categories = categories or self.categories
        for category in categories:
            if category not in category_progress:
                category_progress[category] = {
                    'attempted': 0,
                    'correct': 0,
                    'accuracy': 0,
                    'last_practiced': None
                }

        weak_areas = self.get_recommended_categories(categories)

        return {
            'overall_accuracy': overall_accuracy,
            'total_attempted': total_attempted,
            'total_correct': total_correct,
            'category_progress': category_progress,
            'weak_areas': weak_areas,
            'recommendations': self._generate_recommendations(weak_areas, category_progress)
        }

    def _generate_recommendations(self, weak_areas: list[str], category_progress: dict) -> list[str]:
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
        filter_kwargs = dict(user_id=self.user_id, category=category)
        if self.exam_id:
            filter_kwargs['exam_id'] = self.exam_id

        progress = Progress.query.filter_by(**filter_kwargs).first()

        if not progress:
            progress = Progress(
                user_id=self.user_id,
                category=category,
                exam_id=self.exam_id or 'c_programming',
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
