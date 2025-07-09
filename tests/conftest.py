import os
import pytest_asyncio

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db.models import Base, Location, City, Category, Book, User, BookCategory, WishList, Order, OrderStatus

load_dotenv()

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('TEST_POSTGRES_USER')}:{os.getenv('TEST_POSTGRES_PASSWORD')}"
    f"@{os.getenv('TEST_POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('TEST_POSTGRES_DB')}"
    )


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def clear_all_tables(db_engine):
    async with db_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))


@pytest_asyncio.fixture
async def db_session(db_engine, clear_all_tables):
    async with AsyncSession(db_engine) as session:
        yield session


@pytest_asyncio.fixture
async def sample_users(db_session):
    users = [
        User(telegram_id=12345, name="A", surname='B'),
        User(telegram_id=54321, name="C", surname='D'),
        User(telegram_id=77777, name="Admin", surname='Vention', is_admin=True),
    ]
    db_session.add_all(users)
    await db_session.commit()
    return users


@pytest_asyncio.fixture
async def sample_locations(db_session):
    locations = [
        Location(city=City.Almaty, room="Room 22"),
        Location(city=City.Berlin, room="Room 33")
    ]
    db_session.add_all(locations)
    await db_session.commit()
    return locations


@pytest_asyncio.fixture
async def sample_books(db_session):
    books = [
        Book(title='Python', author='Someone', description='Python description', owner_id=12345, location_id=1),
        Book(title='Java', author='Someone', description='Java description', owner_id=54321, location_id=2)
    ]
    db_session.add_all(books)
    await db_session.commit()
    return books


@pytest_asyncio.fixture
async def sample_books_categories(db_session):
    categories = [
        BookCategory(
            book_id=1,
            category=Category.DEVOPS
        ),
        BookCategory(
            book_id=1,
            category=Category.ALGORITHMS
        ),
        BookCategory(
            book_id=2,
            category=Category.DATABASES
        ),
        BookCategory(
            book_id=2,
            category=Category.DATA_SCIENCE
        )
    ]

    db_session.add_all(categories)
    await db_session.commit()
    return categories


@pytest_asyncio.fixture
async def sample_wishlists(db_session):
    wish_lists = [
        WishList(user_id=12345, book_title="Title", author="Author", comment="Good!"),
        WishList(user_id=54321, book_title="No Title", author="No Author", comment="Bad!")
    ]
    db_session.add_all(wish_lists)
    await db_session.commit()
    return wish_lists


@pytest_asyncio.fixture
async def sample_orders(db_session):
    orders = [
        Order(telegram_id=12345, book_id=1, status=OrderStatus.RESERVED, taken_from_id=1),
        Order(telegram_id=54321, book_id=2, status=OrderStatus.RETURNED, taken_from_id=2, returned_to_id=2),
        Order(telegram_id=12345, book_id=1, status=OrderStatus.IN_PROCESS, taken_from_id=2),
    ]

    db_session.add_all(orders)
    await db_session.commit()
    return orders
