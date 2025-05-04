import pytest

def test_login_success(client):
    response = client.post('/token', data={'username': 'testuser@example.com', 'password': 'userpass'})
    assert response.status_code == 200
    assert 'access_token' in response.json()

def test_login_fail(client):
    response = client.post('/token', data={'username': 'testuser@example.com', 'password': 'wrong'})
    assert response.status_code == 401
