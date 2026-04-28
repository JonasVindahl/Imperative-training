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
