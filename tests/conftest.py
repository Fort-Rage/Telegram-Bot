import os
import pytest_asyncio

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db.models import Base, Location, City, Category, Book, BookCategory, WishList, Order, OrderStatus, AppUsers, \
    TelegramUsers, Employees, Roles

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
async def sample_tg_users(db_session):
    tg_users = [
        TelegramUsers(telegram_id="12345", username="user_a"),
        TelegramUsers(telegram_id="54321", username="admin_user"),
    ]
    db_session.add_all(tg_users)
    await db_session.commit()
    return tg_users


@pytest_asyncio.fixture
async def sample_employees(db_session):
    employees = [
        Employees(full_name="User A", email="user_a@example.com"),
        Employees(full_name="Admin", email="admin@example.com", is_verified=True),
    ]
    db_session.add_all(employees)
    await db_session.commit()
    return employees


@pytest_asyncio.fixture
async def sample_roles(db_session):
    roles = [
        Roles(name="User", description="Default user role"),
        Roles(name="Admin", description="Administrator role"),
    ]
    db_session.add_all(roles)
    await db_session.commit()
    return roles


@pytest_asyncio.fixture
async def sample_app_users(db_session, sample_tg_users, sample_employees, sample_roles):
    result = await db_session.execute(select(TelegramUsers).order_by(TelegramUsers.id))
    tg_users = result.scalars().all()
    result = await db_session.execute(select(Employees).order_by(Employees.id))
    employees = result.scalars().all()
    result = await db_session.execute(select(Roles).order_by(Roles.id))
    roles = result.scalars().all()

    app_users = [
        AppUsers(tg_user_id=tg_users[0].id,
                 employee_id=employees[0].id,
                 role_id=roles[0].id,
                 is_active=False),
        AppUsers(tg_user_id=tg_users[1].id,
                 employee_id=employees[1].id,
                 role_id=roles[1].id),
    ]
    db_session.add_all(app_users)
    await db_session.commit()
    return app_users


@pytest_asyncio.fixture
async def sample_wishlists(db_session, sample_app_users):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()

    wish_lists = [
        WishList(app_user_id=app_users[0].id, book_title="Title", author="Author", comment="Good!"),
        WishList(app_user_id=app_users[0].id, book_title="No Title", author="No Author")
    ]
    db_session.add_all(wish_lists)
    await db_session.commit()
    return wish_lists


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
async def sample_books(db_session, sample_app_users, sample_locations):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    books = [
        Book(
            title="Python", author="Someone", description="Python description",
            owner_id=app_users[0].id, location_id=locations[0].id,
        ),
        Book(
            title="Java", author="Someone 2", description="Java description",
            owner_id=app_users[1].id, location_id=locations[1].id,
        )
    ]
    db_session.add_all(books)
    await db_session.commit()
    return books


@pytest_asyncio.fixture
async def sample_books_categories(db_session, sample_books):
    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()

    categories = [
        BookCategory(
            book_id=books[0].id,
            category=Category.DATABASES
        ),
        BookCategory(
            book_id=books[0].id,
            category=Category.ALGORITHMS
        ),
        BookCategory(
            book_id=books[1].id,
            category=Category.DATA_SCIENCE
        ),
        BookCategory(
            book_id=books[1].id,
            category=Category.MACHINE_LEARNING
        )
    ]
    db_session.add_all(categories)
    await db_session.commit()
    return categories

# TODO: Finish After Book Test
# @pytest_asyncio.fixture
# async def sample_orders(db_session, sample_app_users, sample_books, sample_locations):
#     orders = [
#         Order(app_user_id=(await sample_app_users)[0].id, book_id=(await sample_books)[0].id,
#               status=OrderStatus.RESERVED, taken_from_id=(await sample_locations)[0].id),
#         Order(app_user_id=(await sample_app_users)[0].id, book_id=(await sample_books)[0].id,
#               status=OrderStatus.RETURNED,
#               taken_from_id=(await sample_locations)[0].id, returned_to_id=(await sample_locations)[1].id),
#         Order(app_user_id=(await sample_app_users)[1].id, book_id=(await sample_books)[1].id,
#               status=OrderStatus.IN_PROCESS, taken_from_id=(await sample_locations)[1].id),
#         Order(app_user_id=(await sample_app_users)[1].id, book_id=(await sample_books)[1].id,
#               status=OrderStatus.CANCELLED, taken_from_id=(await sample_locations)[0].id)
#     ]
#
#     db_session.add_all(orders)
#     await db_session.commit()
#     return orders