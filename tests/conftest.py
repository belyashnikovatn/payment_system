import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import SessionLocal


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
async def session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
