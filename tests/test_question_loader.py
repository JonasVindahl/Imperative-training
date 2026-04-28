"""Tests for QuestionLoader, especially path-traversal hardening."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.question_loader import QuestionLoader


@pytest.fixture()
def questions_root(tmp_path: Path) -> Path:
    """Build a fake questions tree:
        <root>/
            ds_exam/
                arrays.json   -> 2 questions
                empty.json    -> []
            legacy_cat.json   -> 1 question (flat layout)
    """
    exam_dir = tmp_path / 'ds_exam'
    exam_dir.mkdir()
    base_mc = {
        'title': 'Sample',
        'description': 'Pick the right one.',
        'options': ['x', 'y'],
        'correct_answer': 'A',
    }
    (exam_dir / 'arrays.json').write_text(json.dumps({
        'questions': [
            {'id': 'q1', 'category': 'arrays', 'type': 'multiple_choice', **base_mc},
            {'id': 'q2', 'category': 'arrays', 'type': 'multiple_choice', **base_mc},
        ]
    }))
    (exam_dir / 'empty.json').write_text(json.dumps({'questions': []}))
    (tmp_path / 'legacy_cat.json').write_text(json.dumps({
        'questions': [{
            'id': 'L1',
            'category': 'legacy_cat',
            'type': 'code_output',
            'title': 'Legacy',
            'description': 'What does this print?',
            'correct_answer': '42',
        }]
    }))
    return tmp_path


@pytest.fixture()
def loader(questions_root: Path) -> QuestionLoader:
    return QuestionLoader(str(questions_root))


class TestSafeIds:
    @pytest.mark.parametrize('bad', [
        '../escape',
        'foo/bar',
        'foo\\bar',
        '..',
        '',
        'has space',
        'has;semicolon',
    ])
    def test_unsafe_category_ids_are_rejected(self, loader, bad):
        assert loader.load_category(bad, exam_id='ds_exam') == []

    @pytest.mark.parametrize('bad', [
        '../escape',
        'foo/bar',
        '..',
        'has space',
    ])
    def test_unsafe_exam_ids_are_rejected(self, loader, bad):
        # Direct API
        assert loader.load_category('arrays', exam_id=bad) == []
        # Via discovery
        assert loader._discover_categories(bad) == []

    @pytest.mark.parametrize('good', ['ds_exam', 'c_programming', 'oop-java', 'a1'])
    def test_safe_ids_are_accepted(self, loader, good):
        assert QuestionLoader._is_safe_id(good) is True


class TestLoading:
    def test_per_exam_layout(self, loader):
        questions = loader.load_category('arrays', exam_id='ds_exam')
        assert len(questions) == 2
        assert questions[0]['id'] == 'q1'

    def test_legacy_flat_fallback(self, loader):
        questions = loader.load_category('legacy_cat', exam_id='ds_exam')
        assert len(questions) == 1
        assert questions[0]['id'] == 'L1'

    def test_missing_category_returns_empty(self, loader):
        assert loader.load_category('does_not_exist', exam_id='ds_exam') == []

    def test_malformed_json_returns_empty(self, loader, questions_root: Path):
        (questions_root / 'ds_exam' / 'broken.json').write_text('{not json')
        assert loader.load_category('broken', exam_id='ds_exam') == []

    def test_get_question_by_id(self, loader):
        q = loader.get_question_by_id('q2', exam_id='ds_exam', categories=['arrays'])
        assert q is not None
        assert q['id'] == 'q2'

    def test_discover_categories(self, loader):
        cats = loader._discover_categories('ds_exam')
        assert sorted(cats) == ['arrays', 'empty']

    def test_random_questions_caps_at_pool_size(self, loader):
        picks = loader.get_random_questions('arrays', count=99, exam_id='ds_exam')
        assert len(picks) == 2

    def test_reload_resets_cache(self, loader, questions_root: Path):
        loader.load_all_questions(exam_id='ds_exam', categories=['arrays'])
        # Mutate file on disk
        (questions_root / 'ds_exam' / 'arrays.json').write_text(json.dumps({'questions': []}))
        loader.reload_questions('ds_exam')
        assert loader.load_all_questions(exam_id='ds_exam', categories=['arrays']) == {}


class TestOptionsNormalisation:
    def test_dict_options_become_list_in_letter_order(self, tmp_path: Path):
        exam_dir = tmp_path / 'demo'
        exam_dir.mkdir()
        (exam_dir / 'cat.json').write_text(json.dumps({
            'questions': [{
                'id': 'q1',
                'type': 'multiple_choice',
                'title': 'Demo',
                'description': 'Pick one.',
                'options': {'B': 'second', 'A': 'first', 'D': 'fourth', 'C': 'third'},
                'correct_answer': 'B',
            }]
        }))
        loader = QuestionLoader(str(tmp_path))
        q = loader.load_category('cat', exam_id='demo')[0]
        assert q['options'] == ['first', 'second', 'third', 'fourth']
        # correct_answer 'B' must still index to 'second'
        idx = ord(q['correct_answer']) - ord('A')
        assert q['options'][idx] == 'second'

    def test_list_options_pass_through_unchanged(self, tmp_path: Path):
        exam_dir = tmp_path / 'demo'
        exam_dir.mkdir()
        (exam_dir / 'cat.json').write_text(json.dumps({
            'questions': [{
                'id': 'q1',
                'type': 'multiple_choice',
                'title': 'Demo',
                'description': 'Pick one.',
                'options': ['x', 'y', 'z'],
                'correct_answer': 'A',
            }]
        }))
        loader = QuestionLoader(str(tmp_path))
        q = loader.load_category('cat', exam_id='demo')[0]
        assert q['options'] == ['x', 'y', 'z']
