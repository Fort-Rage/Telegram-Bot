import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    f"?async_fallback=True"
)

async_engine = create_async_engine(url=DATABASE_URL)

async_session_factory = async_sessionmaker(async_engine)

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('TEST_POSTGRES_USER')}:{os.getenv('TEST_POSTGRES_PASSWORD')}"
    f"@{os.getenv('TEST_POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('TEST_POSTGRES_DB')}"
    f"?async_fallback=True"
)

test_async_engine = create_async_engine(url=TEST_DATABASE_URL)
test_async_session_factory = async_sessionmaker(test_async_engine, expire_on_commit=False)
