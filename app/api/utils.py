from fastapi import APIRouter
from uuid import uuid4
from app.config import settings
from app.security import generate_signature

router = APIRouter()


@router.get("/generate-uuid")
async def generate_uuid():
    """Генерация корректного UUID v4"""
    return {"uuid": str(uuid4())}


@router.post("/signature-check")
async def debug_signature(data: dict):
    return {
        "generated": generate_signature(
            account_id=data["account_id"],
            amount=data["amount"],
            transaction_id=data["transaction_id"],
            user_id=data["user_id"],
            secret_key=settings.SECRET_KEY,
        ),
        "input_data": data,
    }
