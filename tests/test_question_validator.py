"""Tests for services/question_validator.py."""

from __future__ import annotations

import json
from pathlib import Path

from services.question_validator import (
    LEVEL_ERROR,
    LEVEL_WARNING,
    filter_errors,
    lint_question,
    validate_question,
    validate_question_file,
    validate_questions_root,
)


def _mc(**overrides: object) -> dict:
    base = {
        'id': 'q1',
        'type': 'multiple_choice',
        'title': 'A title',
        'description': 'A description.',
        'options': ['one', 'two', 'three'],
        'correct_answer': 'A',
    }
    base.update(overrides)
    return base


class TestCommonFields:
    def test_canonical_question_passes(self):
        assert validate_question(_mc()) == []

    def test_missing_id_is_error(self):
        issues = validate_question(_mc(id=None))
        codes = {i.code for i in issues}
        assert 'missing_field' in codes
        assert all(i.level == LEVEL_ERROR for i in issues)

    def test_unknown_type_is_error(self):
        issues = validate_question(_mc(type='not_a_real_type'))
        assert any(i.code == 'unknown_type' for i in issues)

    def test_missing_title_or_description(self):
        codes = {i.code for i in validate_question(_mc(title=''))}
        assert 'missing_field' in codes


class TestMultipleChoice:
    def test_dict_options_pass_validation(self):
        # The dict variant is structurally valid (just non-canonical).
        q = _mc(options={'A': 'one', 'B': 'two'}, correct_answer='B')
        assert filter_errors(validate_question(q)) == []

    def test_dict_options_emit_lint_warning(self):
        q = _mc(options={'A': 'one', 'B': 'two'}, correct_answer='B')
        warnings = lint_question(q)
        assert any(w.code == 'non_canonical_options_dict' for w in warnings)
        assert all(w.level == LEVEL_WARNING for w in warnings)

    def test_correct_answer_out_of_range_is_error(self):
        q = _mc(options=['only'], correct_answer='B')
        issues = validate_question(q)
        # bad_options because <2 entries, AND correct_answer_out_of_range.
        codes = {i.code for i in issues}
        assert 'bad_options' in codes or 'correct_answer_out_of_range' in codes

    def test_non_letter_correct_answer_is_error(self):
        q = _mc(correct_answer='1')
        assert any(i.code == 'bad_correct_answer' for i in validate_question(q))


class TestMultipleSelect:
    def test_csv_correct_answer(self):
        q = _mc(type='multiple_select', options=['a', 'b', 'c'], correct_answer='A,C')
        assert validate_question(q) == []

    def test_list_correct_answer(self):
        q = _mc(type='multiple_select', options=['a', 'b'], correct_answer=['A', 'B'])
        assert validate_question(q) == []

    def test_out_of_range_letter(self):
        q = _mc(type='multiple_select', options=['a', 'b'], correct_answer='A,Z')
        assert any(i.code == 'correct_answer_out_of_range' for i in validate_question(q))


class TestFillBlanks:
    def test_dict_shape_canonical(self):
        q = {
            'id': 'fb1',
            'type': 'fill_blanks',
            'title': 'T',
            'description': 'A × B is {blank1}, sized {blank2}.',
            'blanks': {
                'blank1': {'correct': 'ordered pairs', 'options': ['ordered pairs', 'subsets']},
                'blank2': {'correct': 'm · n', 'options': ['m + n', 'm · n']},
            },
        }
        assert validate_question(q) == []
        assert lint_question(q) == []

    def test_dict_shape_placeholder_mismatch(self):
        q = {
            'id': 'fb2', 'type': 'fill_blanks', 'title': 'T',
            'description': 'See {blank1} and {blank9}.',
            'blanks': {'blank1': {'correct': 'a', 'options': ['a']}},
        }
        assert any(i.code == 'placeholder_mismatch' for i in validate_question(q))

    def test_legacy_nested_shape_warns(self):
        q = {
            'id': 'fb3', 'type': 'fill_blanks', 'title': 'T', 'description': 'D',
            'questions': [
                {'id': 1, 'text': 'foo', 'blanks': [{'correct': 'a'}]},
            ],
        }
        # Structurally valid …
        assert filter_errors(validate_question(q)) == []
        # … but flagged for migration.
        warnings = lint_question(q)
        assert any(w.code == 'non_canonical_fill_blanks_nested' for w in warnings)

    def test_neither_shape_is_error(self):
        q = {'id': 'fb4', 'type': 'fill_blanks', 'title': 'T', 'description': 'D'}
        assert any(i.code == 'bad_fill_blanks' for i in validate_question(q))


