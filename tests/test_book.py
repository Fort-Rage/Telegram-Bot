import pytest

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from db.models import Book, Category, City, BookCategory, AppUsers, Location
from db.queries.book_crud import BookObj
from db.queries.location_crud import LocationObj


@pytest.mark.asyncio
async def test_book_model(db_session, sample_books_categories):
    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    book_1, book_2 = books[0], books[1]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_1.id))
    categories = result.scalars().all()
    book_1_categories = [Category(cat).value for cat in categories]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_2.id))
    categories = result.scalars().all()
    book_2_categories = [Category(cat).value for cat in categories]

    assert book_1.title == "Python" and book_1.author == "Someone" and book_1.description == "Python description"
    assert book_1.owner_id == app_users[0].id and book_1.location_id == locations[0].id
    assert sorted(book_1_categories) == sorted(["Databases", "Algorithms"])

    assert book_2.title == "Java" and book_2.author == "Someone 2" and book_2.description == "Java description"
    assert book_2.owner_id == app_users[1].id and book_2.location_id == locations[1].id
    assert sorted(book_2_categories) == sorted(["Data Science", "Machine Learning"])


@pytest.mark.asyncio
async def test_book_create(db_session, sample_app_users, sample_locations):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    app_user_1_id, app_user_2_id = app_users[0].id, app_users[1].id
    location_1_id, location_2_id = locations[0].id, locations[1].id

    await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id,
        categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    book_3 = await BookObj().create(
        session=db_session, title="Java", author="Someone 2", description="Java description",
        owner_id=app_user_2_id, location_id=location_2_id,
        categories=[Category.DATA_SCIENCE, Category.MACHINE_LEARNING],
    )
    book_4 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=uuid7(), location_id=location_1_id,
        categories=[Category.DATABASES, Category.ALGORITHMS]
    )
    book_5 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=uuid7(),
        categories=[Category.DATABASES, Category.ALGORITHMS]
    )
    book_6 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id,
        categories=["not_existing_category"]
    )

    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    book_1, book_2 = books[0], books[1]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_1.id))
    categories = result.scalars().all()
    book_1_categories = [Category(cat).value for cat in categories]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_2.id))
    categories = result.scalars().all()
    book_2_categories = [Category(cat).value for cat in categories]

    assert book_1.title == "Python" and book_1.author == "Someone" and book_1.description == "Python description"
    assert book_1.owner_id == app_user_1_id and book_1.location_id == location_1_id
    assert sorted(book_1_categories) == sorted(["Databases", "Algorithms"])

    assert book_2.title == "Java" and book_2.author == "Someone 2" and book_2.description == "Java description"
    assert book_2.owner_id == app_user_2_id and book_2.location_id == location_2_id
    assert sorted(book_2_categories) == sorted(["Data Science", "Machine Learning"])

    assert book_3 is True
    assert book_4 is False and book_5 is False and book_6 is False


