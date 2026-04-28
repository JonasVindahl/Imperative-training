"""Smoke test: app boots, health endpoints respond, login flow works."""

from __future__ import annotations


def test_healthz(client):
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.get_json() == {'status': 'ok'}


def test_readyz(client):
    resp = client.get('/readyz')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ready'


def test_index_redirects_when_logged_out(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_login_required_redirects_to_login(client):
    resp = client.get('/practice/start', follow_redirects=False)
    assert resp.status_code in (302, 401)


def test_register_then_login(client, db):
    # Register
    resp = client.post('/auth/register', data={
        'name': 'Tester',
        'email': 'tester@example.com',
        'password': 'hunter22',
        'confirm_password': 'hunter22',
    }, follow_redirects=False)
    assert resp.status_code in (302, 200)

    # Login
    resp = client.post('/auth/login', data={
        'email': 'tester@example.com',
        'password': 'hunter22',
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert '/progress/dashboard' in resp.headers['Location']


def test_security_headers_present(client):
    resp = client.get('/healthz')
    assert resp.headers.get('X-Frame-Options') == 'DENY'
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'Content-Security-Policy' in resp.headers
