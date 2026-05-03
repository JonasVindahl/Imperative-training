"""Tests for the "Drill mistakes" feature in AdaptiveLearningService.

Covers:
- Latest-attempt-wins semantics (a question retired by a later correct answer
  is no longer in the drill pool).
- Lookback-window honoured (older mistakes drop off).
- Exam scoping (mistakes from another exam don't leak in).
- Pool-aware filtering (mistakes for retired questions are skipped, not
  surfaced as orphans).
- Session ordering (most recent mistake first).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from models import Attempt, User, db
from services.adaptive import AdaptiveLearningService


def _add_attempt(user_id: int, question_id: str, *, correct: bool,
                 days_ago: float = 0, exam_id: str = 'c_programming',
                 category: str = 'control_flow'):
    attempt = Attempt(
        user_id=user_id,
        exam_id=exam_id,
        category=category,
        question_id=question_id,
        correct=correct,
        time_spent=10,
        submitted_answer='X',
        hints_used=0,
        timestamp=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.session.add(attempt)


@pytest.fixture()
def user(db):
    u = User(name='Mistake Tester', email='mt@example.com', password_hash='x')
    db.session.add(u)
    db.session.commit()
    return u


def _service(user_id: int, exam_id: str = 'c_programming') -> AdaptiveLearningService:
    return AdaptiveLearningService(user_id, categories=['control_flow', 'arrays_and_strings'], exam_id=exam_id)


class TestMistakeIds:
    def test_returns_only_incorrect(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q1', correct=False, days_ago=1)
            _add_attempt(user.id, 'q2', correct=True, days_ago=1)
            db.session.commit()
            ids = _service(user.id).get_mistake_question_ids()
            assert ids == ['q1']

    def test_latest_correct_retires_a_mistake(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q1', correct=False, days_ago=5)
            _add_attempt(user.id, 'q1', correct=True, days_ago=1)  # got it right later
            db.session.commit()
            assert _service(user.id).get_mistake_question_ids() == []

    def test_latest_incorrect_keeps_it_in_pool(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q1', correct=True, days_ago=5)
            _add_attempt(user.id, 'q1', correct=False, days_ago=1)  # regression
            db.session.commit()
            assert _service(user.id).get_mistake_question_ids() == ['q1']

    def test_lookback_window_drops_old_mistakes(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q_old', correct=False, days_ago=120)
            _add_attempt(user.id, 'q_recent', correct=False, days_ago=3)
            db.session.commit()
            ids = _service(user.id).get_mistake_question_ids(lookback_days=30)
            assert ids == ['q_recent']

    def test_exam_scoping(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q_c', correct=False, days_ago=1, exam_id='c_programming')
            _add_attempt(user.id, 'q_d', correct=False, days_ago=1, exam_id='diskrete_strukturer')
            db.session.commit()
            assert _service(user.id, 'c_programming').get_mistake_question_ids() == ['q_c']
            assert _service(user.id, 'diskrete_strukturer').get_mistake_question_ids() == ['q_d']

    def test_recency_ordering(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q_oldest',  correct=False, days_ago=20)
            _add_attempt(user.id, 'q_middle',  correct=False, days_ago=10)
            _add_attempt(user.id, 'q_newest',  correct=False, days_ago=1)
            db.session.commit()
            ids = _service(user.id).get_mistake_question_ids()
            assert ids == ['q_newest', 'q_middle', 'q_oldest']


class TestSessionBuilder:
    def _pool(self) -> dict:
        return {
            'control_flow': [
                {'id': 'q1', 'category': 'control_flow', 'title': 'A'},
                {'id': 'q2', 'category': 'control_flow', 'title': 'B'},
            ],
            'arrays_and_strings': [
                {'id': 'q3', 'category': 'arrays_and_strings', 'title': 'C'},
            ],
        }

    def test_picks_only_mistakes(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q1', correct=False, days_ago=1)
            _add_attempt(user.id, 'q2', correct=True,  days_ago=1)
            _add_attempt(user.id, 'q3', correct=False, days_ago=2)
            db.session.commit()
            picks = _service(user.id).generate_mistakes_session(self._pool(), session_size=10)
            assert [q['id'] for q in picks] == ['q1', 'q3']

    def test_caps_at_session_size(self, app, db, user):
        with app.app_context():
            for i in range(5):
                _add_attempt(user.id, f'q{i}', correct=False, days_ago=i + 1)
            db.session.commit()
            pool = {
                'control_flow': [
                    {'id': f'q{i}', 'category': 'control_flow', 'title': str(i)}
                    for i in range(5)
                ],
            }
            picks = _service(user.id).generate_mistakes_session(pool, session_size=2)
            assert len(picks) == 2
            # most recent first
            assert picks[0]['id'] == 'q0'

    def test_skips_orphan_mistakes(self, app, db, user):
        """A mistake whose question_id no longer exists in the active pool
        (e.g. the question was renamed/removed) is skipped silently."""
        with app.app_context():
            _add_attempt(user.id, 'q1',     correct=False, days_ago=1)
            _add_attempt(user.id, 'orphan', correct=False, days_ago=2)
            db.session.commit()
            picks = _service(user.id).generate_mistakes_session(self._pool(), session_size=10)
            assert [q['id'] for q in picks] == ['q1']

    def test_empty_when_no_mistakes(self, app, db, user):
        with app.app_context():
            assert _service(user.id).generate_mistakes_session(self._pool()) == []

    def test_count_matches_session_pool(self, app, db, user):
        with app.app_context():
            _add_attempt(user.id, 'q1', correct=False, days_ago=1)
            _add_attempt(user.id, 'q2', correct=False, days_ago=1)
            _add_attempt(user.id, 'q3', correct=True,  days_ago=1)
            db.session.commit()
            assert _service(user.id).get_mistake_count(lookback_days=30) == 2