@pytest.mark.asyncio
async def test_book_create_invalid(db_session, sample_app_users, sample_locations, mocker):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    app_user_1_id = app_users[0].id
    location_1_id, location_2_id = locations[0].id, locations[1].id

    # Invalid data
    invalid_book_1 = await BookObj().create(
        session=db_session, title=None, author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_1 is False
    invalid_book_1 = await BookObj().create(
        session=db_session, title="", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_1 is False
    invalid_book_1 = await BookObj().create(
        session=db_session, title=12345, author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_1 is False

    invalid_book_2 = await BookObj().create(
        session=db_session, title="Python", author=None, description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_2 is False
    invalid_book_2 = await BookObj().create(
        session=db_session, title="Python", author="", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_2 is False
    invalid_book_2 = await BookObj().create(
        session=db_session, title="Python", author=12345, description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_2 is False

    invalid_book_3 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description=None,
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_3 is False
    invalid_book_3 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="",
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_3 is False
    invalid_book_3 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description=12345,
        owner_id=app_user_1_id, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_3 is False

    invalid_book_4 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=None, location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_4 is False
    invalid_book_4 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id="", location_id=location_1_id, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_4 is False

    invalid_book_5 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=None, categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_5 is False
    invalid_book_5 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id="", categories=[Category.DATABASES, Category.ALGORITHMS],
    )
    assert invalid_book_5 is False

    invalid_book_6 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories=None,
    )
    assert invalid_book_6 is False
    invalid_book_6 = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id, categories="",
    )
    assert invalid_book_6 is False

    mocker.patch.object(db_session, 'add', side_effect=SQLAlchemyError("DB error"))
    db_error_book = await BookObj().create(
        session=db_session, title="Python", author="Someone", description="Python description",
        owner_id=app_user_1_id, location_id=location_1_id,
        categories=[Category.DATABASES, Category.ALGORITHMS]
    )
    assert db_error_book is False


@pytest.mark.asyncio
async def test_book_read(db_session, sample_books, mocker):
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    books_1 = await BookObj().read(db_session)
    # TODO: add check for non-abailable books after finishing order tests
    # books_2 = await BookObj().read(db_session, available_books=False)
    book_1, book_2 = books_1[0], books_1[1]

    assert len(books_1) == 2
    # assert len(books_2) == 0
    assert book_1.title == "Python" and book_1.author == "Someone" and book_1.description == "Python description"
    assert book_1.owner_id == app_users[0].id and book_1.location_id == locations[0].id

    assert book_2.title == "Java" and book_2.author == "Someone 2" and book_2.description == "Java description"
    assert book_2.owner_id == app_users[1].id and book_2.location_id == locations[1].id

    # Invalid data
    invalid_books_1 = await BookObj().read(db_session, available_books=None)
    assert len(invalid_books_1) == 0

    invalid_books_2 = await BookObj().read(db_session, available_books="")
    assert len(invalid_books_2) == 0

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_books = await BookObj().read(db_session)
    assert len(db_error_books) == 0


@pytest.mark.asyncio
async def test_book_update(db_session, sample_books_categories, mocker):
    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()
    book_1_id, book_2_id = books[0].id, books[1].id
    app_user_1_id, app_user_2_id = app_users[0].id, app_users[1].id
    location_1_id, location_2_id = locations[0].id, locations[1].id

    await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates={"title": "Java", "author": "Someone 2", "description": "Java description",
                 "categories": "Data Science, Machine Learning",
                 "owner_id": app_user_2_id, "location_id": location_2_id}
    )
    book_3 = await BookObj().update(
        session=db_session, book_id=book_2_id,
        updates={"title": "Python", "author": "Someone", "description": "Python description",
                 "categories": "Databases, Algorithms",
                 "owner_id": app_user_1_id, "location_id": location_1_id}
    )
    book_4 = await BookObj().update(
        session=db_session, book_id=uuid7(),
        updates={"title": "Python", "author": "Someone", "description": "Python description",
                 "categories": "Databases, Algorithms",
                 "owner_id": app_user_1_id, "location_id": location_1_id}
    )
    book_5 = await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates={"title": "Python", "author": "Someone", "description": "Python description",
                 "categories": "Databases, Algorithms",
                 "owner_id": uuid7(), "location_id": location_1_id}
    )
    book_6 = await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates={"title": "Python", "author": "Someone", "description": "Python description",
                 "categories": "Databases, Algorithms",
                 "owner_id": app_user_1_id, "location_id": uuid7()}
    )
    book_7 = await BookObj().update(session=db_session, book_id=book_1_id, updates={})

    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    book_1, book_2 = books[0], books[1]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_1.id))
    categories = result.scalars().all()
    book_1_categories = [Category(cat).value for cat in categories]

    result = await db_session.execute(select(BookCategory.category).where(BookCategory.book_id == book_2.id))
    categories = result.scalars().all()
    book_2_categories = [Category(cat).value for cat in categories]

    assert len(books) == 2
    assert book_3 is True
    assert book_4 is False and book_5 is False and book_6 is False and book_7 is False

    assert book_1.title == "Java" and book_1.author == "Someone 2" and book_1.description == "Java description"
    assert book_1.owner_id == app_user_2_id and book_1.location_id == location_2_id
    assert sorted(book_1_categories) == sorted(["Data Science", "Machine Learning"])

    assert book_2.title == "Python" and book_2.author == "Someone" and book_2.description == "Python description"
    assert book_2.owner_id == app_user_1_id and book_2.location_id == location_1_id
    assert sorted(book_2_categories) == sorted(["Databases", "Algorithms"])

    # Invalid data
    invalid_book_1 = await BookObj().update(
        session=db_session, book_id=None,
        updates={"title": "Java", "author": "Someone 2", "description": "Java description",
                 "categories": "Data Science, Machine Learning",
                 "owner_id": app_user_2_id, "location_id": location_2_id}
    )
    assert invalid_book_1 is False
    invalid_book_1 = await BookObj().update(
        session=db_session, book_id="",
        updates={"title": "Java", "author": "Someone 2", "description": "Java description",
                 "categories": "Data Science, Machine Learning",
                 "owner_id": app_user_2_id, "location_id": location_2_id}
    )
    assert invalid_book_1 is False

    invalid_book_2 = await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates=None
    )
    assert invalid_book_2 is False
    invalid_book_2 = await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates=""
    )
    assert invalid_book_2 is False

    mocker.patch.object(db_session, 'commit', side_effect=SQLAlchemyError("DB error"))
    db_error_book = await BookObj().update(
        session=db_session, book_id=book_1_id,
        updates={"title": 'Java', "author": "Someone 2", "description": "Java description",
                 "categories": "Data Science, Machine Learning",
                 "owner_id": app_user_2_id, 'location_id': location_2_id}
    )
    assert db_error_book is False


