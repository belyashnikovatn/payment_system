import pytest

def test_generate_uuid(client):
    res = client.get('/utils/generate-uuid')
    assert res.status_code == 200
    assert 'uuid' in res.json()

def test_signature_check(client):
    data = {
        'account_id': 1,
        'amount': 99.9,
        'transaction_id': '00000000-0000-0000-0000-000000000099',
        'user_id': 2
    }
    res = client.post('/utils/signature-check', json=data)
    assert res.status_code == 200
    assert 'generated' in res.json()