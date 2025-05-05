import pytest


def get_token(client):
    res = client.post(
        "/token",
        data={"username": "testuser@example.com", "password": "userpass"},
    )
    return res.json()["access_token"]


def test_get_me(client):
    token = get_token(client)
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
