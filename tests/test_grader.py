"""Unit tests for services.grader.GraderService.

One test class per question type; the compiler is stubbed for code-execution
graders so these tests never shell out to gcc.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from services.grader import GraderService


@pytest.fixture()
def grader():
    return GraderService()


class TestMultipleChoice:
    def test_correct_letter(self, grader):
        q = {'type': 'multiple_choice', 'correct_answer': 'B', 'options': ['x', 'y', 'z']}
        assert grader.grade(q, 'B')['correct'] is True

    def test_incorrect_letter(self, grader):
        q = {'type': 'multiple_choice', 'correct_answer': 'B', 'options': ['x', 'y', 'z']}
        assert grader.grade(q, 'A')['correct'] is False

    def test_case_insensitive_and_whitespace(self, grader):
        q = {'type': 'multiple_choice', 'correct_answer': 'C', 'options': ['x', 'y', 'z']}
        assert grader.grade(q, '  c ')['correct'] is True


class TestMultipleSelect:
    def test_exact_set_match(self, grader):
        q = {'type': 'multiple_select', 'correct_answer': ['A', 'C'], 'options': ['o1', 'o2', 'o3']}
        assert grader.grade(q, json.dumps(['a', 'c']))['correct'] is True

    def test_missing_one_is_wrong(self, grader):
        q = {'type': 'multiple_select', 'correct_answer': 'A,C', 'options': ['o1', 'o2', 'o3']}
        assert grader.grade(q, json.dumps(['A']))['correct'] is False

    def test_extra_one_is_wrong(self, grader):
        q = {'type': 'multiple_select', 'correct_answer': 'A', 'options': ['o1', 'o2']}
        assert grader.grade(q, json.dumps(['A', 'B']))['correct'] is False

    def test_invalid_json_is_no_selection(self, grader):
        q = {'type': 'multiple_select', 'correct_answer': 'A', 'options': ['o1']}
        assert grader.grade(q, 'not-json')['correct'] is False


class TestCodeOutput:
    def test_whitespace_normalised(self, grader):
        q = {'type': 'code_output', 'correct_answer': 'hello world'}
        assert grader.grade(q, '  hello  world  ')['correct'] is True

    def test_mismatch(self, grader):
        q = {'type': 'code_output', 'correct_answer': 'hello'}
        assert grader.grade(q, 'goodbye')['correct'] is False


class TestBugFinding:
    def test_set_equality(self, grader):
        q = {'type': 'bug_finding', 'correct_answer': [3, 7]}
        result = grader.grade(q, '3, 7')
        assert result['correct'] is True

    def test_partial_match_fails(self, grader):
        q = {'type': 'bug_finding', 'correct_answer': [3, 7, 12]}
        assert grader.grade(q, 'lines 3 and 7')['correct'] is False


class TestStructSize:
    def test_correct_int(self, grader):
        q = {'type': 'struct_size', 'correct_answer': 16}
        assert grader.grade(q, '16')['correct'] is True

    def test_non_numeric_input(self, grader):
        q = {'type': 'struct_size', 'correct_answer': 16}
        assert grader.grade(q, 'sixteen')['correct'] is False


class TestFillBlanks:
    def test_all_blanks_correct(self, grader):
        q = {
            'type': 'fill_blanks',
            'questions': [{'id': 1, 'blanks': [{'correct': 'foo'}, {'correct': 'bar'}]}],
        }
        answer = json.dumps({'blank_1_0': 'foo', 'blank_1_1': 'bar'})
        assert grader.grade(q, answer)['correct'] is True

    def test_one_blank_wrong(self, grader):
        q = {
            'type': 'fill_blanks',
            'questions': [{'id': 1, 'blanks': [{'correct': 'foo'}, {'correct': 'bar'}]}],
        }
        answer = json.dumps({'blank_1_0': 'foo', 'blank_1_1': 'baz'})
        result = grader.grade(q, answer)
        assert result['correct'] is False
        assert any(not r['correct'] for r in result['blank_results'])

    def test_dict_shape_all_correct(self, grader):
        q = {
            'type': 'fill_blanks',
            'description': 'A × B is the set of all {blank1} and |A × B| = {blank2}.',
            'blanks': {
                'blank1': {'correct': 'ordered pairs', 'options': ['ordered pairs', 'subsets']},
                'blank2': {'correct': 'm · n', 'options': ['m + n', 'm · n']},
            },
        }
        answer = json.dumps({'blank1': 'ordered pairs', 'blank2': 'm · n'})
        result = grader.grade(q, answer)
        assert result['correct'] is True
        assert {r['blank_id'] for r in result['blank_results']} == {'blank1', 'blank2'}

    def test_dict_shape_one_wrong(self, grader):
        q = {
            'type': 'fill_blanks',
            'description': 'Pre-order: {blank1}, In-order: {blank2}.',
            'blanks': {
                'blank1': {'correct': 'pre', 'options': ['pre', 'in']},
                'blank2': {'correct': 'in', 'options': ['pre', 'in']},
            },
        }
        answer = json.dumps({'blank1': 'pre', 'blank2': 'pre'})
        result = grader.grade(q, answer)
        assert result['correct'] is False
        wrong = [r for r in result['blank_results'] if not r['correct']]
        assert len(wrong) == 1 and wrong[0]['blank_id'] == 'blank2'

    def test_dict_shape_case_insensitive(self, grader):
        q = {
            'type': 'fill_blanks',
            'description': '{blank1}',
            'blanks': {'blank1': {'correct': 'Injektiv', 'options': ['Injektiv']}},
        }
        assert grader.grade(q, json.dumps({'blank1': '  injektiv '}))['correct'] is True


class TestDragDrop:
    def test_correct_placement(self, grader):
        q = {
            'type': 'drag_drop',
            'code_template': 'int x = {b1};',
            'blanks': {'b1': {'correct': '42'}},
        }
        assert grader.grade(q, json.dumps({'b1': '42'}))['correct'] is True

    def test_wrong_token(self, grader):
        q = {
            'type': 'drag_drop',
            'code_template': 'int x = {b1};',
            'blanks': {'b1': {'correct': '42'}},
        }
        assert grader.grade(q, json.dumps({'b1': '0'}))['correct'] is False


class TestRecursiveTrace:
    def test_all_cases_correct(self, grader):
        q = {
            'type': 'recursive_trace',
            'test_cases': [
                {'input': 'fact(3)', 'correct_answer': '6'},
                {'input': 'fact(4)', 'correct_answer': '24'},
            ],
        }
        answer = json.dumps({'test_0': '6', 'test_1': '24'})
        assert grader.grade(q, answer)['correct'] is True

    def test_one_case_wrong(self, grader):
        q = {
            'type': 'recursive_trace',
            'test_cases': [
                {'input': 'fact(3)', 'correct_answer': '6'},
                {'input': 'fact(4)', 'correct_answer': '24'},
            ],
        }
        answer = json.dumps({'test_0': '6', 'test_1': '0'})
        assert grader.grade(q, answer)['correct'] is False


class TestCodeWritingWithStubbedCompiler:
    """Code-running graders use the compiler — replace it with a fake.

    Uses the ``code_writing`` type because the dispatch for ``code_completion``
    in GraderService.grade() is broken (it does not pass ``test_cases`` to
    ``grade_code_completion``). Tracked as a separate bug.
    """

    def test_passes_when_outputs_match(self, grader):
        grader.compiler = MagicMock()
        grader.compiler.compile_and_run.return_value = {
            'success': True, 'stdout': 'hello', 'error': None,
        }
        q = {
            'type': 'code_writing',
            'code_template': 'int main(){ /* YOUR CODE HERE */ }',
            'test_cases': [{'input': '', 'expected_output': 'hello'}],
        }
        result = grader.grade(q, 'puts("hello");')
        assert result['correct'] is True
        assert all(t['passed'] for t in result['test_results'])

    def test_fails_on_compile_error(self, grader):
        grader.compiler = MagicMock()
        grader.compiler.compile_and_run.return_value = {
            'success': False, 'error': 'gcc: error', 'stdout': '',
        }
        q = {
            'type': 'code_writing',
            'code_template': 'int main(){ /* YOUR CODE HERE */ }',
            'test_cases': [{'input': '', 'expected_output': 'hello'}],
        }
        result = grader.grade(q, 'broken;')
        assert result['correct'] is False
