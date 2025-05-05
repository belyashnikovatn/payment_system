import hashlib


def generate_signature(
    account_id: int,
    amount: float,
    transaction_id: str,
    user_id: int,
    secret_key: str,
) -> str:
    normalized_amount = f"{amount:.2f}"  # обязательно нормализуем
    data_string = f"{account_id}:{normalized_amount}:{transaction_id}:{user_id}:{secret_key}"
    return hashlib.sha256(data_string.encode()).hexdigest()
