"""Tests for AdaptiveLearningService.get_recommended_next() — the dashboard's
study-coach surface. The ranking heuristic is the spec; these tests pin it
down so behavioural changes are intentional."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from models import Progress, User, db
from services.adaptive import AdaptiveLearningService

CATEGORIES = ['cat_a', 'cat_b', 'cat_c', 'cat_d']


def _add_progress(user_id, category, *, attempted, correct,
                  last_practiced_days_ago=0, exam_id='c_programming'):
    p = Progress(
        user_id=user_id,
        category=category,
        exam_id=exam_id,
        total_attempted=attempted,
        total_correct=correct,
        last_practiced=datetime.utcnow() - timedelta(days=last_practiced_days_ago),
    )
    db.session.add(p)
    return p


@pytest.fixture()
def user(db):
    u = User(name='Recos', email='recs@example.com', password_hash='x')
    db.session.add(u)
    db.session.commit()
    return u


def _service(user_id):
    return AdaptiveLearningService(user_id, categories=CATEGORIES, exam_id='c_programming')


class TestRanking:
    def test_untouched_categories_recommended_first(self, app, db, user):
        with app.app_context():
            # cat_a: mastered (90%, recent). cat_b: untouched.
            _add_progress(user.id, 'cat_a', attempted=10, correct=9, last_practiced_days_ago=1)
            db.session.commit()
            recs = _service(user.id).get_recommended_next()
            cats = [r['category'] for r in recs]
            # untouched cats (b, c, d) should appear; mastered a should not.
            assert 'cat_a' not in cats
            assert recs[0]['reason'] == 'never_practiced'

    def test_low_accuracy_outranks_rusty(self, app, db, user):
        with app.app_context():
            # cat_a is rusty (60% acc, 30 days ago). cat_b is bombing (20%, recent).
            _add_progress(user.id, 'cat_a', attempted=10, correct=6, last_practiced_days_ago=30)
            _add_progress(user.id, 'cat_b', attempted=10, correct=2, last_practiced_days_ago=1)
            _add_progress(user.id, 'cat_c', attempted=20, correct=20, last_practiced_days_ago=1)  # mastered, ignored
            _add_progress(user.id, 'cat_d', attempted=20, correct=20, last_practiced_days_ago=1)  # mastered, ignored
            db.session.commit()
            recs = _service(user.id).get_recommended_next(limit=2)
            assert [r['category'] for r in recs] == ['cat_b', 'cat_a']
            assert recs[0]['reason'] == 'low_accuracy'
            assert recs[1]['reason'] == 'getting_rusty'

    def test_mastered_recent_filtered_out(self, app, db, user):
        with app.app_context():
            # All mastered + recent → recommendations skip them, untouched fills.
            _add_progress(user.id, 'cat_a', attempted=20, correct=20, last_practiced_days_ago=0)
            _add_progress(user.id, 'cat_b', attempted=20, correct=19, last_practiced_days_ago=2)
            db.session.commit()
            recs = _service(user.id).get_recommended_next()
            assert all(r['category'] not in {'cat_a', 'cat_b'} for r in recs)

    def test_low_accuracy_needs_min_attempts(self, app, db, user):
        with app.app_context():
            # 1 attempt, 0% — too thin to call low_accuracy. Falls through to
            # keep_going (since accuracy < 90 and recent).
            _add_progress(user.id, 'cat_a', attempted=1, correct=0, last_practiced_days_ago=1)
            db.session.commit()
            recs = _service(user.id).get_recommended_next(limit=len(CATEGORIES))
            cat_a_rec = next(r for r in recs if r['category'] == 'cat_a')
            assert cat_a_rec['reason'] != 'low_accuracy'

    def test_lower_accuracy_higher_priority(self, app, db, user):
        with app.app_context():
            _add_progress(user.id, 'cat_a', attempted=10, correct=5, last_practiced_days_ago=1)  # 50%
            _add_progress(user.id, 'cat_b', attempted=10, correct=2, last_practiced_days_ago=1)  # 20%
            _add_progress(user.id, 'cat_c', attempted=10, correct=10, last_practiced_days_ago=1)
            _add_progress(user.id, 'cat_d', attempted=10, correct=10, last_practiced_days_ago=1)
            db.session.commit()
            recs = _service(user.id).get_recommended_next(limit=2)
            # cat_b (20%) ranks before cat_a (50%)
            assert [r['category'] for r in recs] == ['cat_b', 'cat_a']

    def test_limit_respected(self, app, db, user):
        with app.app_context():
            db.session.commit()
            # All 4 cats untouched; ask for 2.
            recs = _service(user.id).get_recommended_next(limit=2)
            assert len(recs) == 2

    def test_exam_scoping(self, app, db, user):
        with app.app_context():
            # Mistake in another exam doesn't bleed in.
            _add_progress(user.id, 'cat_a', attempted=10, correct=2, last_practiced_days_ago=1, exam_id='other_exam')
            db.session.commit()
            recs = _service(user.id).get_recommended_next()
            for r in recs:
                # cat_a here only has progress in the other exam → so for our
                # scoped service it counts as never_practiced, not low_accuracy.
                if r['category'] == 'cat_a':
                    assert r['reason'] == 'never_practiced'


class TestPayloadShape:
    def test_each_record_has_required_keys(self, app, db, user):
        with app.app_context():
            _add_progress(user.id, 'cat_a', attempted=10, correct=4, last_practiced_days_ago=2)
            db.session.commit()
            recs = _service(user.id).get_recommended_next()
            for r in recs:
                for key in ('category', 'reason', 'accuracy', 'attempted',
                            'last_practiced', 'days_since', 'priority'):
                    assert key in r, f'{key!r} missing from {r!r}'

    def test_days_since_zero_for_today(self, app, db, user):
        with app.app_context():
            _add_progress(user.id, 'cat_a', attempted=10, correct=4, last_practiced_days_ago=0)
            db.session.commit()
            recs = _service(user.id).get_recommended_next(limit=len(CATEGORIES))
            cat_a = next(r for r in recs if r['category'] == 'cat_a')
            assert cat_a['days_since'] == 0
