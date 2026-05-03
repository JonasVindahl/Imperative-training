"""Tests for ExamService — the active-exam selection layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from flask import Flask

from services.exam_service import ExamService


@pytest.fixture()
def exams_file(tmp_path: Path) -> str:
    f = tmp_path / 'exams.json'
    f.write_text(json.dumps({
        'default_exam': 'c_programming',
        'exams': [
            {'id': 'c_programming', 'name': 'C', 'icon': 'C', 'categories': [
                {'id': 'arrays', 'name': 'Arrays'},
                {'id': 'pointers', 'name': 'Pointers'},
            ]},
            {'id': 'ds', 'name': 'Diskrete Strukturer', 'icon': 'D', 'categories': [
                {'id': 'k1', 'name': 'K1 Logic'},
            ]},
        ],
    }))
    return str(f)


@pytest.fixture()
def app_ctx():
    """ExamService.set_active_exam touches flask.session, which needs a request context."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'x'
    with app.test_request_context('/'):
        yield app


def test_get_default_exam_id(exams_file, app_ctx):
    svc = ExamService(exams_file)
    assert svc.get_default_exam_id() == 'c_programming'


def test_get_all_exams(exams_file, app_ctx):
    svc = ExamService(exams_file)
    ids = [e['id'] for e in svc.get_all_exams()]
    assert ids == ['c_programming', 'ds']


def test_set_active_exam_valid(exams_file, app_ctx):
    svc = ExamService(exams_file)
    assert svc.set_active_exam('ds') is True
    assert svc.get_active_exam_id() == 'ds'


def test_set_active_exam_invalid_id_rejected(exams_file, app_ctx):
    svc = ExamService(exams_file)
    assert svc.set_active_exam('does_not_exist') is False


def test_get_active_exam_falls_back_to_default(exams_file, app_ctx):
    svc = ExamService(exams_file)
    # No session value yet -> default
    assert svc.get_active_exam()['id'] == 'c_programming'


def test_get_categories_for_unknown_exam(exams_file, app_ctx):
    svc = ExamService(exams_file)
    assert svc.get_categories_for_exam('nope') == []


def test_get_category_name_falls_back_to_titlecase(exams_file, app_ctx):
    svc = ExamService(exams_file)
    assert svc.get_category_name('c_programming', 'unknown_cat') == 'Unknown Cat'


# -----------------------------------------------------------------------------
# CCT (course-level grouping above exams)
# -----------------------------------------------------------------------------

@pytest.fixture()
def cct_exams_file(tmp_path: Path) -> str:
    """An exams.json with a `ccts` block and a `cct` link from each exam.
    Mirrors the production layout: CCT1 has one exam, CCT2 has three, CCT3..6
    are declared but empty (placeholders for future content)."""
    f = tmp_path / 'exams.json'
    f.write_text(json.dumps({
        'default_exam': 'c_programming',
        'ccts': [
            {'id': 'cct1', 'name': 'CCT 1', 'tagline': 'Imperativ programmering'},
            {'id': 'cct2', 'name': 'CCT 2', 'tagline': 'Datalogiske grundbegreber'},
            {'id': 'cct3', 'name': 'CCT 3', 'tagline': 'Coming soon'},
        ],
        'exams': [
            {'id': 'c_programming', 'cct': 'cct1', 'name': 'C', 'icon': 'C', 'categories': []},
            {'id': 'ds',            'cct': 'cct2', 'name': 'D', 'icon': 'D', 'categories': []},
            {'id': 'oop',           'cct': 'cct2', 'name': 'O', 'icon': 'O', 'categories': []},
            {'id': 'agil',          'cct': 'cct2', 'name': 'A', 'icon': 'A', 'categories': []},
            {'id': 'unassigned',                   'name': 'U', 'icon': 'U', 'categories': []},
        ],
    }))
    return str(f)


class TestCcts:
    def test_get_all_ccts_preserves_order(self, cct_exams_file, app_ctx):
        svc = ExamService(cct_exams_file)
        assert [c['id'] for c in svc.get_all_ccts()] == ['cct1', 'cct2', 'cct3']

    def test_get_cct_for_exam(self, cct_exams_file, app_ctx):
        svc = ExamService(cct_exams_file)
        assert svc.get_cct_for_exam('c_programming')['id'] == 'cct1'
        assert svc.get_cct_for_exam('ds')['id'] == 'cct2'

    def test_get_cct_for_exam_with_no_cct_field(self, cct_exams_file, app_ctx):
        svc = ExamService(cct_exams_file)
        assert svc.get_cct_for_exam('unassigned') is None

    def test_get_cct_for_unknown_exam(self, cct_exams_file, app_ctx):
        svc = ExamService(cct_exams_file)
        assert svc.get_cct_for_exam('nope') is None

    def test_group_exams_by_cct(self, cct_exams_file, app_ctx):
        svc = ExamService(cct_exams_file)
        groups = svc.group_exams_by_cct()
        # CCT1 + CCT2 + CCT3 + Other = 4 groups
        assert [g['id'] for g in groups] == ['cct1', 'cct2', 'cct3', None]
        cct1 = next(g for g in groups if g['id'] == 'cct1')
        cct2 = next(g for g in groups if g['id'] == 'cct2')
        cct3 = next(g for g in groups if g['id'] == 'cct3')
        other = next(g for g in groups if g['id'] is None)
        assert [e['id'] for e in cct1['exams']] == ['c_programming']
        assert [e['id'] for e in cct2['exams']] == ['ds', 'oop', 'agil']
        # Empty CCTs are still listed (placeholder for future content)
        assert cct3['exams'] == []
        # Exams without a `cct` field land in the Other bucket
        assert [e['id'] for e in other['exams']] == ['unassigned']

    def test_group_exams_by_cct_drops_other_when_empty(self, exams_file, app_ctx):
        # The legacy fixture (no `ccts` block, no `cct` field on exams) should
        # not raise — it just yields a single Other bucket with everything.
        svc = ExamService(exams_file)
        groups = svc.group_exams_by_cct()
        # No declared CCTs → only the Other bucket if there are exams.
        assert len(groups) == 1
        assert groups[0]['id'] is None
        assert [e['id'] for e in groups[0]['exams']] == ['c_programming', 'ds']
