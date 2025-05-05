import hashlib
import hmac


def generate_signature(
    account_id: int,
    amount: float,
    transaction_id: str,
    user_id: int,
    secret_key: str,
) -> str:
    """
    Generate HMAC-SHA256 signature for webhook data.

    Args:
        account_id: Account ID
        amount: Transaction amount (will be normalized to 2 decimal places)
        transaction_id: Unique transaction identifier
        user_id: User ID
        secret_key: Secret key for signing

    Returns:
        Hex-encoded signature string
    """
    # Normalize amount to prevent float precision issues
    normalized_amount = f"{float(amount):.2f}"

    # Create consistent string representation
    data_string = (
        f"{account_id}:{normalized_amount}:{transaction_id}:{user_id}"
    )

    signature = hmac.new(
        secret_key.encode("utf-8"), data_string.encode("utf-8"), hashlib.sha256
    )

    return signature.hexdigest()


def verify_signature(
    received_signature: str,
    account_id: int,
    amount: float,
    transaction_id: str,
    user_id: int,
    secret_key: str,
) -> bool:
    """
    Verify HMAC signature in constant time to prevent timing attacks.

    Args:
        received_signature: Signature to verify
        account_id: Account ID
        amount: Transaction amount
        transaction_id: Unique transaction identifier
        user_id: User ID
        secret_key: Secret key for verification

    Returns:
        bool: True if signature is valid, False otherwise
    """
    expected_signature = generate_signature(
        account_id=account_id,
        amount=amount,
        transaction_id=transaction_id,
        user_id=user_id,
        secret_key=secret_key,
    )

    return hmac.compare_digest(received_signature, expected_signature)
