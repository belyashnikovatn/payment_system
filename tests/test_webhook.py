import pytest
from app.security import generate_signature
from app.config import settings


def test_webhook_payment(client):
    sig = generate_signature(
        account_id=1,
        amount=50.0,
        transaction_id="00000000-0000-0000-0000-000000000050",
        user_id=1,
        secret_key=settings.SECRET_KEY,
    )
    data = {
        "account_id": 1,
        "amount": 50.0,
        "transaction_id": "00000000-0000-0000-0000-000000000050",
        "user_id": 1,
        "signature": sig,
    }

    response = client.post("/webhook/payment", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
