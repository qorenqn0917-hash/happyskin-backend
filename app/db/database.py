from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.skin import Base

# User 모델을 Base.metadata에 등록하기 위해 import
import app.models.user  # noqa: F401

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 기존 DB에 user_id 컬럼이 없으면 추가 (무중단 마이그레이션)
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(skin_analyses)"))
        columns = [row[1] for row in result.fetchall()]
        if "user_id" not in columns:
            await conn.execute(
                text("ALTER TABLE skin_analyses ADD COLUMN user_id TEXT")
            )
            await conn.commit()


async def get_session() -> AsyncSession:  # used as a FastAPI dependency when needed
    async with AsyncSessionLocal() as session:
        yield session
