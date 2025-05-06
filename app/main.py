from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.api import router as api_router
import logging
import platform
import asyncio
import uvicorn
from alembic.config import Config
from alembic import command
from pathlib import Path

logger = logging.getLogger(__name__)

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting application...")
    yield
    # Shutdown logic
    logger.info("Shutting down application...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your app!"}


def run_alembic_migrations():
    # Путь до alembic.ini
    alembic_cfg = Config(
        str(Path(__file__).resolve().parent.parent / "alembic.ini")
    )
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_alembic_migrations()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