@pytest.mark.asyncio
async def test_book_delete(db_session, sample_books, mocker):
    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    book_1_id, book_2_id = books[0].id, books[1].id

    await BookObj().remove(session=db_session, book_id=book_1_id)
    book_2 = await BookObj().remove(session=db_session, book_id=uuid7())

    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()

    assert len(books) == 1
    assert book_2 is False

    # Invalid data
    invalid_book_1 = await BookObj().remove(session=db_session, book_id=None)
    assert invalid_book_1 is False

    invalid_book_2 = await BookObj().remove(session=db_session, book_id="")
    assert invalid_book_2 is False

    mocker.patch.object(db_session, 'execute', side_effect=SQLAlchemyError("DB error"))
    db_error_book = await BookObj().remove(session=db_session, book_id=book_2_id)
    assert db_error_book is False


@pytest.mark.asyncio
async def test_book_get_object(db_session, sample_books, mocker):
    result = await db_session.execute(select(Book).order_by(Book.id))
    books = result.scalars().all()
    result = await db_session.execute(select(AppUsers).order_by(AppUsers.id))
    app_users = result.scalars().all()
    result = await db_session.execute(select(Location).order_by(Location.id))
    locations = result.scalars().all()

    book_1 = await BookObj().get_obj(session=db_session, book_id=books[0].id)
    book_2 = await BookObj().get_obj(session=db_session, book_id=books[1].id)
    book_3 = await BookObj().get_obj(session=db_session, book_id=uuid7())

    assert book_1.title == "Python" and book_1.author == "Someone" and book_1.description == "Python description"
    assert book_1.owner_id == app_users[0].id and book_1.location_id == locations[0].id

    assert book_2.title == "Java" and book_2.author == "Someone 2" and book_2.description == "Java description"
    assert book_2.owner_id == app_users[1].id and book_2.location_id == locations[1].id

    assert book_3 is None

    # Invalid data
    invalid_book_1 = await BookObj().get_obj(session=db_session, book_id=None)
    assert invalid_book_1 is None

    invalid_book_2 = await BookObj().get_obj(session=db_session, book_id="")
    assert invalid_book_2 is None

    mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
    db_error_book = await BookObj().get_obj(session=db_session, book_id=books[0].id)
    assert db_error_book is None


# TODO: Finish after main CRUD functions tests
# @pytest.mark.asyncio
# async def test_book_get_book_categories(
#         db_session,
#         sample_users, sample_locations, sample_books, sample_books_categories):
#     book_categories = await BookObj.get_book_categories(book_id=1, session=db_session)
#     assert len(book_categories) == 2
#     assert book_categories[0] == Category.DEVOPS
#     assert book_categories[1] == Category.ALGORITHMS
#
#
# @pytest.mark.asyncio
# async def test_get_categories():
#     categories = await BookObj().get_categories()
#     assert len(categories) == 10
#     assert categories[0] == Category.PROGRAMMING
#     assert categories[-1] == Category.ALGORITHMS
#
#
# @pytest.mark.asyncio
# async def test_get_book_location(db_session, mocker):
#     await LocationObj().create(city=City.New_York, room='33', session=db_session)
#     await LocationObj().create(city=City.Tashkent, room='44', session=db_session)
#
#     book_location_1 = await BookObj().get_book_location(loc_id=1, session=db_session)
#     book_location_2 = await BookObj().get_book_location(loc_id=2, session=db_session)
#     book_location_3 = await BookObj().get_book_location(loc_id=22323, session=db_session)
#
#     assert book_location_1.city == City.New_York
#     assert book_location_2.room == '44'
#     assert book_location_3 is None
#
#     mocker.patch.object(db_session, 'get', side_effect=SQLAlchemyError("DB error"))
#     error_book_location = await BookObj().get_book_location(loc_id=3, session=db_session)
#
#     assert error_book_location is None
