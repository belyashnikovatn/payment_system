import pytest

def get_admin_token(client):
    res = client.post('/token', data={'username': 'admin@example.com', 'password': 'adminpass'})
    return res.json()['access_token']

def test_admin_get_users(client):
    token = get_admin_token(client)
    res = client.get('/admin/users', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert isinstance(res.json(), list)