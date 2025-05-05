import uuid
import pytest
from app.security import generate_signature
from app.config import settings


def test_webhook_payment(client):
    transaction_id = str(uuid.uuid4())
    sig = generate_signature(
        account_id=1,
        amount=50.0,
        transaction_id=transaction_id,
        user_id=1,
        secret_key=settings.SECRET_KEY,
    )
    data = {
        "account_id": 1,
        "amount": 50.0,
        "transaction_id": transaction_id,
        "user_id": 1,
        "signature": sig,
    }

    response = client.post("/webhook/payment", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
