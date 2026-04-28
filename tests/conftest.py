"""Shared pytest fixtures.

The app boots in DEBUG with an in-memory SQLite database so tests are
fully isolated from the developer's instance/practice.db.
"""

from __future__ import annotations

import os

# Force a safe, debug-mode environment before importing the app module.
# These env vars are read by config.Config at import time.
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('FORCE_HTTPS', 'false')

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from models import db as _db  # noqa: E402


@pytest.fixture(scope='session')
def app():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    )
    with flask_app.app_context():
        _db.drop_all()
        _db.create_all()
        yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    """Per-test transactional cleanup."""
    yield _db
    _db.session.rollback()
    # Truncate non-schema tables between tests
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()