class TestOtherTypes:
    def test_drag_drop_requires_blanks(self):
        q = {'id': 'd1', 'type': 'drag_drop', 'title': 'T', 'description': 'D',
             'code_template': 'int main() {{blank1}}'}
        assert any(i.code == 'bad_blanks' for i in validate_question(q))

    def test_recursive_trace_requires_test_cases(self):
        q = {'id': 'r1', 'type': 'recursive_trace', 'title': 'T', 'description': 'D'}
        assert any(i.code == 'bad_test_cases' for i in validate_question(q))

    def test_bug_finding_correct_answer_must_be_int_list(self):
        q = {'id': 'b1', 'type': 'bug_finding', 'title': 'T', 'description': 'D',
             'correct_answer': '7,12'}  # wrong: should be [7, 12]
        assert any(i.code == 'bad_correct_answer' for i in validate_question(q))

    def test_struct_size_accepts_numeric_string(self):
        q = {'id': 's1', 'type': 'struct_size', 'title': 'T', 'description': 'D',
             'correct_answer': '24'}
        assert validate_question(q) == []


class TestFileLevel:
    def test_duplicate_id_within_file(self, tmp_path: Path):
        p = tmp_path / 'cat.json'
        p.write_text(json.dumps({
            'questions': [_mc(id='dup'), _mc(id='dup')],
        }))
        codes = {i.code for i in validate_question_file(str(p))}
        assert 'duplicate_id' in codes

    def test_invalid_json(self, tmp_path: Path):
        p = tmp_path / 'broken.json'
        p.write_text('{not json')
        issues = validate_question_file(str(p))
        assert issues and issues[0].code == 'invalid_json'

    def test_missing_questions_root(self, tmp_path: Path):
        p = tmp_path / 'noroot.json'
        p.write_text(json.dumps({'foo': []}))
        codes = {i.code for i in validate_question_file(str(p))}
        assert 'bad_root' in codes


class TestRoot:
    def test_skips_ignored_top_level(self, tmp_path: Path):
        good = tmp_path / 'good'
        good.mkdir()
        bad = tmp_path / 'archive'
        bad.mkdir()
        (good / 'cat.json').write_text(json.dumps({'questions': [_mc()]}))
        (bad / 'cat.json').write_text(json.dumps({'questions': [_mc(id='', title='')]}))

        # Without the ignore, the archive contributes errors.
        full = validate_questions_root(str(tmp_path))
        assert filter_errors(full)

        # With the ignore, only the 'good' tree is walked → no errors.
        filtered = validate_questions_root(str(tmp_path), ignore_top_level=['archive'])
        assert filter_errors(filtered) == []

    def test_cross_file_duplicate_id(self, tmp_path: Path):
        exam = tmp_path / 'exam'
        exam.mkdir()
        (exam / 'a.json').write_text(json.dumps({'questions': [_mc(id='shared')]}))
        (exam / 'b.json').write_text(json.dumps({'questions': [_mc(id='shared')]}))
        codes = {i.code for i in validate_questions_root(str(tmp_path))}
        assert 'duplicate_id_cross_file' in codes


class TestRealQuestions:
    def test_repo_questions_have_no_structural_errors(self):
        """Snapshot guard: every wired-up exam dir must pass structural
        validation. ``old_categories`` is excluded — it is on-disk archive
        not referenced from ``exams.json`` and intentionally not loaded."""
        import os
        repo_root = Path(__file__).resolve().parent.parent
        questions_root = repo_root / 'questions'
        if not questions_root.is_dir():
            return
        # Load the live exams.json and only validate the dirs it points at.
        exams_path = repo_root / 'exams.json'
        with open(exams_path, encoding='utf-8') as f:
            exams = json.load(f).get('exams', [])
        wired_dirs = {e['id'] for e in exams}
        all_top_level = {name for name in os.listdir(questions_root)
                         if (questions_root / name).is_dir()}
        ignore = sorted(all_top_level - wired_dirs)
        issues = validate_questions_root(str(questions_root), ignore_top_level=ignore)
        errors = filter_errors(issues)
        assert errors == [], '\n'.join(e.format() for e in errors[:10])
