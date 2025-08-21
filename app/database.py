from time import time

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel

from app.config import DEBUG_FEATURES

engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:?cache=shared",
    echo=DEBUG_FEATURES,
    future=True,
    connect_args={"check_same_thread": False},
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


class Channel(SQLModel, table=True):
    id: int = Field(primary_key=True)
    creator_id: int = Field(nullable=False, unique=True)


class Ban(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    staff_id: int = Field(nullable=False)
    reason: str = Field(nullable=False)
    timestamp: int = Field(default_factory=lambda: int(time()))
